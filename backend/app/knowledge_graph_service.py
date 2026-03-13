import json
from sqlalchemy.orm import Session
from app.models import StudentKnowledgeStat, QuestionHistory


def _normalize_knowledge_points(knowledge_points: list[str]) -> list[str]:
    result = []
    seen = set()

    for item in knowledge_points:
        name = (item or "").strip()
        if not name or name in seen:
            continue
        seen.add(name)
        result.append(name)

    return result


def update_student_knowledge_stat(
    db: Session,
    student_id: int,
    knowledge_points: list[str],
    is_wrong: bool,
):
    kp_list = _normalize_knowledge_points(knowledge_points)

    for kp in kp_list:
        row = (
            db.query(StudentKnowledgeStat)
            .filter(
                StudentKnowledgeStat.student_id == student_id,
                StudentKnowledgeStat.knowledge_name == kp,
            )
            .first()
        )

        if not row:
            row = StudentKnowledgeStat(
                student_id=student_id,
                knowledge_name=kp,
                total_count=0,
                wrong_count=0,
                correct_count=0,
            )
            db.add(row)
            db.flush()

        row.total_count += 1
        if is_wrong:
            row.wrong_count += 1
        else:
            row.correct_count += 1

    db.commit()


def rebuild_student_knowledge_stat(db: Session, student_id: int):
    db.query(StudentKnowledgeStat).filter(
        StudentKnowledgeStat.student_id == student_id
    ).delete()
    db.flush()

    rows = (
        db.query(QuestionHistory)
        .filter(QuestionHistory.student_id == student_id)
        .order_by(QuestionHistory.id.asc())
        .all()
    )

    stat_map: dict[str, dict[str, int]] = {}

    for row in rows:
        try:
            knowledge_points = json.loads(row.knowledge_points or "[]")
        except Exception:
            knowledge_points = []

        kp_list = _normalize_knowledge_points(knowledge_points)

        for kp in kp_list:
            if kp not in stat_map:
                stat_map[kp] = {
                    "total_count": 0,
                    "wrong_count": 0,
                    "correct_count": 0,
                }

            stat_map[kp]["total_count"] += 1
            if row.is_wrong:
                stat_map[kp]["wrong_count"] += 1
            else:
                stat_map[kp]["correct_count"] += 1

    for knowledge_name, stat in stat_map.items():
        db.add(
            StudentKnowledgeStat(
                student_id=student_id,
                knowledge_name=knowledge_name,
                total_count=stat["total_count"],
                wrong_count=stat["wrong_count"],
                correct_count=stat["correct_count"],
            )
        )

    db.commit()


def get_student_knowledge_graph(db: Session, student_id: int):
    rows = (
        db.query(StudentKnowledgeStat)
        .filter(StudentKnowledgeStat.student_id == student_id)
        .order_by(
            StudentKnowledgeStat.wrong_count.desc(),
            StudentKnowledgeStat.total_count.desc(),
            StudentKnowledgeStat.knowledge_name.asc(),
        )
        .all()
    )

    items = []
    for row in rows:
        wrong_rate = round((row.wrong_count / row.total_count * 100), 2) if row.total_count > 0 else 0.0
        items.append({
            "knowledge_name": row.knowledge_name,
            "total_count": row.total_count,
            "wrong_count": row.wrong_count,
            "correct_count": row.correct_count,
            "wrong_rate": wrong_rate,
        })

    return {
        "student_id": student_id,
        "items": items,
    }