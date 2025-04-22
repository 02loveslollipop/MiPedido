from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from bson import ObjectId

class UserBase(BaseModel):
    """Base model with common user attributes"""
    username: str = Field(..., description="Username for login")
    
class UserAuth(UserBase):
    """Model used for user authentication"""
    password: str = Field(..., description="Password for login")
    
class UserInDB(UserBase):
    """Model representing how user is stored in database"""
    id: str = Field(default=None, alias="_id")
    hashed_password: str = Field(..., description="Hashed password")
    controls: List[str] = Field(default_factory=list, description="List of restaurant IDs the user controls")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class User(UserBase):
    """Model returned to clients via API"""
    id: str = Field(..., description="Unique identifier of the user")
    controls: List[str] = Field(default_factory=list, description="List of restaurant IDs the user controls")
    
    model_config = ConfigDict(populate_by_name=True)

class Token(BaseModel):
    """Model for authentication token response"""
    access_token: str = Field(..., description="JWT access token")
    user_id: str = Field(..., description="User ID")
    
    model_config = ConfigDict(populate_by_name=True)