from pydantic import BaseModel, Field, HttpUrl

class RestaurantBase(BaseModel):
    """Base model with common restaurant attributes"""
    name: str
    img_url: HttpUrl = Field(..., description="URL to restaurant image")

class RestaurantCreate(RestaurantBase):
    """Model used for restaurant creation requests"""
    pass

class RestaurantInDB(RestaurantBase):
    """Model representing how restaurant is stored in database"""
    _id: str
    
    class Config:
        orm_mode = True
        populate_by_name = True

class Restaurant(RestaurantBase):
    """Model returned to clients via API"""
    id: str

    class Config:
        orm_mode = True
        populate_by_name = True
        
    @classmethod
    def from_db_model(cls, db_restaurant: RestaurantInDB) -> "Restaurant":
        """Convert from database model to API model"""
        return cls(
            id=db_restaurant._id,
            name=db_restaurant.name,
            img_url=db_restaurant.img_url
        )