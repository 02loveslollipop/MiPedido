from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
import traceback
import logging
from bson import ObjectId
from models.product import ProductCreate, Product, ProductUpdate
from database.repositories import ProductRepository, RestaurantRepository
from utils.admin_auth import get_current_admin, AdminTokenData
from utils.admin_logger import log_admin_operation
from cache.redis.cache import cache_product

router = APIRouter(
    prefix="/admin/products",
    tags=["Admin Products"],
    responses={404: {"description": "Not found"}},
)

@router.get("/restaurant/{restaurant_id}", response_model=List[Dict])
async def admin_list_products(
    restaurant_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    List all products for a specific restaurant, including disabled ones.
    Only accessible by admins.
    """
    try:
        # First check if the restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        # Get all products
        products = await ProductRepository.list_all_products_by_restaurant(restaurant_id)
        return products
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.post("/", response_model=Product, status_code=201)
async def admin_create_product(
    product: ProductCreate,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Create a new product. Only accessible by admins.
    """
    try:
        # First check if the restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(product.restaurant_id)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")
            
        created_product = await ProductRepository.create_product(product)
        
        # Update cache
        await cache_product(created_product.id, created_product.model_dump())
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="create",
            target_type="product",
            target_id=created_product.id,
            details={
                "name": created_product.name,
                "restaurant_id": product.restaurant_id
            }
        )
        
        return created_product
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{product_id}", response_model=Dict)
async def admin_get_product(
    product_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Get details of a specific product. Only accessible by admins.
    """
    try:
        product = await ProductRepository.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{product_id}", response_model=Dict)
async def admin_update_product(
    product_id: str,
    product_data: ProductUpdate,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Update a product's details. Only accessible by admins.
    """
    try:
        # First check if product exists
        existing_product = await ProductRepository.get_product(product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Build update data dictionary
        update_data = {}
        if product_data.name is not None:
            update_data["name"] = product_data.name
        if product_data.description is not None:
            update_data["description"] = product_data.description
        if product_data.price is not None:
            update_data["price"] = product_data.price
        if product_data.img_url is not None:
            update_data["img_url"] = str(product_data.img_url)
        if product_data.ingredients is not None:
            update_data["ingredients"] = product_data.ingredients
            
        # Update product
        await ProductRepository.collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        
        # Get the updated product
        updated_product = await ProductRepository.get_product(product_id)
        
        # Update cache
        await cache_product(product_id, updated_product)
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="update",
            target_type="product",
            target_id=product_id,
            details={
                "updated_fields": list(update_data.keys()),
                "name": existing_product.get("name", ""),
                "restaurant_id": existing_product.get("restaurant_id", "")
            }
        )
        
        return updated_product
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.delete("/{product_id}", status_code=204)
async def admin_delete_product(
    product_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Delete a product permanently. Only accessible by admins.
    Note: This is different from disabling a product, which makes it unavailable but keeps it in the database.
    """
    try:
        # Check if product exists
        existing_product = await ProductRepository.get_product(product_id)
        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Save product info for logging
        product_name = existing_product.get("name", "")
        restaurant_id = existing_product.get("restaurant_id", "")
            
        # Delete the product
        result = await ProductRepository.collection.delete_one({"_id": ObjectId(product_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete product")
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="delete",
            target_type="product",
            target_id=product_id,
            details={
                "name": product_name,
                "restaurant_id": restaurant_id
            }
        )
            
        return None
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{product_id}/enable", status_code=200)
async def admin_enable_product(
    product_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Enable a product. Only accessible by admins.
    """
    try:
        # Find the product to get its restaurant_id
        product = await ProductRepository.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        restaurant_id = product.get("restaurant_id")
        product_name = product.get("name", "")
        
        # Enable the product
        result = await ProductRepository.enable_product(product_id, restaurant_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="enable",
            target_type="product",
            target_id=product_id,
            details={
                "name": product_name,
                "restaurant_id": restaurant_id
            }
        )
            
        return {"message": "Product enabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.put("/{product_id}/disable", status_code=200)
async def admin_disable_product(
    product_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Disable a product. Only accessible by admins.
    """
    try:
        # Find the product to get its restaurant_id
        product = await ProductRepository.get_product(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        restaurant_id = product.get("restaurant_id")
        product_name = product.get("name", "")
        
        # Disable the product
        result = await ProductRepository.disable_product(product_id, restaurant_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        
        # Log the operation
        await log_admin_operation(
            admin_id=current_admin.admin_id,
            admin_username=current_admin.username,
            operation="disable",
            target_type="product",
            target_id=product_id,
            details={
                "name": product_name,
                "restaurant_id": restaurant_id
            }
        )
            
        return {"message": "Product disabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error in admin product operation: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)