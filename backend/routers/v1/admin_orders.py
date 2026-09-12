from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
import traceback
import logging

from database.repositories import OrderRepository 
from utils.admin_auth import get_current_admin, AdminTokenData
from utils.admin_logger import log_admin_operation

router = APIRouter(
    prefix="/admin/orders",
    tags=["Admin Orders"],
    responses={404: {"description": "Not found"}},
)

@router.get(
    "/",
    response_model=List[Dict[str, str]],
    responses={
        500: {"description": "Internal server error"}
    }
)
async def get_orders(
    skip: int = 0,
    limit: int = 100,
    order_repository: OrderRepository = Depends(),
    current_admin: AdminTokenData = Depends(get_current_admin),
):
    try:
        orders = await order_repository.get_all_orders(skip=skip, limit=limit)
        return orders
    except HTTPException:
        raise
    except Exception as e:
        logging.exception("Error in admin order operation: %s", e)
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)