import redis.asyncio as redis_asyncio
import os
import json
import logging
import re
from typing import List, Dict, Optional
from redis.commands.search.field import TextField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import AuthenticationError, ResponseError  # Import exceptions from the correct module
from fastapi import HTTPException
from database import db as database

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = str(os.getenv("REDIS_DB", 0))
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "True") == "True"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)

# Singleton Redis connection for search
redis_client: Optional[redis_asyncio.Redis] = None

def get_wildcard(query: str) -> str:
    """Convert a query string to a Redis search query string"""
    # Escape any special characters in the query
    escaped_query = query.replace("'", r"\\'").replace('"', r'\\"')
    # separate words by spaces and add wildcard for fuzzy match based on Levenshtein distance
    words = escaped_query.split()
    wildcard_query = " ".join([f"%%{word}%%" for word in words])
    return wildcard_query

def to_restaurant_query(query: str) -> str:
    return f" (@name:{query}) | (@description:{query}) | (@type:{query}) | (@products_text:{query})"

def to_product_query(query: str, restaurant_id: str) -> str:
    # Compose the RediSearch query for product search within a restaurant
    # Example: ( (@name:%fish%) | (@description:%fish%) | (@ingredients:%fish%) ) @restaurant_id:"68105134fb5fb08039605d38"
    return f"((@name:{query}) | (@description:{query}) | (@ingredients:{query})) @restaurant_id:\"{restaurant_id}\""

async def get_redis_search_client() -> redis_asyncio.Redis:
    global redis_client
    if redis_client is None:
        try:
            # Use settings from env.py instead of environment variables directly
            redis_client = redis_asyncio.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                username=REDIS_USERNAME,
                decode_responses=REDIS_DECODE_RESPONSES,
                password=REDIS_PASSWORD,
                socket_connect_timeout=10.0,       # Add timeout to prevent hanging
                socket_keepalive=True              # Keep connection alive
            )
            # Test the connection - properly await the ping coroutine
            logging.info("Connecting to Redis...")
            await redis_client.ping()  # Will raise an error if authentication fails
            logging.info("Successfully connected to Redis")
        except AuthenticationError as e:
            logging.exception("Redis authentication error: %s", e)
            raise
        except ResponseError as e:
            logging.exception("Redis response error: %s", e)
            raise
        except Exception as e:
            logging.exception("Redis connection error: %s", e)
            raise
    return redis_client

async def create_search_indices():
    """Create Redis search indices if they don't exist"""
    r = await get_redis_search_client()
    # Restaurant search index
    try:
        await r.ft("restaurant-idx").info()
        logging.info("Restaurant search index already exists")
    except Exception:
        logging.info("Creating restaurant search index")
        # Use prefix for restaurant keys
        await r.ft("restaurant-idx").create_index([
            TextField("name", weight=5.0),
            TextField("description", weight=1.0),
            TextField("type", weight=2.0),
            TextField("products_text", weight=1.0)  # Contains concatenated product data
        ], definition=IndexDefinition(prefix=["restaurant:"], index_type=IndexType.HASH))
    # Product search index
    try:
        await r.ft("product-idx").info()
        logging.info("Product search index already exists")
    except Exception:
        logging.info("Creating product search index")
        # Use prefix for product keys
        await r.ft("product-idx").create_index([
            TextField("name", weight=5.0),
            TextField("description", weight=1.0),
            TextField("ingredients", weight=2.0),
            TextField("restaurant_id", weight=1.0)
        ], definition=IndexDefinition(prefix=["product:"], index_type=IndexType.HASH))

async def index_restaurant(restaurant_id: str, restaurant_data: dict, products: List[dict]):
    """Index a restaurant and its products for search"""
    r = await get_redis_search_client()
    # Create products_text field by concatenating product names and descriptions
    products_text = ""
    if products:
        products_text = " ".join([
            f"{p.get('name', '')} {p.get('description', '')}" for p in products
        ])
    # Index restaurant with products_text
    restaurant_doc = {
        "name": restaurant_data.get("name", ""),
        "description": restaurant_data.get("description", "") or "",
        "type": restaurant_data.get("type", "") or "",
        "products_text": products_text
    }
    # Store with restaurant: prefix
    await r.hset(f"restaurant:{restaurant_id}", mapping=restaurant_doc)
    # Index each product
    for product in products:
        product_id = product.get("id")
        if product_id:
            ingredients = " ".join(product.get("ingredients", []))
            product_doc = {
                "name": product.get("name", ""),
                "description": product.get("description", "") or "",
                "ingredients": ingredients,
                "restaurant_id": restaurant_id
            }
            # Store with product: prefix
            await r.hset(f"product:{product_id}", mapping=product_doc)

