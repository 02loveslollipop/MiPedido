from pydantic import BaseModel, Field, HttpUrl, optional
from bson import ObjectId
    
class OrderProduct(BaseModel):
    name: str = Field(..., description="Name of the product")
    price: float = Field(..., description="Price of the product")
    img_url: HttpUrl = Field(..., description="URL of the product image")
    quantity: int = Field(..., description="Quantity of the product in the order")
    ingredients : list[str] = Field(..., description="List of ingredients for the product")
    
class OrderItemUpdate(BaseModel):
    """Model for updating an item in an order"""
    product_id: str = Field(..., description="Unique identifier of the product")
    quantity: int = Field(..., description="Quantity of the product in the order")
    ingredients: list[str] = Field(default_factory=list, description="List of selected ingredients for the product")
    
class UserOrder(BaseModel):
    products: list[OrderProduct] = Field(..., description="List of products in the order")
    
class OrderBase(BaseModel):
    id: str = Field(..., description="Unique identifier for the order")
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: dict[str, UserOrder] = Field(..., description="Dictionary of users and their orders")

class OrderInDBCreate(OrderBase):
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: dict[ObjectId, UserOrder] = Field(..., description="Dictionary of users and their orders")
    
    class Config:
        json_encoders = {
            ObjectId: str
        }
    
    @classmethod
    def from_model(cls, model: OrderBase) -> "OrderInDBCreate":
        return cls(
            restaurant_id=model.restaurant_id,
            users={ObjectId(user_id): user_order for user_id, user_order in model.users.items()}
        )

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


class OrderCreatedResponse(BaseModel):
    order_id: str = Field(..., description="Unique identifier for the created order")
    user_id: str = Field(..., description="Unique identifier for the user who created the order")
