from pydantic import BaseModel, Field, HttpUrl, optional
from bson import ObjectId
    
class OrderProduct(BaseModel):
    name: str = Field(..., description="Name of the product")
    price: float = Field(..., description="Price of the product")
    img_url: HttpUrl = Field(..., description="URL of the product image")
    quantity: int = Field(..., description="Quantity of the product in the order")
    ingredients : list[str] = Field(..., description="List of ingredients for the product")
    
class UserOrder(BaseModel):
    products: list[OrderProduct] = Field(..., description="List of products in the order")
    
class OrderBase(BaseModel):
    id: str = Field(..., description="Unique identifier for the order")
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: dict[str, UserOrder] = Field(..., description="Dictionary of users and their orders")
    
class OrderInDB(OrderBase):
    id: ObjectId = Field(default_factory=ObjectId, description="Unique identifier for the order in the database")
    
    class Config:
        json_encoders = {
            ObjectId: str
        }

class Order(OrderBase):
    id: str = Field(..., description="Unique identifier for the order")
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: dict[str, UserOrder] = Field(..., description="Dictionary of users and their orders")
    
    class Config:
        json_encoders = {
            ObjectId: str
        }
    
    @classmethod
    def from_db_model(cls, db_model: OrderInDB) -> "Order":
        return cls(
            id=str(db_model.id),
            restaurant_id=db_model.restaurant_id,
            users=db_model.users
        )


