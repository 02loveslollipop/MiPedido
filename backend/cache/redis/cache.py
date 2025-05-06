import redis.asyncio as redis_asyncio
import os
import json
from typing import Any, Optional, List
from cache.redis.search import index_restaurant

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = str(os.getenv("REDIS_DB", 0))
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "True") == "True"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Singleton Redis connection
redis: Optional[redis_asyncio.Redis] = None

async def get_redis() -> redis_asyncio.Redis:
    global redis
    if redis is None:
        redis = redis_asyncio.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=REDIS_DECODE_RESPONSES,
            password=REDIS_PASSWORD,
        )
    return redis

# Restaurant cache functions
async def cache_restaurant(restaurant_id: str, data: dict, ttl: int = 3600):
    r = await get_redis()
    await r.set(f"restaurant:{restaurant_id}", json.dumps(data), ex=ttl)

async def get_cached_restaurant(restaurant_id: str) -> Optional[dict]:
    r = await get_redis()
    val = await r.get(f"restaurant:{restaurant_id}")
    if val:
        return json.loads(val)
    return None

async def invalidate_restaurant_cache(restaurant_id: str):
    r = await get_redis()
    await r.delete(f"restaurant:{restaurant_id}")

async def cache_restaurant_list(restaurants: List[dict], ttl: int = 3600):
    r = await get_redis()
    print(json.dumps(restaurants)) #TODO: remove this line
    await r.set("restaurants:all", json.dumps(restaurants), ex=ttl)

async def get_cached_restaurant_list() -> Optional[List[dict]]:
    r = await get_redis()
    val = await r.get("restaurants:all")
    if val:
        return json.loads(val)
    return None

async def invalidate_restaurant_list_cache():
    r = await get_redis()
    await r.delete("restaurants:all")

# Product cache functions
async def cache_product(product_id: str, data: dict, ttl: int = 3600):
    r = await get_redis()
    await r.set(f"product:{product_id}", json.dumps(data), ex=ttl)

async def get_cached_product(product_id: str) -> Optional[dict]:
    r = await get_redis()
    val = await r.get(f"product:{product_id}")
    if val:
        return json.loads(val)
    return None

async def invalidate_product_cache(product_id: str):
    r = await get_redis()
    await r.delete(f"product:{product_id}")

async def cache_product_list(restaurant_id: str, products: List[dict], ttl: int = 3600):
    r = await get_redis()
    await r.set(f"products:restaurant:{restaurant_id}", json.dumps(products), ex=ttl)

async def get_cached_product_list(restaurant_id: str) -> Optional[List[dict]]:
    r = await get_redis()
    val = await r.get(f"products:restaurant:{restaurant_id}")
    if val:
        return json.loads(val)
    return None

async def invalidate_product_list_cache(restaurant_id: str):
    r = await get_redis()
    await r.delete(f"products:restaurant:{restaurant_id}")