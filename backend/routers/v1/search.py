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
        
        # Fetch full restaurant data for the matching IDs
        results = []
        for restaurant_id in restaurant_ids:
            restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
            if restaurant:
                results.append(restaurant.model_dump())
        
        return SearchResponse(count=len(results), results=results)
    except Exception as e:
        error_detail = f"Search error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/products", response_model=SearchResponse)
async def search_products_endpoint(
    q: str = Query(..., description="Search query for products, ingredients or descriptions"),
    limit: int = Query(10, description="Maximum number of results to return"),
    offset: int = Query(0, description="Number of results to skip")
):
    """
    Search for products by name, description, or ingredients.
    Returns products that match the search query.
    """
    try:
        # Get product references from Redis search
        product_refs = await search_products(q, limit=limit, offset=offset)
        
        # Fetch full product data for the matching IDs
        results = []
        for ref in product_refs:
            product_id = ref.get("product_id")
            restaurant_id = ref.get("restaurant_id")
            
            if product_id and restaurant_id:
                product = await ProductRepository.get_product(product_id, restaurant_id)
                if product:
                    # Add restaurant info to the product
                    restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
                    if restaurant:
                        product["restaurant"] = {
                            "id": restaurant.id,
                            "name": restaurant.name
                        }
                    results.append(product)
        
        return SearchResponse(count=len(results), results=results)
    except Exception as e:
        error_detail = f"Search error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)