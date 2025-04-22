from fastapi import APIRouter, HTTPException, status, Depends
from database.repositories import RestaurantRepository, ProductRepository, UserRepository
from models import Restaurant, Product, OrderStatusResponse
import traceback
from typing import List
from utils.auth import get_current_user, TokenData, get_token_from_body, TokenRequest

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

@router.delete("/{restaurant_id}/{product_id}", response_model=OrderStatusResponse)
async def disable_product(
    restaurant_id: str, 
    product_id: str, 
    token_request: TokenRequest,
    current_user: TokenData = Depends(get_token_from_body)
):
    """
    Disables a product in a restaurant.
    Requires JWT authentication provided in the request body.
    The user must control the restaurant of the product.
    """
    try:
        # First check if the restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Check if user controls the restaurant
        is_authorized = await UserRepository.user_controls_restaurant(current_user.user_id, restaurant_id)
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This user cannot fulfill this request"
            )
        
        # Disable the product
        result = await ProductRepository.disable_product(product_id, restaurant_id)
        
        if result["status"] == "error":
            if "not found" in result["message"].lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=result["message"]
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
        
        # Return success response
        return OrderStatusResponse(status="Disabled")
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)