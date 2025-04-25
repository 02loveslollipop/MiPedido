from fastapi import APIRouter, HTTPException, status, Depends
from typing import Dict, Any, List
import traceback
from bson import ObjectId
from datetime import datetime
import logging

from database.repositories import OrderRepository, RestaurantRepository, UserRepository
from models.order import OrderItemUpdate, OrderCreatedResponse, OrderProduct, CreateOrderRequest, JoinOrderResponse, OrderStatusResponse, OrderCompletedResponse, OrderFulfillResponse
from utils.auth import get_current_user, TokenData, get_token_from_body, TokenRequest

router = APIRouter(
    prefix="/order",
    tags=["Order"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderCreatedResponse, status_code=201)
async def create_order(request: CreateOrderRequest):
    """
    Creates an empty order in a restaurant and returns the order id and the user id.
    If the restaurant does not exist, it returns an error.
    """
    try:
        # Check if restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(request.restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )
        
        # Create the order
        order_data = await OrderRepository.create_order(request.restaurant_id)
        return order_data
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )

@router.put("/{order_id}", response_model=JoinOrderResponse, status_code=201)
async def join_order(order_id: str):
    """
    Adds a user to an existing order.
    Returns the user id for the specific order.
    If the order does not exist, it returns an error.
    """
    try:
        user_id = await OrderRepository.join_order(order_id)
        if not user_id:
            raise HTTPException(
                status_code=404,
                detail="Order not found"
            )
        
        return JoinOrderResponse(user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=500,
            detail=error_detail
        )

@router.put("/{order_id}/{user_id}", response_model=OrderStatusResponse)
async def modify_user_order(order_id: str, user_id: str, item_update: OrderItemUpdate):
    """
    Modify the order of a user.
    - If the product does not exist, it is created
    - If it exists, it is updated
    - If the given quantity is 0, it is deleted
    """
    try:
        result = await OrderRepository.modify_order(
            order_id=order_id,
            user_id=user_id,
            product_id=item_update.product_id,
            quantity=item_update.quantity,
            ingredients=item_update.ingredients
        )
        
        # Check for errors
        if result["status"] == "error":
            if result["message"] == "Order not found":
                raise HTTPException(status_code=404, detail="Order not found")
            elif result["message"] == "User not found for order":
                raise HTTPException(status_code=404, detail="User not found for order")
            elif result["message"] == "Product not found in the restaurant":
                raise HTTPException(status_code=404, detail="Product not found in the restaurant")
            elif result["message"] == "Ingredient not found for product":
                raise HTTPException(status_code=404, detail="Ingredient not found for product")
            else:
                # Generic error
                raise HTTPException(status_code=500, detail=result["message"])
        
        # Return appropriate status and response code
        if result["message"] == "Created":
            return OrderStatusResponse(status="Created")
        elif result["message"] == "Updated":
            return OrderStatusResponse(status="Updated")
        elif result["message"] == "Deleted":
            return OrderStatusResponse(status="Deleted")
        else:
            return OrderStatusResponse(status=result["message"])
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{order_id}/{user_id}", response_model=List[OrderProduct])
async def get_user_order(order_id: str, user_id: str):
    """
    Returns the order of a specific user.
    If the order does not exist, it returns an error.
    If the user does not exist for the order, it returns an error.
    """
    try:
        result = await OrderRepository.get_user_order(order_id, user_id)
        
        if result["status"] == "error":
            if result["message"] == "Order not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )
            elif result["message"] == "User not found for order":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found for order"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
        
        # Return the list of products
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.post("/{order_id}/finalize", response_model=OrderCompletedResponse)
async def finalize_order(
    order_id: str, 
    token_request: TokenRequest,
    current_user: TokenData = Depends(get_token_from_body)
):
    """
    Finalize the order and return the final order with all products aggregated.
    This makes the order ready for fulfillment but doesn't mark it as fulfilled yet.
    An order can be finalized multiple times as long as it hasn't been fulfilled.
    Requires JWT authentication provided in the request body.
    The user must control the restaurant of the order.
    """
    try:
        # Get the order to check the restaurant_id
        order_doc = await OrderRepository.collection.find_one({"_id": ObjectId(order_id)})
        if not order_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user controls the restaurant
        restaurant_id = order_doc.get("restaurant_id")
        is_authorized = await UserRepository.user_controls_restaurant(current_user.user_id, restaurant_id)
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This user cannot finalize this order"
            )
        
        # Finalize the order and get the aggregated result
        result = await OrderRepository.finalize_order(order_id)
        
        if result["status"] == "error":
            if result["message"] == "Order not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )
            elif result["message"] == "Order already fulfilled":
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Order already fulfilled"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
                
        # Return the completed order with current datetime as placeholder for date_completed
        # The actual date_completed will be set when the order is fulfilled
        response_data = {**result["data"], "date_completed": datetime.now()}
        return OrderCompletedResponse(**response_data)
    
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )

@router.post("/{order_id}/fulfill", response_model=OrderFulfillResponse)
async def fulfill_order(
    order_id: str,
    token_request: TokenRequest,
    current_user: TokenData = Depends(get_token_from_body)
):
    """
    Mark an order as fulfilled by a business user.
    Requires JWT authentication provided in the request body.
    The user must control the restaurant of the order.
    The order must be finalized before it can be fulfilled.
    This endpoint adds the date_completed field to the order.
    """
    try:
        # Get the order to check the restaurant_id
        order_doc = await OrderRepository.collection.find_one({"_id": ObjectId(order_id)})
        if not order_doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Check if user controls the restaurant
        restaurant_id = order_doc.get("restaurant_id")
        is_authorized = await UserRepository.user_controls_restaurant(current_user.user_id, restaurant_id)
        
        if not is_authorized:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="This user cannot fulfill this order"
            )
            
        # Fulfill the order
        result = await OrderRepository.fulfill_order(order_id)
        
        if result["status"] == "error":
            if result["message"] == "Order not found":
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Order not found"
                )
            elif result["message"] == "Order already fulfilled":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order already fulfilled"
                )
            elif result["message"] == "Order must be finalized before fulfillment":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Order must be finalized before fulfillment"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
                
        # Return the fulfillment response
        return OrderFulfillResponse(
            status="Fulfilled",
            fulfilled_at=result["fulfilled_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )