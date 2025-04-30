from fastapi import APIRouter, HTTPException, status
from database.repositories import ReviewRepository, RestaurantRepository
from models.review import Review
from pydantic import BaseModel
import traceback
import logging

router = APIRouter(
    prefix="/review",
    tags=["Review"],
    responses={404: {"description": "Not found"}}
)

class ReviewCreate(BaseModel):
    """Schema for creating a review"""
    restaurant_id: str
    rating: int

@router.post("/", response_model=Review, status_code=201)
async def create_review(review: ReviewCreate):
    """
    Create an anonymous review for a restaurant
    - rating must be between 1 and 5
    - review starts with 'pending' status
    - a cron job will process pending reviews and update restaurant ratings
    """
    try:
        # Validate rating
        if review.rating < 1 or review.rating > 5:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rating must be between 1 and 5"
            )
            
        # Check if restaurant exists
        restaurant = await RestaurantRepository.get_restaurant(review.restaurant_id)
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Restaurant not found"
            )
            
        # Create the review
        created_review = await ReviewRepository.create_review(
            restaurant_id=review.restaurant_id,
            rating=review.rating
        )
        
        return created_review
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error creating review: {str(e)}")
        logging.error(traceback.format_exc())
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)