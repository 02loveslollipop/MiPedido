from fastapi import APIRouter, HTTPException, Depends
import traceback
import logging
from typing import List, Dict
from models.user import UserAuth
from pydantic import BaseModel
from models.user import User
from database.repositories import UserRepository, RestaurantRepository
from utils.admin_auth import get_current_admin, AdminTokenData
from utils.admin_logger import log_admin_operation
from bson import ObjectId

router = APIRouter(
    prefix="/admin/users",
    tags=["Admin Users"],
    responses={404: {"description": "Not found"}},
)

class UserUpdate(BaseModel):
    """Schema for updating user details"""
    username: str | None = None
    password: str | None = None

@router.get("/", response_model=List[Dict])
async def admin_list_users(current_admin: AdminTokenData = Depends(get_current_admin)):
    """
    List all users. Only accessible by admins.
    """
    try:
        users = await UserRepository.get_users()
        if not users:
            raise HTTPException(status_code=404, detail="No users found")
        
        # Convert UserInDB objects to dictionaries
        user_dicts = []
        for user in users:
            user_dict = {
                "id": user.id,
                "username": user.username,
                "controls": user.controls if hasattr(user, "controls") else []
                # Don't include hashed_password for security
            }
            user_dicts.append(user_dict)
        
        return user_dicts
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)
        


@router.get("/{user_id}", response_model=Dict)
async def admin_get_user(
    user_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Get details of a specific user. Only accessible by admins.
    """
    try:
        user = await UserRepository.get_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Format the user data
        user_data = {
            "id": user.id,
            "username": user.username,
            "controls": user.controls
        }
        return user_data
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/", response_model=User, status_code=201)
async def admin_create_user(
    user_auth: UserAuth, 
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Create a new user. Only accessible by admins.
    """
    try:
        # Check if username already exists
        existing_user = await UserRepository.get_user_by_username(user_auth.username)
        if existing_user:
            raise HTTPException(status_code=400, detail=f"User with username {user_auth.username} already exists")
        
        # Create the user
        new_user = await UserRepository.create_user(
            username=user_auth.username,
            password=user_auth.password
        )
        logging.info(f"User created: {new_user.username} with ID: {new_user.id}")
        print(f"User created: {new_user.username} with ID: {new_user.id}")  # For debugging purposes
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="create",
            target_type="user",
            target_id=new_user.id,
            details={"username": new_user.username}
        )
        logging.info(f"Admin {current_admin.username} created user {new_user.username} with ID: {new_user.id}")
        
        return new_user
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        logging.error(f"Error creating user: {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{user_id}", status_code=200)
async def admin_update_user(
    user_id: str,
    user_data: UserUpdate,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Update a user's details. Only accessible by admins.
    """
    try:
        # First check if user exists
        existing_user = await UserRepository.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Build update data dictionary
        update_data = {}
        if user_data.username is not None:
            # Check if username is already taken
            if user_data.username != existing_user.username:
                user_by_username = await UserRepository.get_user_by_username(user_data.username)
                if user_by_username:
                    raise HTTPException(status_code=400, detail=f"Username {user_data.username} is already taken")
            update_data["username"] = user_data.username
            
        if user_data.password is not None:
            # Hash the new password
            import hashlib
            hashed_password = hashlib.sha256(user_data.password.encode()).hexdigest()
            update_data["hashed_password"] = hashed_password
            
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        # Update user
        await UserRepository.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        # Log the operation
        log_details = {
            "username": existing_user.username,
            "updated_fields": list(update_data.keys())
        }
        
        # Don't include password details in logs for security
        if "hashed_password" in update_data:
            log_details["updated_fields"].remove("hashed_password")
            log_details["password_updated"] = True
        
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="update",
            target_type="user",
            target_id=user_id,
            details=log_details
        )
        
        return {"message": "User updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.delete("/{user_id}", status_code=204)
async def admin_delete_user(
    user_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Delete a user. Only accessible by admins.
    """
    try:
        # Check if user exists
        existing_user = await UserRepository.get_user_by_id(user_id)
        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Store user info for logging
        username = existing_user.username
            
        # Delete the user
        result = await UserRepository.collection.delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete user")
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="delete",
            target_type="user",
            target_id=user_id,
            details={"username": username}
        )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{user_id}/assign-restaurant", status_code=200)
async def admin_assign_restaurant(
    user_id: str,
    data: dict,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Assign a restaurant to a user. Only accessible by admins.
    """
    try:
        if "restaurant_id" not in data:
            raise HTTPException(status_code=400, detail="Restaurant ID required")
            
        restaurant_id = data["restaurant_id"]
        
        # Check if user exists
        user = await UserRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        # Get current controls
        controls = user.controls.copy() if hasattr(user, 'controls') and user.controls else []
        
        # Check if already assigned
        already_assigned = restaurant_id in controls
        
        # Only add if not already assigned
        if not already_assigned:
            controls.append(restaurant_id)
        
            # Update user's restaurant controls
            await UserRepository.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"controls": controls}}
            )
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="assign_restaurant",
            target_type="user",
            target_id=user_id,
            details={
                "username": user.username,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant.name,
                "already_assigned": already_assigned
            }
        )
        
        return {"message": "Restaurant assigned successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{user_id}/revoke-restaurant", status_code=200)
async def admin_revoke_restaurant(
    user_id: str,
    data: dict,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Revoke a restaurant access from a user. Only accessible by admins.
    """
    try:
        if "restaurant_id" not in data:
            raise HTTPException(status_code=400, detail="Restaurant ID required")
            
        restaurant_id = data["restaurant_id"]
        
        # Check if user exists
        user = await UserRepository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
            
        # Get current controls
        controls = user.controls.copy() if hasattr(user, 'controls') and user.controls else []
        
        # Check if restaurant exists before querying for its name
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        restaurant_name = restaurant.name if restaurant else "Unknown Restaurant"
        
        # Remove if exists
        if restaurant_id in controls:
            controls.remove(restaurant_id)
            
            # Update user's restaurant controls
            await UserRepository.collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"controls": controls}}
            )
            
            was_revoked = True
        else:
            was_revoked = False
            raise HTTPException(status_code=400, detail="User does not control this restaurant")
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="revoke_restaurant",
            target_type="user",
            target_id=user_id,
            details={
                "username": user.username,
                "restaurant_id": restaurant_id,
                "restaurant_name": restaurant_name,
                "was_revoked": was_revoked
            }
        )
        
        return {"message": "Restaurant access revoked successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin user operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)