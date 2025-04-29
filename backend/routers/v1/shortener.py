from fastapi import APIRouter, HTTPException, status
import traceback
from bson import ObjectId
from typing import Dict, Any
import sys
import os
from pathlib import Path
from database.repositories.shortener import ShortenerRepository
from models.shortener import ShortCodeResponse

router = APIRouter(
    prefix="/shortener",
    tags=["Shortener"],
    responses={404: {"description": "Not found"}},
)



@router.get("/{short_code}", response_model=None)
async def decode_short_code(short_code: str):
    """
    Decode a base36 shortened code back to a MongoDB ObjectID.
    This endpoint doesn't require authentication.
    
    The short_code should be in the format "timestamp-counter" where both parts are base36 encoded.
    """
    try:
        # Parse the base36 encoded string and convert to binary values
        if not isinstance(short_code, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="short_code must be a string"
            )
        
        if '-' not in short_code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="short_code must be in the format 'timestamp-counter'"
            )
        
        # Get the ObjectId from the timestamp and counter
        try:
            object_id = await ShortenerRepository.get_object_id(short_code)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving ObjectId: {str(e)}"
            )
        
        if not object_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No matching ObjectId found for this code"
            )
        
        # Return the decoded ObjectId
        return {"object_id": str(object_id)}
        
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)