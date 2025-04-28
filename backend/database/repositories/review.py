from bson import ObjectId
from database import db
from models.review import Review
from typing import Dict, Any

class ReviewRepository:
    collection = db.db.db["reviews"]
    
    @classmethod
    async def create_review(cls, restaurant_id: str, rating: int) -> Review:
        """Create a new review"""
        review = Review(
            restaurant_id=restaurant_id,
            rating=rating
        )
        
        # Convert to dict for insertion
        review_dict = review.model_dump(by_alias=True)
        
        # Insert into database
        result = await cls.collection.insert_one(review_dict)
        
        # Return created review with ID
        review.id = result.inserted_id
        return review