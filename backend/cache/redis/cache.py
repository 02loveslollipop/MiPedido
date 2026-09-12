import redis.asyncio as redis_asyncio
import os
import json
import logging
from typing import Any, Optional, List
from redis.exceptions import RedisError
from cache.redis.search import index_restaurant

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = str(os.getenv("REDIS_DB", 0))
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "True") == "True"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Singleton Redis connection
redis: Optional[redis_asyncio.Redis] = None

RESTAURANT_LIST_CACHE_KEY = "restaurants:all"

def get_redis() -> redis_asyncio.Redis:
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

# Cache operations must never take the API down: Redis is an optional
# accelerator. On any Redis failure, reads report a cache miss (callers fall
# back to MongoDB) and writes/invalidations are skipped.
async def _redis_op(op):
    try:
        r = get_redis()
        return await op(r)
    except (RedisError, OSError) as e:
        logging.warning(f"Redis unavailable, bypassing cache: {e}")
        return None

# Restaurant cache functions
async def cache_restaurant(restaurant_id: str, data: dict, ttl: int = 3600):
    async def op(r):
        await r.set(f"restaurant:{restaurant_id}", json.dumps(data, default=str), ex=ttl)
    await _redis_op(op)

async def get_cached_restaurant(restaurant_id: str) -> Optional[dict]:
    async def op(r):
        return await r.get(f"restaurant:{restaurant_id}")
    val = await _redis_op(op)
    if val:
        return json.loads(val)
    return None

async def invalidate_restaurant_cache(restaurant_id: str):
    async def op(r):
        await r.delete(f"restaurant:{restaurant_id}")
    await _redis_op(op)

async def cache_restaurant_list(restaurants: List[dict], ttl: int = 3600):
    async def op(r):
        await r.set(RESTAURANT_LIST_CACHE_KEY, json.dumps(restaurants, default=str), ex=ttl)
    await _redis_op(op)

async def get_cached_restaurant_list() -> Optional[List[dict]]:
    async def op(r):
        return await r.get(RESTAURANT_LIST_CACHE_KEY)
    val = await _redis_op(op)
    if val:
        return json.loads(val)
    return None

async def invalidate_restaurant_list_cache():
    async def op(r):
        await r.delete(RESTAURANT_LIST_CACHE_KEY)
    await _redis_op(op)

# Product cache functions
async def cache_product(product_id: str, data: dict, ttl: int = 3600):
    async def op(r):
        await r.set(f"product:{product_id}", json.dumps(data, default=str), ex=ttl)
    await _redis_op(op)

async def get_cached_product(product_id: str) -> Optional[dict]:
    async def op(r):
        return await r.get(f"product:{product_id}")
    val = await _redis_op(op)
    if val:
        return json.loads(val)
    return None

async def invalidate_product_cache(product_id: str):
    async def op(r):
        await r.delete(f"product:{product_id}")
    await _redis_op(op)

async def cache_product_list(restaurant_id: str, products: List[dict], ttl: int = 3600):
    async def op(r):
        await r.set(f"products:restaurant:{restaurant_id}", json.dumps(products, default=str), ex=ttl)
    await _redis_op(op)

async def get_cached_product_list(restaurant_id: str) -> Optional[List[dict]]:
    async def op(r):
        return await r.get(f"products:restaurant:{restaurant_id}")
    val = await _redis_op(op)
    if val:
        return json.loads(val)
    return None

async def invalidate_product_list_cache(restaurant_id: str):
    async def op(r):
        await r.delete(f"products:restaurant:{restaurant_id}")
    await _redis_op(op)
