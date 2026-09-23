"""lazily created MongoClient shared by mongo_store and the checkpointer."""

from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database
from config.settings import settings


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    return MongoClient(settings.mongo_uri.get_secret_value())


def get_db() -> Database:
    return get_client()[settings.mongo_db]