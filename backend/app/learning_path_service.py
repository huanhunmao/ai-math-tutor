from sqlalchemy.orm import Session
from app.models import StudentKnowledgeStat

def generate_learning_path(db: Session, student_id: int):

    rows = (
        db.query(StudentKnowledgeStat)
        .filter(StudentKnowledgeStat.student_id == student_id)
        .all()
    )

    items = []

    for row in rows:

        if row.total_count == 0:
            continue

        wrong_rate = row.wrong_count / row.total_count

        items.append({
            "knowledge_name": row.knowledge_name,
            "total": row.total_count,
            "wrong": row.wrong_count,
            "wrong_rate": round(wrong_rate * 100, 2)
        })

    # 按错误率排序
    items.sort(key=lambda x: x["wrong_rate"], reverse=True)

    path = []

    for item in items:

        if item["wrong_rate"] > 50:
            suggestion = "重点训练（推荐10题）"

        elif item["wrong_rate"] > 20:
            suggestion = "强化练习（推荐5题）"

        else:
            suggestion = "保持复习"

        path.append({
            "knowledge_name": item["knowledge_name"],
            "wrong_rate": item["wrong_rate"],
            "suggestion": suggestion
        })

    return path