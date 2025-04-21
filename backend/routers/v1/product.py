from fastapi import APIRouter, HTTPException, status
from database.repositories import RestaurantRepository, ProductRepository
from models import Restaurant, Product
import traceback
from typing import List

router = APIRouter(
    prefix="/products",
    tags=["Products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/{restaurant_id}", response_model=List[Product])
async def list_products(restaurant_id: str):
    """
    Returns a list of products available for the user in a restaurant.
    If the restaurant does not exist, it returns an error.
    """
    try:
        # First check if the restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Get all products for this restaurant
        products = await ProductRepository.list_products_by_restaurant(restaurant_id)
        return products
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)