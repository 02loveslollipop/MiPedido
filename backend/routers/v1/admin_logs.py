from fastapi import APIRouter, HTTPException, Depends, Query
from models.admin_log import AdminLog, AdminLogFilter
from database.repositories.admin_log_repository import AdminLogRepository
from utils.admin_auth import get_current_admin, AdminTokenData
import traceback
import logging
from typing import List, Dict
from datetime import datetime

router = APIRouter(
    prefix="/admin/logs",
    tags=["Admin Logs"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=Dict)
async def get_admin_logs(
    admin_id: str = None,
    admin_username: str = None,
    operation: str = None,
    target_type: str = None,
    target_id: str = None,
    from_date: datetime = None,
    to_date: datetime = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Get admin operation logs with optional filtering.
    
    Args:
        admin_id: Filter by admin ID
        admin_username: Filter by admin username
        operation: Filter by operation type (create, update, delete)
        target_type: Filter by target resource type (user, restaurant, product)
        target_id: Filter by target resource ID
        from_date: Filter logs from this date/time
        to_date: Filter logs until this date/time
        skip: Number of records to skip for pagination
        limit: Maximum number of records to return
        
    Returns:
        Dict containing logs and total count
    """
    try:
        # Create filter object
        filters = AdminLogFilter(
            admin_id=admin_id,
            admin_username=admin_username,
            operation=operation,
            target_type=target_type,
            target_id=target_id,
            from_date=from_date,
            to_date=to_date
        )
        
        # Get logs and total count
        logs = await AdminLogRepository.get_logs(
            filters=filters,
            skip=skip,
            limit=limit
        )
        
        total = await AdminLogRepository.count_logs(filters=filters)
        
        # Return logs and metadata
        return {
            "logs": logs,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    except Exception as e:
        logging.error(f"Error getting admin logs: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/{log_id}", response_model=AdminLog)
async def get_admin_log(
    log_id: str,
    current_admin: AdminTokenData = Depends(get_current_admin)
):
    """
    Get a specific admin log entry by ID
    
    Args:
        log_id: ID of the log entry
        
    Returns:
        Log entry details
    """
    try:
        log = await AdminLogRepository.get_log(log_id)
        
        if not log:
            raise HTTPException(status_code=404, detail="Log entry not found")
            
        return log
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting specific admin log: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n{traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)