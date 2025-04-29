from bson import ObjectId
from database import db
from models.admin_log import AdminLogCreate, AdminLogInDB, AdminLog, AdminLogFilter
from typing import List, Optional
from datetime import datetime
import traceback

class AdminLogRepository:
    """Repository for admin log operations"""
    
    # Reference to the admin_log collection in the database
    collection = db.db.db["admin_log"]
    
    @classmethod
    async def create_log(cls, log_data: AdminLogCreate) -> AdminLog:
        """
        Create a new admin log entry
        
        Args:
            log_data: Log entry data
            
        Returns:
            Created log entry
        """
        try:
            # Insert document into collection
            result = await cls.collection.insert_one(log_data.model_dump())
            
            # Return created log with ID
            return AdminLog(
                id=str(result.inserted_id),
                **log_data.model_dump()
            )
        except Exception as e:
            # If logging fails, we don't want to break the application
            # Just print the error and continue
            print(f"Error creating admin log: {e}")
            print(traceback.format_exc())
            return None
    
    @classmethod
    async def get_logs(cls, filters: Optional[AdminLogFilter] = None, 
                      skip: int = 0, limit: int = 100) -> List[AdminLog]:
        """
        Get admin logs with optional filtering
        
        Args:
            filters: Optional filters to apply
            skip: Number of records to skip (for pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of matching log entries
        """
        try:
            # Build query from filters
            query = {}
            
            if filters:
                if filters.admin_id:
                    query["admin_id"] = filters.admin_id
                
                if filters.admin_username:
                    query["admin_username"] = filters.admin_username
                
                if filters.operation:
                    query["operation"] = filters.operation
                
                if filters.target_type:
                    query["target_type"] = filters.target_type
                
                if filters.target_id:
                    query["target_id"] = filters.target_id
                
                # Date range filtering
                date_query = {}
                if filters.from_date:
                    date_query["$gte"] = filters.from_date
                
                if filters.to_date:
                    date_query["$lte"] = filters.to_date
                
                if date_query:
                    query["timestamp"] = date_query
            
            # Execute query
            cursor = cls.collection.find(query).sort("timestamp", -1).skip(skip).limit(limit)
            
            # Convert results to AdminLog objects
            logs = []
            async for document in cursor:
                logs.append(AdminLog(
                    id=str(document["_id"]),
                    admin_id=document["admin_id"],
                    admin_username=document["admin_username"],
                    operation=document["operation"],
                    target_type=document["target_type"],
                    target_id=document["target_id"],
                    details=document.get("details"),
                    timestamp=document["timestamp"]
                ))
            
            return logs
        except Exception as e:
            print(f"Error getting admin logs: {e}")
            print(traceback.format_exc())
            return []
    
    @classmethod
    async def get_log(cls, log_id: str) -> Optional[AdminLog]:
        """
        Get a specific log entry by ID
        
        Args:
            log_id: ID of the log entry
            
        Returns:
            Log entry if found, None otherwise
        """
        try:
            document = await cls.collection.find_one({"_id": ObjectId(log_id)})
            if not document:
                return None
            
            return AdminLog(
                id=str(document["_id"]),
                admin_id=document["admin_id"],
                admin_username=document["admin_username"],
                operation=document["operation"],
                target_type=document["target_type"],
                target_id=document["target_id"],
                details=document.get("details"),
                timestamp=document["timestamp"]
            )
        except Exception as e:
            print(f"Error getting admin log: {e}")
            print(traceback.format_exc())
            return None
    
    @classmethod
    async def count_logs(cls, filters: Optional[AdminLogFilter] = None) -> int:
        """
        Count admin logs with optional filtering
        
        Args:
            filters: Optional filters to apply
            
        Returns:
            Number of matching log entries
        """
        try:
            # Build query from filters
            query = {}
            
            if filters:
                if filters.admin_id:
                    query["admin_id"] = filters.admin_id
                
                if filters.admin_username:
                    query["admin_username"] = filters.admin_username
                
                if filters.operation:
                    query["operation"] = filters.operation
                
                if filters.target_type:
                    query["target_type"] = filters.target_type
                
                if filters.target_id:
                    query["target_id"] = filters.target_id
                
                # Date range filtering
                date_query = {}
                if filters.from_date:
                    date_query["$gte"] = filters.from_date
                
                if filters.to_date:
                    date_query["$lte"] = filters.to_date
                
                if date_query:
                    query["timestamp"] = date_query
            
            # Count matching documents
            return await cls.collection.count_documents(query)
        except Exception as e:
            print(f"Error counting admin logs: {e}")
            print(traceback.format_exc())
            return 0