import uuid
from langchain_ollama import OllamaEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from config.settings import settings
from models.memory_models import RuleRecord

EMBEDDING_DIM = 768  # nomic-embed-text
SCORE_THRESHOLD = 0.75

COLLECTION_BY_RULE_TYPE = {
    "generation": "generation_rules",
    "evaluation": "evaluator_rules",
}

embeddings = OllamaEmbeddings(
    model=settings.ollama_embedding_model,
    base_url=settings.ollama_base_url,
)

client = QdrantClient(url=settings.qdrant_url,check_compatibility=False)


def _ensure_collection(name: str) -> None:
    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE),
        )


def _search_rules(collection: str, topic: str, top_k: int = 5) -> list[str]:
    _ensure_collection(collection)
    result = client.query_points(
        collection_name=collection,
        query=embeddings.embed_query(topic),
        limit=top_k,
        score_threshold=SCORE_THRESHOLD,
        with_payload=True,
    )
    return [
        point.payload["rule"]
        for point in result.points
        if point.payload and "rule" in point.payload
    ]


def get_generation_rules(topic: str) -> list[str]:
    return _search_rules(COLLECTION_BY_RULE_TYPE["generation"], topic)


def get_evaluation_rules(topic: str) -> list[str]:
    return _search_rules(COLLECTION_BY_RULE_TYPE["evaluation"], topic)


def _rule_point_id(record: RuleRecord) -> str:
    criteria_key = "|".join(sorted(record.source_criteria))
    key = f"{record.topic}::{record.rule_type}::{criteria_key}"
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, key))


def upsert_rule(record: RuleRecord) -> None:
    collection = COLLECTION_BY_RULE_TYPE[record.rule_type]
    _ensure_collection(collection)
    client.upsert(
        collection_name=collection,
        points=[
            PointStruct(
                id=_rule_point_id(record),
                vector=embeddings.embed_query(record.topic),
                payload=record.model_dump(),
            )
        ],
    )