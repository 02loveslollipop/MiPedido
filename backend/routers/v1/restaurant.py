from fastapi import APIRouter, HTTPException
from database.repositories import RestaurantRepository
from models import Restaurant, RestaurantCreate
import traceback
from cache.redis.cache import cache_restaurant, cache_restaurant_list, get_cached_restaurant_list, invalidate_restaurant_cache, invalidate_restaurant_list_cache

router = APIRouter(
    prefix="/restaurant",
    tags=["Restaurant"],
    responses={404: {"description": "Not found", "currrent router" : "restaurant"}},
)

@router.get("/", response_model=list[Restaurant])
async def list_restaurants():
    try:
        restaurants = await RestaurantRepository.list_restaurants()
        return restaurants
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)
    
@router.post ("/", response_model=Restaurant, status_code=201)
async def create_restaurant(restaurant: RestaurantCreate):
    try:
        created_restaurant = await RestaurantRepository.create_restaurant(restaurant)
        # Update cache for this restaurant and the restaurant list
        await cache_restaurant(created_restaurant.id, created_restaurant.model_dump())
        await invalidate_restaurant_list_cache()
        return created_restaurant
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    try:
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/cache", response_model=list[Restaurant])
async def get_cached_restaurants():
    cached = await get_cached_restaurant_list()
    if cached is not None:
        return cached
    # Fallback to DB if cache miss
    restaurants = await RestaurantRepository.list_restaurants()
    return [r.model_dump() for r in restaurants]