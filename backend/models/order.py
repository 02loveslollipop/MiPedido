from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List, Dict, Any
from bson import ObjectId
from datetime import datetime

# Define OrderProduct first
class OrderProduct(BaseModel):
    id: str = Field(default=None, description="ID of the product")
    name: str = Field(..., description="Name of the product")
    price: float = Field(..., description="Price of the product")
    img_url: HttpUrl = Field(..., description="URL of the product image")
    quantity: int = Field(..., description="Quantity of the product in the order")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients for the product")
    
    model_config = ConfigDict(populate_by_name=True)
    
class OrderItemUpdate(BaseModel):
    """Model for updating an item in an order"""
    product_id: str = Field(..., description="Unique identifier of the product")
    quantity: int = Field(..., description="Quantity of the product in the order")
    ingredients: List[str] = Field(default_factory=list, description="List of selected ingredients for the product")

# Request models
class CreateOrderRequest(BaseModel):
    """Request model for creating an order"""
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")

# Response models
class JoinOrderResponse(BaseModel):
    """Response model for joining an order"""
    user_id: str = Field(..., description="Unique identifier for the user who joined the order")
    
class OrderStatusResponse(BaseModel):
    """Response model for order modification status"""
    status: str = Field(..., description="Status of the operation (Created, Updated, or Deleted)")

class FinalOrderProduct(BaseModel):
    """Product in a finalized order with total price calculation"""
    id: str = Field(..., description="ID of the product")
    name: str = Field(..., description="Name of the product")
    price_per_unit: float = Field(..., description="Price per unit of the product")
    total_price: float = Field(..., description="Total price for this product (quantity * price)")
    img_url: HttpUrl = Field(..., description="URL of the product image")
    quantity: int = Field(..., description="Total quantity of the product")
    ingredients: List[str] = Field(default_factory=list, description="List of ingredients for the product")
    
    model_config = ConfigDict(populate_by_name=True)

class OrderCompletedResponse(BaseModel):
    """Response model for completed orders"""
    products: List[FinalOrderProduct] = Field(..., description="List of products in the final order")
    total_price: float = Field(..., description="Total price of the order")
    total_quantity: int = Field(..., description="Total quantity of products")
    date_completed: datetime = Field(..., description="Date and time when the order was completed")
    
class UserOrder(BaseModel):
    products: List[OrderProduct] = Field(default_factory=list, description="List of products in the order")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)
    
class OrderBase(BaseModel):
    id: Optional[str] = Field(default=None, description="Unique identifier for the order")
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: Dict[str, UserOrder] = Field(default_factory=dict, description="Dictionary of users and their orders")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class OrderInDBCreate(BaseModel):
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: Dict[str, UserOrder] = Field(default_factory=dict, description="Dictionary of users and their orders")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class OrderInDB(BaseModel):
    id: str = Field(..., description="Unique identifier for the order in the database")
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: Dict[str, UserOrder] = Field(default_factory=dict, description="Dictionary of users and their orders")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class Order(BaseModel):
    id: str = Field(..., description="Unique identifier for the order")
    restaurant_id: str = Field(..., description="Unique identifier for the restaurant")
    users: Dict[str, UserOrder] = Field(default_factory=dict, description="Dictionary of users and their orders")
    
    model_config = ConfigDict(arbitrary_types_allowed=True)

class OrderCreatedResponse(BaseModel):
    order_id: str = Field(..., description="Unique identifier for the created order")
    user_id: str = Field(..., description="Unique identifier for the user who created the order")
