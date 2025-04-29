from models.admin_log import AdminLogCreate
from database.repositories.admin_log_repository import AdminLogRepository
from typing import Optional, Any
import asyncio

async def log_admin_operation(
    admin_id: str,
    admin_username: str,
    operation: str,
    target_type: str,
    target_id: str,
    details: Optional[dict] = None
) -> None:
    """
    Log an admin operation to the admin_log collection.
    
    This utility function creates an audit log entry for admin operations.
    It's designed to be non-blocking and fault-tolerant - if logging fails,
    the error is logged but the main operation continues.
    
    Args:
        admin_id: ID of the admin performing the operation
        admin_username: Username of the admin performing the operation
        operation: Type of operation (create, update, delete, etc.)
        target_type: Type of resource targeted (user, restaurant, product, etc.)
        target_id: ID of the resource targeted
        details: Optional additional details about the operation
    """
    # Create log entry
    log_data = AdminLogCreate(
        admin_id=admin_id,
        admin_username=admin_username,
        operation=operation,
        target_type=target_type,
        target_id=target_id,
        details=details
    )
    
    # Run logging in background to avoid blocking the main operation
    # If logging fails, the main operation will still succeed
    asyncio.create_task(AdminLogRepository.create_log(log_data))