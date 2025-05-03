from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional, Dict, Any
import jwt
import os
from datetime import datetime, timedelta, timezone
import traceback
import json

# OAuth2 scheme for admin token extraction from requests
# Using a different URL endpoint than the user login
oauth2_admin_scheme = OAuth2PasswordBearer(tokenUrl="/v1/admin/login", scheme_name="admin")

# Admin-specific secret key and algorithm settings
# Using a different secret key for admin tokens to separate the auth systems
ADMIN_PUBLIC_KEY = os.getenv("ADMIN_PUBLIC_KEY", None)
ADMIN_PRIVATE_KEY = os.getenv("ADMIN_PRIVATE_KEY", None)
ALGORITHM = "RS256"

if ADMIN_PRIVATE_KEY and "\\n" in ADMIN_PRIVATE_KEY:
    ADMIN_PRIVATE_KEY = ADMIN_PRIVATE_KEY.replace("\\n", "\n")
    
if ADMIN_PUBLIC_KEY and "\\n" in ADMIN_PUBLIC_KEY:
    ADMIN_PUBLIC_KEY = ADMIN_PUBLIC_KEY.replace("\\n", "\n")

class AdminTokenData(BaseModel):
    """Data extracted from JWT token for admin users"""
    username: str
    admin_id: str
    exp: datetime
    role: str = "admin"  # Explicit role for admin users

class AdminTokenRequest(BaseModel):
    """Request model for body-based admin token authentication"""
    access_token: str

def decode_admin_jwt_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate an admin JWT token using RS256
    Returns the token payload if valid
    """
    try:
        if ADMIN_PUBLIC_KEY is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Admin public key not configured for RS256."
            )
        payload = jwt.decode(token, ADMIN_PUBLIC_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid admin authentication credentials: {str(e)}"
        )

async def get_current_admin(token: str = Depends(oauth2_admin_scheme)) -> AdminTokenData:
    """
    Dependency function to extract and validate admin information from JWT token in header
    """
    try:
        payload = decode_admin_jwt_token(token)
        
        # Extract admin information
        username = payload.get("sub")
        admin_id = payload.get("id")
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        role = payload.get("role")
        
        # Validate admin-specific fields
        if not username or not admin_id or role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token contents"
            )
            
        # Check token expiration
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin token has expired"
            )
            
        # Return admin data
        return AdminTokenData(username=username, admin_id=admin_id, exp=exp, role=role)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error validating admin token: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )

async def get_admin_token_from_body(token_request: AdminTokenRequest) -> AdminTokenData:
    """
    Dependency function to extract and validate admin information from JWT token in request body
    """
    try:
        payload = decode_admin_jwt_token(token_request.access_token)
        
        # Extract admin information
        username = payload.get("sub")
        admin_id = payload.get("id")
        exp = datetime.fromtimestamp(payload.get("exp"), tz=timezone.utc)
        role = payload.get("role")
        
        # Validate admin-specific fields
        if not username or not admin_id or role != "admin":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid admin token contents"
            )
            
        # Check token expiration
        if datetime.now(timezone.utc) > exp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin token has expired"
            )
            
        # Return admin data
        return AdminTokenData(username=username, admin_id=admin_id, exp=exp, role=role)
    except HTTPException:
        raise
    except Exception as e:
        error_detail = f"Error validating admin token: {str(e)}\n Stack trace: {traceback.format_exc()}"
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_detail
        )

def create_admin_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT token for admin authentication using RS256
    """
    to_encode = data.copy()
    
    # Set expiration time
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        # Default expiration of 12 hours
        expire = datetime.now(timezone.utc) + timedelta(hours=12)
        
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    
    if ADMIN_PRIVATE_KEY is None:
        raise Exception("Admin private key not configured for RS256.")
    
    # Create and return the token
    encoded_jwt = jwt.encode(to_encode, ADMIN_PRIVATE_KEY, algorithm=ALGORITHM)
    return encoded_jwt