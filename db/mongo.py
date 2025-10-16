# core/mongo.py
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient
from core.config import settings

@lru_cache
def _client() -> AsyncIOMotorClient:
    return AsyncIOMotorClient(settings.mongo_uri)

def get_mongo_db():
    db = _client()[settings.mongo_db]
    return db
