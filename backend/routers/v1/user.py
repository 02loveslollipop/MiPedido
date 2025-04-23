from fastapi import APIRouter, HTTPException, status, Depends
from models import UserAuth, Token
from database.repositories import UserRepository
import traceback
from utils.auth import get_current_user, TokenData

router = APIRouter(
    prefix="/user",
    tags=["User"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=Token)
async def login(user_auth: UserAuth):
    """
    Sign in to the server. Returns an access token and the user id.
    If the user does not exist, it returns an error.
    """
    try:
        token = await UserRepository.authenticate_user(
            username=user_auth.username,
            password=user_auth.password
        )
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
            
        return token
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)

@router.get("/restaurant", response_model=dict)
async def get_user_restaurant(current_user: TokenData = Depends(get_current_user)):
    """
    Get the primary restaurant ID associated with the authenticated user.
    This endpoint requires authentication and returns only one restaurant ID.
    """
    try:
        user = await UserRepository.get_user_by_id(current_user.user_id)
        
        if not user or not user.controls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No restaurant found for this user"
            )
            
        # Return only the first restaurant ID from the user's controls
        return {"restaurant_id": user.controls[0]}
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(status_code=500, detail=error_detail)