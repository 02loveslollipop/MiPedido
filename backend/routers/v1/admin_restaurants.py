from fastapi import APIRouter, HTTPException, status, Depends
from models.restaurant import Restaurant, RestaurantCreate, RestaurantBase
from database.repositories import RestaurantRepository
from utils.admin_auth import get_current_admin, AdminTokenData
from utils.admin_logger import log_admin_operation
import traceback
import logging
from typing import List
from pydantic import BaseModel
from bson import ObjectId

router = APIRouter(
    prefix="/admin/restaurants",
    tags=["Admin Restaurants"],
    responses={404: {"description": "Not found"}},
)

class RestaurantUpdate(BaseModel):
    """Schema for updating restaurant details"""
    name: str | None = None
    img_url: str | None = None
    type: str | None = None
    description: str | None = None
    
@router.get("/", response_model=List[Restaurant])
async def admin_list_restaurants(current_admin: AdminTokenData = Depends(get_current_admin)):
    """
    List all restaurants. Only accessible by admins.
    """
    try:
        restaurants = await RestaurantRepository.list_restaurants()
        return restaurants
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error listing restaurants: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/", response_model=Restaurant, status_code=201)
async def admin_create_restaurant(
    restaurant: RestaurantCreate, 
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Create a new restaurant. Only accessible by admins.
    """
    try:
        created_restaurant = await RestaurantRepository.create_restaurant(restaurant)
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="create",
            target_type="restaurant",
            target_id=created_restaurant.id,
            details={"name": created_restaurant.name}
        )
        
        return created_restaurant
    except HTTPException as e:
        logging.error(f"Error creating restaurant: {str(e)}")
        logging.error(traceback.format_exc())
        raise e
    except Exception as e:
        logging.error(f"Error creating restaurant: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{restaurant_id}", response_model=Restaurant)
async def admin_get_restaurant(
    restaurant_id: str, 
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Get details of a specific restaurant. Only accessible by admins.
    """
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

@router.put("/{restaurant_id}", response_model=Restaurant)
async def admin_update_restaurant(
    restaurant_id: str,
    restaurant_data: RestaurantUpdate,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Update a restaurant's details. Only accessible by admins.
    """
    try:
        # First check if restaurant exists
        existing_restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not existing_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Build update data dictionary
        update_data = {}
        if restaurant_data.name is not None:
            update_data["name"] = restaurant_data.name
        if restaurant_data.img_url is not None:
            update_data["img_url"] = restaurant_data.img_url
        if restaurant_data.type is not None:
            update_data["type"] = restaurant_data.type
        if restaurant_data.description is not None:
            update_data["description"] = restaurant_data.description
            
        # Update restaurant
        await RestaurantRepository.collection.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": update_data}
        )
        
        # Get the updated restaurant
        updated_restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="update",
            target_type="restaurant",
            target_id=restaurant_id,
            details={"updated_fields": list(update_data.keys())}
        )
        
        return updated_restaurant
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error updating restaurant: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.delete("/{restaurant_id}", status_code=204)
async def admin_delete_restaurant(
    restaurant_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Delete a restaurant. Only accessible by admins.
    """
    try:
        # Check if restaurant exists
        existing_restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not existing_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
        
        # Save restaurant info for logging before deletion
        restaurant_name = existing_restaurant.name
            
        # Delete the restaurant
        result = await RestaurantRepository.collection.delete_one({"_id": ObjectId(restaurant_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete restaurant")
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="delete",
            target_type="restaurant",
            target_id=restaurant_id,
            details={"name": restaurant_name}
        )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{restaurant_id}/update-rating", status_code=200)
async def admin_update_restaurant_rating(
    restaurant_id: str,
    data: dict,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Manually update a restaurant's rating. Only accessible by admins.
    """
    try:
        if "rating" not in data:
            raise HTTPException(status_code=400, detail="Rating required")
            
        rating = data["rating"]
        
        # Validate rating
        if not isinstance(rating, (int, float)) or rating < 0 or rating > 5:
            raise HTTPException(status_code=400, detail="Rating must be a number between 0 and 5")
        
        # Check if restaurant exists
        existing_restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not existing_restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        # Store old rating for logging
        old_rating = existing_restaurant.rating
            
        # Update rating
        await RestaurantRepository.collection.update_one(
            {"_id": ObjectId(restaurant_id)},
            {"$set": {"rating": rating}}
        )
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="update_rating",
            target_type="restaurant",
            target_id=restaurant_id,
            details={
                "old_rating": old_rating,
                "new_rating": rating,
                "name": existing_restaurant.name
            }
        )
        
        return {"message": "Rating updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)