from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import List, Optional
from bson import ObjectId

class ProductBase(BaseModel):
    """Base model with common product attributes"""
    name: str = Field(..., description="Name of the product")
    description: str = Field(..., description="Description of the product")
    price: float = Field(..., description="Price of the product")
    img_url: HttpUrl = Field(..., description="URL to product image")
    ingredients: List[str] = Field(default_factory=list, description="List of available ingredients for the product")

class ProductCreate(ProductBase):
    """Model used for product creation requests"""
    restaurant_id: str = Field(..., description="ID of the restaurant that offers this product")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class ProductInDB(ProductBase):
    """Model representing how product is stored in database"""
    id: str = Field(default=None, alias="_id")
    restaurant_id: str = Field(..., description="ID of the restaurant that offers this product")
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

class Product(ProductBase):
    """Model returned to clients via API"""
    id: str = Field(..., description="Unique identifier of the product")
    
    model_config = ConfigDict(
        populate_by_name=True
    )
    
    @classmethod
    def from_db_model(cls, db_product: ProductInDB) -> "Product":
        """Convert from database model to API model"""
        return cls(
            id=str(db_product.id),
            name=db_product.name,
            description=db_product.description,
            price=db_product.price,
            img_url=db_product.img_url,
            ingredients=db_product.ingredients
        )
        
class ProductUpdate(BaseModel):
    """Schema for updating product details"""
    name: str | None = None
    description: str | None = None
    price: float | None = None
    img_url: HttpUrl | None = None
    ingredients: List[str] | None = None
