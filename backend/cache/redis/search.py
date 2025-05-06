import redis.asyncio as redis_asyncio
import os
import json
import logging
from typing import List, Dict, Optional
from redis.commands.search.field import TextField, TagField
from redis.commands.search.index_definition import IndexDefinition, IndexType

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = str(os.getenv("REDIS_DB", 0))
REDIS_DECODE_RESPONSES = os.getenv("REDIS_DECODE_RESPONSES", "True") == "True"
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

# Singleton Redis connection for search
redis_client: Optional[redis_asyncio.Redis] = None

def get_redis_search_client() -> redis_asyncio.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis_asyncio.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            db=REDIS_DB,
            decode_responses=REDIS_DECODE_RESPONSES,
            password=REDIS_PASSWORD,
        )
    return redis_client

async def create_search_indices():
    """Create Redis search indices if they don't exist"""
    r = get_redis_search_client()
    # Restaurant search index
    try:
        await r.ft("restaurant-idx").info()
        logging.info("Restaurant search index already exists")
    except Exception:
        logging.info("Creating restaurant search index")
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
        await r.ft("product-idx").create_index([
            TextField("name", weight=5.0),
            TextField("description", weight=1.0),
            TextField("ingredients", weight=2.0),
            TextField("restaurant_id", weight=1.0)
        ], definition=IndexDefinition(prefix=["product:"], index_type=IndexType.HASH))

async def index_restaurant(restaurant_id: str, restaurant_data: dict, products: List[dict]):
    """Index a restaurant and its products for search"""
    r = get_redis_search_client()
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
            await r.hset(f"product:{product_id}", mapping=product_doc)

async def search_restaurants(query: str, limit: int = 10, offset: int = 0) -> List[dict]:
    """Search restaurants by name, description, type or products"""
    if not query:
        return []
    r = get_redis_search_client()
    # Build search query - escape any special characters in the query
    escaped_query = query.replace("'", r"\\'").replace('"', r'\\"')
    # Search across multiple fields with different weights
    redis_query = f'(@name:"{escaped_query}")=>{{5.0}} | (@description:"{escaped_query}")=>{{1.0}} | ' \
                  f'(@type:"{escaped_query}")=>{{2.0}} | (@products_text:"{escaped_query}")=>{{1.0}}'
    # Execute search
    try:
        results = await r.ft("restaurant-idx").search(
            redis_query, 
            offset=offset,
            num=limit
        )
        # Process results - extract restaurant IDs from keys
        restaurant_ids = []
        for doc in results.docs:
            # Extract ID from key (format: "restaurant:ID")
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
    r = get_redis_search_client()
    # Build search query - escape any special characters in the query
    escaped_query = query.replace("'", r"\\'").replace('"', r'\\"')
    # Search across multiple fields with different weights
    redis_query = f'(@name:"{escaped_query}")=>{{5.0}} | (@description:"{escaped_query}")=>{{1.0}} | ' \
                  f'(@ingredients:"{escaped_query}")=>{{2.0}}'
    # Execute search
    try:
        results = await r.ft("product-idx").search(
            redis_query,
            offset=offset,
            num=limit
        )
        # Process results - extract product IDs and restaurant IDs
        products = []
        for doc in results.docs:
            # Extract ID from key (format: "product:ID")
            product_id = doc.id.split(":", 1)[1] if ":" in doc.id else doc.id
            restaurant_id = getattr(doc, "restaurant_id", None)
            products.append({
                "product_id": product_id,
                "restaurant_id": restaurant_id
            })
        return products
    except Exception as e:
        raise e # Log the error and return an empty list