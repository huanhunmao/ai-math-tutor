import json
import os
from typing import List, Dict

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "math_knowledge.json")
QDRANT_PATH = os.path.join(BASE_DIR, "qdrant_data")
COLLECTION_NAME = "math_knowledge"
MODEL_NAME = os.getenv("RAG_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() not in {"0", "false", "off", "no"}

_model = None
_client = None
_rag_error = None


def is_rag_enabled() -> bool:
    return RAG_ENABLED


def get_rag_status() -> Dict[str, str | bool | None]:
    return {
        "enabled": RAG_ENABLED,
        "ready": _rag_error is None,
        "error": _rag_error,
        "model": MODEL_NAME,
    }


def _mark_rag_error(error: Exception):
    global _rag_error
    _rag_error = str(error)


def get_embedding_model():
    global _model, _rag_error
    if not RAG_ENABLED:
        raise RuntimeError("RAG 功能已关闭，请设置 RAG_ENABLED=true 后重试")
    if _model is None:
        try:
            _model = SentenceTransformer(MODEL_NAME)
            _rag_error = None
        except Exception as error:
            _mark_rag_error(error)
            raise
    return _model


def get_qdrant_client():
    global _client
    if not RAG_ENABLED:
        raise RuntimeError("RAG 功能已关闭，请设置 RAG_ENABLED=true 后重试")
    if _client is None:
        _client = QdrantClient(path=QDRANT_PATH)
    return _client


def load_knowledge_base() -> List[Dict]:
    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def build_doc_text(item: Dict) -> str:
    parts = [
        f"标题：{item.get('title', '')}",
        f"关键词：{'、'.join(item.get('keywords', []))}",
        f"内容：{item.get('content', '')}",
    ]
    return "\n".join(parts)


def ensure_collection():
    client = get_qdrant_client()
    model = get_embedding_model()
    vector_size = model.get_sentence_embedding_dimension()

    collections = client.get_collections().collections
    exists = any(c.name == COLLECTION_NAME for c in collections)

    if not exists:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


def rebuild_index():
    if not RAG_ENABLED:
        raise RuntimeError("RAG 功能已关闭，无法重建索引")
    client = get_qdrant_client()
    model = get_embedding_model()
    ensure_collection()

    kb = load_knowledge_base()

    client.delete_collection(collection_name=COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=Distance.COSINE,
        ),
    )

    if not kb:
        return {"count": 0}

    points = []
    docs = [build_doc_text(item) for item in kb]
    vectors = model.encode(docs, normalize_embeddings=True).tolist()

    for idx, (item, vector, doc_text) in enumerate(zip(kb, vectors, docs), start=1):
        points.append(
            PointStruct(
                id=idx,
                vector=vector,
                payload={
                    "title": item.get("title", ""),
                    "keywords": item.get("keywords", []),
                    "content": item.get("content", ""),
                    "doc_text": doc_text,
                },
            )
        )

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return {"count": len(points)}


def ensure_index_ready():
    if not RAG_ENABLED:
        return
    ensure_collection()
    client = get_qdrant_client()
    count_result = client.count(collection_name=COLLECTION_NAME, exact=True)
    if count_result.count == 0:
        rebuild_index()


def retrieve_knowledge(question: str, top_k: int = 3):
    if not RAG_ENABLED:
        return []

    try:
        ensure_index_ready()

        client = get_qdrant_client()
        model = get_embedding_model()

        query_vector = model.encode(question, normalize_embeddings=True).tolist()

        results = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True,
        )

        items = []

        for item in results.points:
            payload = item.payload or {}

            items.append(
                {
                    "title": payload.get("title", ""),
                    "keywords": payload.get("keywords", []),
                    "content": payload.get("content", ""),
                    "score": float(item.score),
                }
            )

        return items
    except Exception as error:
        _mark_rag_error(error)
        return []


def build_context(question: str, top_k: int = 3) -> str:
    items = retrieve_knowledge(question, top_k=top_k)
    if not items:
        return ""

    parts = []
    for idx, item in enumerate(items, start=1):
        parts.append(
            f"知识片段{idx}：\n"
            f"标题：{item['title']}\n"
            f"关键词：{'、'.join(item.get('keywords', []))}\n"
            f"内容：{item['content']}\n"
            f"相关度：{item['score']:.4f}\n"
        )
    return "\n".join(parts)


def get_knowledge_titles(question: str, top_k: int = 3) -> List[str]:
    items = retrieve_knowledge(question, top_k=top_k)
    return [item["title"] for item in items if item.get("title")]
