import json
import os
from typing import List, Dict

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "math_knowledge.json")


def load_knowledge_base() -> List[Dict]:
    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def score_item(question: str, item: Dict) -> int:
    score = 0
    text = f"{item.get('title', '')} {' '.join(item.get('keywords', []))} {item.get('content', '')}"

    for kw in item.get("keywords", []):
        if kw and kw in question:
            score += 5

    for ch in set(question):
        if ch.strip() and ch in text:
            score += 1

    return score


def retrieve_knowledge(question: str, top_k: int = 3) -> List[Dict]:
    kb = load_knowledge_base()
    scored = []

    for item in kb:
        score = score_item(question, item)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:top_k]]


def build_context(question: str) -> str:
    items = retrieve_knowledge(question, top_k=3)
    if not items:
        return ""

    parts = []
    for idx, item in enumerate(items, start=1):
        parts.append(
            f"知识片段{idx}：\n"
            f"标题：{item['title']}\n"
            f"内容：{item['content']}\n"
        )
    return "\n".join(parts)


def get_knowledge_titles(question: str) -> List[str]:
    items = retrieve_knowledge(question, top_k=3)
    return [item["title"] for item in items]