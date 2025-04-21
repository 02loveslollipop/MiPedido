from fastapi import APIRouter, HTTPException
from database.repositories import RestaurantRepository
from models import Restaurant

router = APIRouter(
    prefix="/restaurant",
    tags=["Restaurant"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=list[Restaurant])
async def list_restaurants():
    try:
        restaurants = await RestaurantRepository.list_restaurants()
        return restaurants
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post ("/", response_model=Restaurant, status_code=201)
async def create_restaurant(restaurant: Restaurant):
    try:
        created_restaurant = await RestaurantRepository.create_restaurant(restaurant)
        return created_restaurant
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{restaurant_id}", response_model=Restaurant)
async def get_restaurant(restaurant_id: str):
    try:
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        return restaurant
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))