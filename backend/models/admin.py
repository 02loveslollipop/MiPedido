from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime

class AdminBase(BaseModel):
    """Base admin model with common fields"""
    username: str = Field(..., description="Username for admin login")

class AdminAuth(AdminBase):
    """Admin authentication model"""
    password: str = Field(..., description="Password for admin login")

class AdminInDB(AdminBase):
    """Admin model as stored in the database"""
    id: str = Field(default=None, alias="_id")
    hashed_password: str = Field(..., description="Hashed password")
    created_at: Optional[datetime] = None
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Admin(AdminBase):
    """Public admin model returned from API"""
    id: str
    
    model_config = ConfigDict(
        populate_by_name=True
    )

class AdminToken(BaseModel):
    """Response model for admin authentication"""
    access_token: str
    admin_id: str
    
    model_config = ConfigDict(
        populate_by_name=True
    )

class AdminUpdate(BaseModel):
    """Model for updating admin data"""
    username: Optional[str] = None
    password: Optional[str] = None
    
    model_config = ConfigDict(
        populate_by_name=True
    )