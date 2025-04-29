from bson import ObjectId
from database import db
from models.admin import AdminBase, AdminInDB, Admin
from typing import List, Optional
import hashlib
from datetime import datetime, timedelta
from utils.admin_auth import create_admin_access_token

class AdminRepository:
    """Repository for admin user operations"""
    
    # Reference to the admins collection in the database
    collection = db.db.db["admin"]
    
    @classmethod
    async def create_admin(cls, username: str, password: str) -> Admin:
        """
        Create a new admin user
        
        Args:
            username: Admin username
            password: Plain text password
            
        Returns:
            The created admin user
            
        Raises:
            ValueError: If an admin with the same username already exists
        """
        # Check if admin already exists
        existing_admin = await cls.get_admin_by_username(username)
        if existing_admin:
            raise ValueError(f"Admin with username '{username}' already exists")
        
        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Create admin document
        admin_doc = {
            "username": username,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow(),
        }
        
        # Insert into database
        result = await cls.collection.insert_one(admin_doc)
        admin_id = str(result.inserted_id)
        
        # Return the created admin
        return Admin(id=admin_id, username=username)
    
    @classmethod
    async def authenticate_admin(cls, username: str, password: str) -> Optional[dict]:
        """
        Authenticate an admin user
        
        Args:
            username: Admin username
            password: Plain text password
            
        Returns:
            Dict with access token and admin ID if authentication succeeds, None otherwise
        """
        # Get admin from database
        admin = await cls.get_admin_by_username(username)
        if not admin:
            return None
        
        # Hash the password and compare
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if admin.hashed_password != hashed_password:
            return None
        
        # Create access token
        token_data = {
            "sub": admin.username,
            "id": admin.id,
            "role": "admin"  # Include role to distinguish from regular users
        }
        
        # Set token expiration (12 hours)
        expires_delta = timedelta(hours=12)
        access_token = create_admin_access_token(token_data, expires_delta)
        
        # Return token and admin ID
        return {
            "access_token": access_token,
            "admin_id": admin.id
        }
    
    @classmethod
    async def get_admin_by_username(cls, username: str) -> Optional[AdminInDB]:
        """
        Get admin by username
        
        Args:
            username: Admin username
            
        Returns:
            AdminInDB if found, None otherwise
        """

        admin_doc = await cls.collection.find_one({"username": username})
        
        if not admin_doc:
            return None
        
        return AdminInDB(
            id=str(admin_doc["_id"]),
            username=admin_doc["username"],
            hashed_password=admin_doc["hashed_password"]
        )
    
    @classmethod
    async def get_admin_by_id(cls, admin_id: str) -> Optional[AdminInDB]:
        """
        Get admin by ID
        
        Args:
            admin_id: Admin ID
            
        Returns:
            AdminInDB if found, None otherwise
        """
        try:
            admin_doc = await cls.collection.find_one({"_id": ObjectId(admin_id)})
            if not admin_doc:
                return None
            
            return AdminInDB(
                id=str(admin_doc["_id"]),
                username=admin_doc["username"],
                hashed_password=admin_doc["hashed_password"]
            )
        except Exception:
            return None
    
    @classmethod
    async def list_admins(cls) -> List[Admin]:
        """
        List all admins
        
        Returns:
            List of Admin objects
        """
        admins = []
        cursor = cls.collection.find({})
        
        async for admin_doc in cursor:
            admin = Admin(
                id=str(admin_doc["_id"]),
                username=admin_doc["username"]
            )
            admins.append(admin)
            
        return admins
    
    @classmethod
    async def update_admin(cls, admin_id: str, update_data: dict) -> bool:
        """
        Update admin fields
        
        Args:
            admin_id: Admin ID
            update_data: Dict of fields to update
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            # Handle password separately if included
            if "password" in update_data:
                # Hash the new password
                update_data["hashed_password"] = hashlib.sha256(
                    update_data.pop("password").encode()
                ).hexdigest()
            
            # Update the admin document
            result = await cls.collection.update_one(
                {"_id": ObjectId(admin_id)},
                {"$set": update_data}
            )
            
            return result.modified_count > 0
        except Exception:
            return False
    
    @classmethod
    async def delete_admin(cls, admin_id: str) -> bool:
        """
        Delete an admin
        
        Args:
            admin_id: Admin ID
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            result = await cls.collection.delete_one({"_id": ObjectId(admin_id)})
            return result.deleted_count > 0
        except Exception:
            return False