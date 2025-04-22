from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
from pydantic import BaseModel
import os
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
        self.client = AsyncIOMotorClient(self.settings.mongodb_url)
        self.db = self.client[self.settings.database_name]
        print(f"Connected to MongoDB database: {self.settings.database_name}")
        
    def close_db_connection(self) -> None:
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

# Create a database instance to be used throughout the app
db = Database()