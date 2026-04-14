import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from app.rag_service import build_context, get_knowledge_titles

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
MODEL = os.getenv("OPENAI_MODEL", "moonshot-v1-8k")

_client = None

SYSTEM_PROMPT = """
你是一位专业的初中数学辅导老师。

请严格返回 JSON，格式如下：
{
  "answer": "最终答案",
  "steps": ["步骤1", "步骤2", "步骤3"],
  "knowledge_points": ["知识点1", "知识点2"],
  "similar_question": "一道类似的新题目"
}

要求：
1. 只返回 JSON，不要返回 markdown，不要加 ```json
2. steps 必须清晰易懂，适合初中学生
3. knowledge_points 只返回核心知识点
4. similar_question 必须和原题难度接近
5. 如果题目不清晰，也要尽量给出合理提示，并保持 JSON 格式
"""


def solve_math_question(question: str):
    client = get_openai_client()
    model_name = get_model_name()

    context = build_context(question, top_k=3)
    matched_knowledge = get_knowledge_titles(question, top_k=3)

    user_content = f"题目：{question}"
    if context:
        user_content += f"\n\n以下是从数学知识库中检索到的参考内容，请优先基于这些内容解答：\n{context}"

    resp = client.chat.completions.create(
        model=model_name,
        temperature=0.3,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
    )

    content = (resp.choices[0].message.content or "").strip()

    if content.startswith("```json"):
        content = content.removeprefix("```json").strip()
    if content.startswith("```"):
        content = content.removeprefix("```").strip()
    if content.endswith("```"):
        content = content.removesuffix("```").strip()

    if not content:
        raise ValueError("模型返回为空")

    try:
        data = json.loads(content)
    except Exception:
        raise ValueError(f"模型返回的不是合法 JSON：{content}")

    for key in ["answer", "steps", "knowledge_points", "similar_question"]:
        if key not in data:
            raise ValueError(f"模型返回缺少字段 {key}：{data}")

    if not isinstance(data["steps"], list):
        raise ValueError(f"steps 不是数组：{data}")

    if not isinstance(data["knowledge_points"], list):
        raise ValueError(f"knowledge_points 不是数组：{data}")

    data["matched_knowledge"] = matched_knowledge
    return data


def get_model_name() -> str:
    if not MODEL:
        raise ValueError("未读取到 OPENAI_MODEL")
    return MODEL


def get_openai_client() -> OpenAI:
    global _client
    if not OPENAI_API_KEY:
        raise ValueError("未读取到 OPENAI_API_KEY")
    if not OPENAI_BASE_URL:
        raise ValueError("未读取到 OPENAI_BASE_URL")
    if _client is None:
        _client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )
    return _client
