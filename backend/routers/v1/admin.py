from fastapi import APIRouter, HTTPException, status, Depends
from models.admin import AdminAuth, AdminToken, Admin, AdminUpdate
from database.repositories.admin_repository import AdminRepository
from utils.admin_auth import get_current_admin, AdminTokenData
from utils.admin_logger import log_admin_operation  # Import the logging utility
import traceback
from typing import List

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=AdminToken)
async def admin_login(admin_auth: AdminAuth):
    """
    Admin login endpoint
    
    Authenticates an admin and returns an access token
    """
    try:
        result = await AdminRepository.authenticate_admin(
            username=admin_auth.username,
            password=admin_auth.password
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin credentials"
            )
            
        return AdminToken(**result)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/me", response_model=Admin)
async def get_current_admin_info(current_admin: AdminTokenData = Depends(get_current_admin)):
    """
    Get current admin information
    
    Returns information about the currently authenticated admin
    """
    try:
        admin = await AdminRepository.get_admin_by_id(current_admin.admin_id)
        
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
            
        return Admin(id=admin.id, username=admin.username)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

# Admin management endpoints
@router.post("/", response_model=Admin, status_code=status.HTTP_201_CREATED)
async def create_admin(
    admin: AdminAuth,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Create a new admin
    
    Only existing admins can create new admins
    """
    try:
        new_admin = await AdminRepository.create_admin(
            username=admin.username,
            password=admin.password
        )
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="create",
            target_type="admin",
            target_id=new_admin.id,
            details={"username": new_admin.username}
        )
        
        return new_admin
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/", response_model=List[Admin])
async def list_admins(current_admin: AdminTokenData = Depends(get_current_admin)):
    """
    List all admin users
    
    Only accessible by admins
    """
    try:
        admins = await AdminRepository.list_admins()
        return admins
    except Exception as e:
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{admin_id}", response_model=Admin)
async def update_admin(
    admin_id: str,
    admin_update: AdminUpdate,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Update an admin's information
    
    Only accessible by admins
    """
    try:
        # Check if admin exists
        admin = await AdminRepository.get_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Admin not found"
            )
            
        # Update admin
        update_data = admin_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
            
        # If updating username, check if it already exists
        if "username" in update_data and update_data["username"] != admin.username:
            existing_admin = await AdminRepository.get_admin_by_username(update_data["username"])
            if existing_admin:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Admin with username '{update_data['username']}' already exists"
                )
                
        success = await AdminRepository.update_admin(admin_id, update_data)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update admin"
            )
        
        # Prepare log details - don't log password in details
        log_details = {
            "username": admin.username,
            "updated_fields": list(update_data.keys())
        }
        
        if "password" in update_data:
            log_details["updated_fields"].remove("password")
            log_details["password_updated"] = True
            
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="update",
            target_type="admin",
            target_id=admin_id,
            details=log_details
        )
            
        # Get updated admin
        updated_admin = await AdminRepository.get_admin_by_id(admin_id)
        return Admin(id=updated_admin.id, username=updated_admin.username)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)