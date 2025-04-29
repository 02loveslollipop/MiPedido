from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any
from datetime import datetime

class AdminLogBase(BaseModel):
    """Base model for admin operation logs"""
    admin_id: str = Field(..., description="ID of the admin who performed the operation")
    admin_username: str = Field(..., description="Username of the admin who performed the operation")
    operation: str = Field(..., description="Type of operation performed (create, update, delete, etc.)")
    target_type: str = Field(..., description="Type of resource that was targeted (user, restaurant, product, etc.)")
    target_id: str = Field(..., description="ID of the resource that was targeted")
    details: Optional[dict] = Field(default=None, description="Additional details about the operation")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="When the operation was performed")

class AdminLogCreate(AdminLogBase):
    """Model for creating admin log entries"""
    pass

class AdminLogInDB(AdminLogBase):
    """Model for admin log entries stored in the database"""
    id: str = Field(default=None, alias="_id", description="Unique identifier of the log entry")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class AdminLog(AdminLogBase):
    """Model for admin log entries returned from API"""
    id: str = Field(..., description="Unique identifier of the log entry")
    
    model_config = ConfigDict(
        populate_by_name=True
    )

class AdminLogFilter(BaseModel):
    """Model for filtering admin logs"""
    admin_id: Optional[str] = None
    admin_username: Optional[str] = None
    operation: Optional[str] = None
    target_type: Optional[str] = None
    target_id: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None