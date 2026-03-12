import json
from collections import defaultdict
from sqlalchemy.orm import Session
from app.models import QuestionHistory


def build_study_suggestion(db: Session, student_id: int):
    rows = db.query(QuestionHistory).filter(QuestionHistory.student_id == student_id).all()

    stat_map = defaultdict(lambda: {"total": 0, "wrong": 0})

    for row in rows:
        try:
            knowledge_points = json.loads(row.knowledge_points or "[]")
        except Exception:
            knowledge_points = []

        for kp in knowledge_points:
            if not kp:
                continue
            stat_map[kp]["total"] += 1
            if row.is_wrong:
                stat_map[kp]["wrong"] += 1

    weak_list = []
    for name, stat in stat_map.items():
        total = stat["total"]
        wrong = stat["wrong"]
        wrong_rate = round((wrong / total * 100), 2) if total > 0 else 0.0

        if wrong > 0:
            if wrong_rate >= 60:
                suggestion = f"建议优先强化“{name}”基础概念，并连续练习 3~5 道同类题。"
            elif wrong_rate >= 30:
                suggestion = f"建议针对“{name}”做专项复习，并配合 2~3 道练习题巩固。"
            else:
                suggestion = f"“{name}”有少量错误，建议复盘错题并适量练习。"

            weak_list.append({
                "name": name,
                "wrong_count": wrong,
                "total_count": total,
                "wrong_rate": wrong_rate,
                "suggestion": suggestion,
            })

    weak_list.sort(key=lambda x: (x["wrong_rate"], x["wrong_count"]), reverse=True)
    weak_list = weak_list[:5]

    if not weak_list:
        overall_suggestion = "当前暂无明显薄弱知识点，建议继续保持练习，并适度拓展更高难度题目。"
    else:
        top_name = weak_list[0]["name"]
        overall_suggestion = f"当前最需要优先突破的知识点是“{top_name}”，建议先复习核心方法，再进行针对性训练。"

    return {
        "weak_knowledge_points": weak_list,
        "overall_suggestion": overall_suggestion,
    }