def _word_regexes(query: str) -> List[re.Pattern]:
    """Case-insensitive substring regex per word (AND across words in the Mongo fallback)."""
    return [re.compile(re.escape(w), re.IGNORECASE) for w in query.split() if w]

async def _mongo_search_restaurant_ids(query: str, limit: int, offset: int) -> List[str]:
    """MongoDB fallback when RediSearch is unavailable: match words against
    restaurant name/description/type and product name/description/ingredients."""
    collection = database.db.db["restaurants"]
    word_filters = [{"$or": [{"name": r}, {"description": r}, {"type": r}]} for r in _word_regexes(query)]
    direct_ids = await collection.distinct("_id", {"$and": word_filters} if word_filters else {})
    product_filters = [{"$or": [{"name": r}, {"description": r}, {"ingredients": r}]} for r in _word_regexes(query)]
    product_restaurant_ids = await database.db.db["products"].distinct(
        "restaurant_id", {"$and": product_filters} if product_filters else {})
    # Direct restaurant matches first, then restaurants matched via their products
    ids: List[str] = []
    seen = set()
    for oid in list(direct_ids) + product_restaurant_ids:
        sid = str(oid)
        if sid not in seen:
            seen.add(sid)
            ids.append(sid)
    return ids[offset:offset + limit]

async def _mongo_search_products(query: str, restaurant_id: str, limit: int, offset: int) -> List[Dict]:
    """MongoDB fallback when RediSearch is unavailable."""
    collection = database.db.db["products"]
    word_filters = [{"$or": [{"name": r}, {"description": r}, {"ingredients": r}]} for r in _word_regexes(query)]
    mongo_filter = {"restaurant_id": restaurant_id}
    if word_filters:
        mongo_filter["$and"] = word_filters
    cursor = collection.find(mongo_filter).skip(offset).limit(limit)
    return [{"product_id": str(doc["_id"]), "restaurant_id": doc["restaurant_id"]}
            async for doc in cursor]

async def search_restaurants(query: str, limit: int = 10, offset: int = 0) -> List[dict]:
    """Search restaurants by name, description, type or products (supports prefix/non-exact match)"""
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        r = await get_redis_search_client()
        # Build search query - remove any non A-Z, a-z, 0-9 characters and escape any special characters
        #regex = re.compile(r"[^A-Za-z0-9 ]")
        #cleaned_query = regex.sub("", query)

        redis_query = to_restaurant_query(get_wildcard(query))

        print(f"Redis query: {redis_query}")
        query_obj = Query(redis_query).paging(offset, limit)
        results = await r.ft("restaurant-idx").search(query_obj)
        restaurant_ids = []
        for doc in results.docs:
            restaurant_id = doc.id.split(":", 1)[1] if ":" in doc.id else doc.id
            restaurant_ids.append(restaurant_id)
        return restaurant_ids
    except HTTPException:
        raise
    except Exception as e:
        logging.warning(f"Redis search unavailable, falling back to MongoDB: {e}")
        return await _mongo_search_restaurant_ids(query, limit, offset)

async def search_products(query: str, restaurant_id: str, limit: int = 10, offset: int = 0) -> List[dict]:
    """Search products by name, description or ingredients (supports prefix/non-exact match)"""
    if not query or not restaurant_id:
        return []
    try:
        r = await get_redis_search_client()
        redis_query = to_product_query(get_wildcard(query), restaurant_id)
        print(redis_query)
        query_obj = Query(redis_query).paging(offset, limit)
        results = await r.ft("product-idx").search(query_obj)
        products = []
        for doc in results.docs:
            product_id = doc.id.split(":", 1)[1] if ":" in doc.id else doc.id
            doc_restaurant_id = getattr(doc, "restaurant_id", None)
            products.append({
                "product_id": product_id,
                "restaurant_id": doc_restaurant_id
            })
        return products
    except Exception as e:
        logging.warning(f"Redis search unavailable, falling back to MongoDB: {e}")
        return await _mongo_search_products(query, restaurant_id, limit, offset)