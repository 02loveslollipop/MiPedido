from bson import ObjectId
from database import db
from models.admin import Admin, AdminInDB, AdminToken
from typing import Optional, List
import jwt
import os
import datetime
import hashlib

# Secret key for JWT tokens - in production this should come from environment variables
SECRET_KEY = os.getenv("ADMIN_SECRET_KEY", "admin_secret_key_here")
ALGORITHM = "HS256"
TOKEN_EXPIRE_MINUTES = 60 * 12  # 12 hours

class AdminRepository:
    collection = db.db.db["admins"]
    
    @classmethod
    async def get_admin_by_username(cls, username: str) -> Optional[AdminInDB]:
        """
        Get an admin by username
        """
        document = await cls.collection.find_one({"username": username})
        if not document:
            return None
            
        admin = AdminInDB(
            id=str(document["_id"]),
            username=document["username"],
            hashed_password=document["hashed_password"]
        )
        return admin
    
    @classmethod
    async def get_admin_by_id(cls, admin_id: str) -> Optional[AdminInDB]:
        """
        Get an admin by ID
        """
        try:
            document = await cls.collection.find_one({"_id": ObjectId(admin_id)})
            if not document:
                return None
                
            admin = AdminInDB(
                id=str(document["_id"]),
                username=document["username"],
                hashed_password=document["hashed_password"]
            )
            return admin
        except Exception as e:
            print(f"Error getting admin by ID: {e}")
            return None
    
    @classmethod
    async def authenticate_admin(cls, username: str, password: str) -> Optional[AdminToken]:
        """
        Authenticate an admin and return a JWT token if successful
        """
        admin = await cls.get_admin_by_username(username)
        if not admin:
            return None
            
        # Verify password (simple hash for demonstration purposes)
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if hashed_password != admin.hashed_password:
            return None
            
        # Create access token
        expires_delta = datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
        expire = datetime.datetime.utcnow() + expires_delta
        
        # Create token payload
        payload = {
            "sub": admin.username,
            "id": admin.id,
            "exp": expire,
            "iat": datetime.datetime.utcnow(),
            "role": "admin"  # Add role to distinguish from regular users
        }
        
        # Create JWT token
        access_token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        return AdminToken(
            access_token=access_token,
            admin_id=admin.id
        )
    
    @classmethod
    async def create_admin(cls, username: str, password: str) -> Admin:
        """
        Create a new admin
        """
        # Check if username already exists
        existing_admin = await cls.get_admin_by_username(username)
        if existing_admin:
            raise ValueError(f"Admin with username {username} already exists")
            
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Create admin document
        admin_doc = {
            "username": username,
            "hashed_password": hashed_password
        }
        
        # Insert into database
        result = await cls.collection.insert_one(admin_doc)
        
        # Return the created admin
        return Admin(
            id=str(result.inserted_id),
            username=username
        )
    
    @classmethod
    async def list_admins(cls) -> List[Admin]:
        """
        List all admins
        """
        admins = []
        cursor = cls.collection.find({})
        async for document in cursor:
            admin = Admin(
                id=str(document["_id"]),
                username=document["username"]
            )
            admins.append(admin)
        return admins
    
    @classmethod
    async def delete_admin(cls, admin_id: str) -> bool:
        """
        Delete an admin
        """
        try:
            result = await cls.collection.delete_one({"_id": ObjectId(admin_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting admin: {e}")
            return False
    
    @classmethod
    async def update_admin_password(cls, admin_id: str, new_password: str) -> bool:
        """
        Update an admin's password
        """
        try:
            # Hash the password
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            
            result = await cls.collection.update_one(
                {"_id": ObjectId(admin_id)},
                {"$set": {"hashed_password": hashed_password}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating admin password: {e}")
            return False