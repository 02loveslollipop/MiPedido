from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal, Annotated
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema, handler):
        return {"type": "string"}

class Review(BaseModel):
    """
    Model for anonymous restaurant reviews
    """
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    restaurant_id: str
    rating: int  # Rating between 1 and 5 stars
    status: Literal["pending", "processed"] = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "restaurant_id": "60d4b3e7c9e9f3f5c8a1b2c3",
                "rating": 4,
                "status": "pending",
                "created_at": "2023-01-01T12:00:00.000Z"
            }
        }
    )