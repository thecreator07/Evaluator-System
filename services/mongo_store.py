from datetime import datetime, timezone
from services.mongo_client import get_db

_runs = None


def _get_collection():
    global _runs
    if _runs is None:
        _runs = get_db()["lesson_runs"]
    return _runs


def persist_run(state) -> str:
    doc = {
        "topic": state.topic,
        "final_status": state.final_status,
        "attempt": state.attempt,
        "lesson": state.lesson.model_dump() if state.lesson else None,
        "evaluation": state.evaluation.model_dump() if state.evaluation else None,
        "rejection_log": [r.model_dump() for r in state.rejection_log],
        "created_at": datetime.now(timezone.utc),
    }
    result = _get_collection().insert_one(doc)
    return str(result.inserted_id)


def get_criterion_failure_history(topic: str, criterion_id: str, limit: int = 50) -> int:
    """How many past runs on this topic have a rejection record"""

    return _get_collection().count_documents(
        {"topic": topic, "rejection_log.failed_criteria": criterion_id},
        limit=limit,
    )