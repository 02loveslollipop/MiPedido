from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from pydantic import BaseModel
import os
import ssl
import certifi
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class DatabaseSettings(BaseModel):
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "mipedido")

class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    settings: DatabaseSettings = DatabaseSettings()
    
    def __init__(self):
        # Connect to the database right away
        self.connect_to_db()
    
    def connect_to_db(self) -> None:
        try:
            # Setup MongoDB connection options with proper TLS configuration
            connection_options = {
                "tlsCAFile": certifi.where(),  # Use certifi for trusted certificates
                "ssl": True,
                "ssl_cert_reqs": ssl.CERT_REQUIRED,
                "retryWrites": True,
                "serverSelectionTimeoutMS": 30000,  # 30 seconds timeout
                "connectTimeoutMS": 20000
            }
            
            # For local development without TLS, don't use the options
            if "localhost" in self.settings.mongodb_url or "127.0.0.1" in self.settings.mongodb_url:
                self.client = AsyncIOMotorClient(self.settings.mongodb_url)
            else:
                # For cloud deployments with MongoDB Atlas
                self.client = AsyncIOMotorClient(
                    self.settings.mongodb_url,
                    **connection_options
                )
                
            self.db = self.client[self.settings.database_name]
            print(f"Connected to MongoDB database: {self.settings.database_name}")
        except Exception as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
        
    def close_db_connection(self) -> None:
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

# Create a database instance to be used throughout the app
db = Database()