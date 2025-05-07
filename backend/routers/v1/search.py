from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from models.restaurant import Restaurant
from models.product import Product
import traceback
from cache.redis.search import search_restaurants, search_products
from database.repositories.restuarant import RestaurantRepository
from database.repositories.product import ProductRepository
from pydantic import BaseModel

router = APIRouter(
    prefix="/search",
    tags=["Search"],
    responses={404: {"description": "Not found"}},
)

class SearchResponse(BaseModel):
    count: int
    results: List[Dict]

@router.get("/restaurants", response_model=SearchResponse)
async def search_restaurants_endpoint(
    q: str = Query(..., description="Search query for restaurants, products or cuisines"),
    limit: int = Query(10, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """
    Search for restaurants by name, description, type, or associated products.
    Returns restaurants that match the search query.
    """
    try:
        # Get restaurant IDs from Redis search
        restaurant_ids = await search_restaurants(q, limit=limit, offset=offset)
        
        print(f"Restaurant IDs: {restaurant_ids}")
        
        if not restaurant_ids:
            return SearchResponse(count=0, results=[])
        # Fetch all restaurants in a single query
        all_restaurants = await RestaurantRepository.list_restaurants()
        # Build a dict for fast lookup
        restaurant_dict = {r.id: r for r in all_restaurants}
        # Build Restaurant models for results (as dicts for Pydantic v2 compatibility)
        results = [Restaurant.from_db_model(restaurant_dict[rid]).model_dump() for rid in restaurant_ids if rid in restaurant_dict]
        return SearchResponse(count=len(results), results=results)
    except Exception as e:
        error_detail = f"Search error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/products", response_model=SearchResponse)
async def search_products_endpoint(
    q: str = Query(..., description="Search query for products, ingredients or descriptions"),
    restaurant_id: str = Query(..., description="Restaurant ID to filter products by restaurant"),
    limit: int = Query(10, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """
    Search for products by name, description, or ingredients. Returns products that match the search query, including basic restaurant info for each product.
    """
    try:
        # Get product refs from Redis search (list of product_ids)
        product_refs = await search_products(q, restaurant_id, limit=limit, offset=offset)
        if not product_refs:
            return SearchResponse(count=0, results=[])
        # Fetch product details for each product_id
        products = await ProductRepository.list_products_by_ids(product_refs)
        # Fetch all restaurants for mapping id->name
        all_restaurants = await RestaurantRepository.list_restaurants()
        restaurant_map = {r.id: r for r in all_restaurants}
        # Build response with product models and nested restaurant info
        results = []
        for p in products:
            rest = restaurant_map.get(p.restaurant_id)
            product_model = Product(
                id=p.id,
                name=p.name,
                description=p.description,
                price=p.price,
                img_url=p.img_url,
                ingredients=p.ingredients
            )
            # Attach restaurant info as dict (to match API response)
            product_dict = product_model.model_dump()
            product_dict["restaurant"] = {
                "id": rest.id if rest else None,
                "name": rest.name if rest else None
            }
            results.append(product_dict)
        return SearchResponse(count=len(results), results=results)
    except Exception as e:
        error_detail = f"Search error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)