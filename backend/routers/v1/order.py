from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List

from database.repositories import OrderRepository, RestaurantRepository
from models.order import OrderItemUpdate, OrderCreatedResponse, OrderProduct

router = APIRouter(
    prefix="/order",
    tags=["Order"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=OrderCreatedResponse, status_code=201)
async def create_order(data: Dict[str, str]):
    """
    Creates an empty order in a restaurant and returns the order id and the user id.
    If the restaurant does not exist, it returns an error.
    """
    restaurant_id = data.get("restaurant_id")
    if not restaurant_id:
        raise HTTPException(
            status_code=400, 
            detail="Restaurant ID is required"
        )
    
    try:
        # Check if restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=404,
                detail="Restaurant not found"
            )
        
        # Create the order
        order_data = await OrderRepository.create_order(restaurant_id)
        return order_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.put("/{order_id}", status_code=201)
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
        
        return {"user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.put("/{order_id}/{user_id}", response_model=Dict[str, str])
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
            return {"status": "Created"}
        elif result["message"] == "Updated":
            return {"status": "Updated"}
        elif result["message"] == "Deleted":
            return {"status": "Deleted"}
        else:
            return {"status": result["message"]}
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(status_code=500, detail=str(e))

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )