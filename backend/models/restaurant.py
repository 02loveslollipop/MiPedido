from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Any, Optional
from bson import ObjectId

class Position(BaseModel):
    """Position model with latitude and longitude coordinates"""
    lat: float
    lng: float

class RestaurantBase(BaseModel):
    """Base model with common restaurant attributes"""
    name: str
    img_url: HttpUrl = Field(..., description="URL to restaurant image")
    rating: Optional[float] = None
    type: Optional[str] = None
    description: Optional[str] = None
    position: Optional[Position] = None

class RestaurantCreate(RestaurantBase):
    """Model used for restaurant creation requests"""
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),  # Convert ObjectId to string for JSON serialization
            HttpUrl: lambda v: str(v)  # Convert HttpUrl to string for JSON serialization
        }
    pass

class RestaurantInDB(RestaurantBase):
    """Model representing how restaurant is stored in database"""
    id: str = Field(default=None, alias="_id")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Restaurant(RestaurantBase):
    """Model returned to clients via API"""
    id: str

    model_config = ConfigDict(populate_by_name=True)
        
    @classmethod
    def from_db_model(cls, db_restaurant: RestaurantInDB) -> "Restaurant":
        """Convert from database model to API model"""
        return cls(
            id=str(db_restaurant.id),
            name=db_restaurant.name,
            img_url=db_restaurant.img_url,
            rating=db_restaurant.rating,
            type=db_restaurant.type,
            description=db_restaurant.description,
            position=db_restaurant.position
        )