from fastapi import APIRouter, HTTPException, status, Depends
from database.repositories import RestaurantRepository, ProductRepository, UserRepository
from models import Restaurant, Product, OrderStatusResponse
import traceback
from typing import List, Dict
from utils.auth import get_current_user, TokenData, get_token_from_body, TokenRequest
import logging
from cache.redis.cache import get_cached_product_list, invalidate_product_cache, invalidate_product_list_cache

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

@router.get("/{restaurant_id}/all", response_model=List[Dict])
async def list_all_products(
    restaurant_id: str,
    current_user: TokenData = Depends(get_current_user)
):
    """
    Returns a list of all products (both enabled and disabled) for a specific restaurant.
    Requires authentication and proper authorization.
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
        
        # Check if user controls the restaurant
        is_authorized = await UserRepository.user_controls_restaurant(current_user.user_id, restaurant_id)
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This user cannot access this restaurant's products"
            )
        
        # Get all products for this restaurant (both active and inactive)
        products = await ProductRepository.list_all_products_by_restaurant(restaurant_id)
        return products
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{restaurant_id}/{product_id}")
async def get_product_details(restaurant_id: str, product_id: str):
    """
    Returns detailed information about a specific product in a restaurant.
    If the product or restaurant does not exist, it returns an error.
    """
    try:
        # First check if the restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
        
        # Get the product details
        product = await ProductRepository.get_product(product_id, restaurant_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        return product
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/cache/{restaurant_id}", response_model=List[Dict])
async def get_cached_products(restaurant_id: str):
    cached = await get_cached_product_list(restaurant_id)
    if cached is not None:
        return cached
    # Fallback to DB if cache miss
    products = await ProductRepository.list_all_products_by_restaurant(restaurant_id)
    return products

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
        
        # Invalidate product cache
        await invalidate_product_cache(product_id)
        await invalidate_product_list_cache(restaurant_id)
        
        # Return success response
        return OrderStatusResponse(status="Disabled")
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{restaurant_id}/{product_id}/enable", response_model=OrderStatusResponse)
async def enable_product(
    restaurant_id: str, 
    product_id: str, 
    token_request: TokenRequest,
    current_user: TokenData = Depends(get_token_from_body)
):
    """
    Enables a previously disabled product in a restaurant.
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
        
        # Enable the product
        result = await ProductRepository.enable_product(product_id, restaurant_id)
        
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
        
        # Invalidate product cache
        await invalidate_product_cache(product_id)
        await invalidate_product_list_cache(restaurant_id)
        
        # Return success response
        return OrderStatusResponse(status="Enabled")
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        LOG = logging.getLogger("uvicorn.error")
        LOG.error(f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=error_detail)