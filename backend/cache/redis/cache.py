import aioredis
import os
import json
from typing import Any, Optional, List

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Singleton Redis connection
redis: Optional[aioredis.Redis] = None

async def get_redis() -> aioredis.Redis:
    global redis
    if redis is None:
        redis = await aioredis.from_url(REDIS_URL, decode_responses=True)
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

# Refresh all cache (to be called on startup or periodically)
async def refresh_all_cache(fetch_restaurants, fetch_products_by_restaurant):
    restaurants = await fetch_restaurants()
    await cache_restaurant_list(restaurants)
    for rest in restaurants:
        await cache_restaurant(rest['id'], rest)
        products = await fetch_products_by_restaurant(rest['id'])
        await cache_product_list(rest['id'], products)
        for prod in products:
            await cache_product(prod['id'], prod)
