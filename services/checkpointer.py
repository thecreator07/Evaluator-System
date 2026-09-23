"""LangGraph checkpointer backed by the same MongoDB cluster as mongo_store."""

from functools import lru_cache
from langgraph.checkpoint.mongodb import MongoDBSaver
from config.settings import settings
from services.mongo_client import get_client


@lru_cache(maxsize=1)
def get_checkpointer() -> MongoDBSaver:
    return MongoDBSaver(get_client(), db_name=settings.mongo_db)