import json
from collections import Counter
from sqlalchemy.orm import Session
from app.models import QuestionHistory


def build_learning_report(db: Session, student_id: int):
    rows = (
        db.query(QuestionHistory)
        .filter(QuestionHistory.student_id == student_id)
        .order_by(QuestionHistory.id.desc())
        .all()
    )

    total_count = len(rows)
    wrong_count = sum(1 for row in rows if row.is_wrong)
    correct_count = total_count - wrong_count
    wrong_rate = round((wrong_count / total_count * 100), 2) if total_count > 0 else 0.0

    kp_counter = Counter()
    for row in rows:
        try:
            knowledge_points = json.loads(row.knowledge_points or "[]")
        except Exception:
            knowledge_points = []

        for kp in knowledge_points:
            if kp:
                kp_counter[kp] += 1

    top_knowledge_points = [
        {"name": name, "count": count}
        for name, count in kp_counter.most_common(5)
    ]

    recent_records = []
    for row in rows[:7]:
        try:
            knowledge_points = json.loads(row.knowledge_points or "[]")
        except Exception:
            knowledge_points = []

        recent_records.append({
            "id": row.id,
            "question": row.question,
            "is_wrong": row.is_wrong,
            "knowledge_points": knowledge_points,
        })

    return {
        "total_count": total_count,
        "wrong_count": wrong_count,
        "correct_count": correct_count,
        "wrong_rate": wrong_rate,
        "top_knowledge_points": top_knowledge_points,
        "recent_records": recent_records,
    }