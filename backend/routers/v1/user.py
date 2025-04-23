from fastapi import APIRouter, HTTPException, status
from models import UserAuth, Token
from database.repositories import UserRepository
import traceback

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