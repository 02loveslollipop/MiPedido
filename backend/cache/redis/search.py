import redis.asyncio as redis_asyncio
import os
import json
import logging
from typing import List, Dict, Optional
from redis.commands.search.field import TextField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from redis.exceptions import AuthenticationError, ResponseError  # Import exceptions from the correct module

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = str(os.getenv("REDIS_DB", 0))  # Changed str() to int()
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "True") == "True"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
REDIS_USERNAME = os.getenv("REDIS_USERNAME", None)

# Singleton Redis connection for search
redis_client: Optional[redis_asyncio.Redis] = None

async def get_redis_search_client() -> redis_asyncio.Redis:
    global redis_client
    if redis_client is None:
        try:
            # Use settings from env.py instead of environment variables directly
            redis_client = redis_asyncio.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                #db=REDIS_DB,
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
            logging.error(f"Redis authentication error: {e}")
            raise
        except ResponseError as e:
            logging.error(f"Redis response error: {e}")
            raise
        except Exception as e:
            logging.error(f"Redis connection error: {e}")
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

async def search_restaurants(query: str, limit: int = 10, offset: int = 0) -> List[dict]:
    """Search restaurants by name, description, type or products"""
    if not query:
        return []
    r = await get_redis_search_client()
    # Build search query - escape any special characters in the query
    escaped_query = query.replace("'", r"\\'").replace('"', r'\\"')
    # Use a simple OR query across all fields for compatibility
    redis_query = f'@name:"{escaped_query}" | @description:"{escaped_query}" | @type:"{escaped_query}" | @products_text:"{escaped_query}"'
    # Execute search
    try:
        query_obj = Query(redis_query).paging(offset, limit)
        results = await r.ft("restaurant-idx").search(query_obj)
        restaurant_ids = []
        for doc in results.docs:
            restaurant_id = doc.id.split(":", 1)[1] if ":" in doc.id else doc.id
            restaurant_ids.append(restaurant_id)
        return restaurant_ids
    except Exception as e:
        logging.error(f"Redis search error: {str(e)}")
        return []

async def search_products(query: str, limit: int = 10, offset: int = 0) -> List[dict]:
    """Search products by name, description or ingredients"""
    if not query:
        return []
    r = await get_redis_search_client()
    # Build search query - escape any special characters in the query
    escaped_query = query.replace("'", r"\\'").replace('"', r'\\"')
    # Use a simple OR query across all fields for compatibility
    redis_query = f'@name:"{escaped_query}" | @description:"{escaped_query}" | @ingredients:"{escaped_query}"'
    # Execute search
    try:
        query_obj = Query(redis_query).paging(offset, limit)
        results = await r.ft("product-idx").search(query_obj)
        products = []
        for doc in results.docs:
            product_id = doc.id.split(":", 1)[1] if ":" in doc.id else doc.id
            restaurant_id = getattr(doc, "restaurant_id", None)
            products.append({
                "product_id": product_id,
                "restaurant_id": restaurant_id
            })
        return products
    except Exception as e:
        logging.error(f"Redis search error: {str(e)}")
        return []