from bson import ObjectId
from database import db
from models.user import User, UserInDB, Token
from typing import Optional, List
import jwt
import os
import datetime
import hashlib

# Secret key for JWT tokens - in production this should come from environment variables
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key_here")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 24  # 24 hours

class UserRepository:
    collection = db.db.db["users"]
    
    @classmethod
    async def get_user_by_username(cls, username: str) -> Optional[UserInDB]:
        """
        Get a user by username
        """
        document = await cls.collection.find_one({"username": username})
        if not document:
            return None
            
        user = UserInDB(
            id=str(document["_id"]),
            username=document["username"],
            hashed_password=document["hashed_password"],
            controls=document.get("controls", [])
        )
        return user
    
    @classmethod
    async def get_user_by_id(cls, user_id: str) -> Optional[UserInDB]:
        """
        Get a user by ID
        """
        try:
            document = await cls.collection.find_one({"_id": ObjectId(user_id)})
            if not document:
                return None
                
            user = UserInDB(
                id=str(document["_id"]),
                username=document["username"],
                hashed_password=document["hashed_password"],
                controls=document.get("controls", [])
            )
            return user
        except Exception as e:
            print(f"Error getting user by ID: {e}")
            return None
    
    @classmethod
    async def authenticate_user(cls, username: str, password: str) -> Optional[Token]:
        """
        Authenticate a user and return a JWT token if successful
        """
        user = await cls.get_user_by_username(username)
        if not user:
            return None
            
        # Verify password (simple hash for demonstration purposes)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_password != user.hashed_password:
            return None
            
        # Create access token
        expires_delta = datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        expire = datetime.datetime.utcnow() + expires_delta
        
        # Create token payload
        payload = {
            "sub": user.username,
            "id": user.id,
            "exp": expire,
            "iat": datetime.datetime.utcnow()
        }
        
        # Create JWT token
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return Token(
            access_token=access_token,
            user_id=user.id
        )
    
    @classmethod
    async def create_user(cls, username: str, password: str, controls: List[str] = None) -> User:
        """
        Create a new user
        """
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Create user document
        user_doc = {
            "username": username,
            "hashed_password": hashed_password,
            "controls": controls or []
        }
        
        # Insert into database
        result = await cls.collection.insert_one(user_doc)
        
        # Return the created user
        return User(
            id=str(result.inserted_id),
            username=username,
            controls=controls or []
        )
        
    @classmethod
    async def user_controls_restaurant(cls, user_id: str, restaurant_id: str) -> bool:
        """
        Check if a user controls a specific restaurant
        """
        user = await cls.get_user_by_id(user_id)
        if not user:
            return False
        
        return restaurant_id in user.controls