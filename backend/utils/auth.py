from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
import os
from datetime import datetime, timedelta, timezone
import traceback
import json


# OAuth2 scheme for token extraction from requests
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/user/login")

# Secret key and algorithm settings
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"

class TokenData(BaseModel):
    """Data extracted from JWT token"""
    username: str
    user_id: str
    exp: datetime

class TokenRequest(BaseModel):
    """Request model for body-based token authentication"""
    access_token: str

def decode_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token
    Returns the token payload if valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}"
        )

async def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    """
    Dependency function to extract and validate user information from JWT token in header
    """
    try:
        payload = decode_jwt_token(token)
        
        # Extract user information
        username = payload.get("sub")
        user_id = payload.get("id")
        exp = datetime.fromtimestamp(payload.get("exp"))
        
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token contents"
            )
            
        # Check token expiration
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
            
        # Return user data
        return TokenData(username=username, user_id=user_id, exp=exp)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error validating token: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )

async def get_token_from_body(token_request: TokenRequest) -> TokenData:
    """
    Dependency function to extract and validate user information from JWT token in request body
    """
    try:
        payload = decode_jwt_token(token_request.access_token)
        
        # Extract user information
        username = payload.get("sub")
        user_id = payload.get("id")
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        
        if not username or not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token contents"
            )
            
        # Check token expiration
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
            
        # Return user data
        return TokenData(username=username, user_id=user_id, exp=exp)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error validating token: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )
