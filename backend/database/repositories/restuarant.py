from bson import ObjectId
from database import db
from models.restaurant import Restaurant, RestaurantCreate, RestaurantInDB, Position
from typing import List

class RestaurantRepository:
    collection = db.db.db["restaurants"]
    
    @classmethod
    async def list_restaurants(cls) -> List[Restaurant]:
        restaurants = []
        cursor = cls.collection.find({}) # Get all restaurants
        async for document in cursor:
            # Create optional Position object if position data exists
            position = None
            if "position" in document and document["position"]:
                position = Position(
                    lat=document["position"]["lat"],
                    lng=document["position"]["lng"]
                )
            
            restaurant = Restaurant(
                id=str(document["_id"]),
                name=document["name"],
                img_url=document["img_url"],
                rating=document.get("rating"),
                type=document.get("type"),
                description=document.get("description"),
                position=position
            )
            restaurants.append(restaurant)
        return restaurants

    @classmethod
    async def create_restaurant(cls, restaurant: RestaurantCreate) -> Restaurant:
        restaurant_dict = restaurant.model_dump()
        
        # Create document for insertion
        db_restaurant = restaurant_dict.copy()
        db_restaurant["img_url"] = str(db_restaurant["img_url"])
        db_restaurant["rating"] = 0 # Default rating
        db_restaurant["type"] = db_restaurant.get("type", "restaurant")
        db_restaurant["_review_count"] = 0
        
        # Handle position separately if it exists
        if db_restaurant.get("position"):
            db_restaurant["position"] = db_restaurant["position"].model_dump()
        
        # Insert into database
        result = await cls.collection.insert_one(db_restaurant)
        
        # Return the created restaurant with ID
        return Restaurant(
            id=str(result.inserted_id),
            **restaurant_dict
        )
        
    @classmethod
    async def get_restaurant(cls, restaurant_id: str) -> Restaurant | None:
        try:
            document = await cls.collection.find_one({"_id": ObjectId(restaurant_id)})
            if not document:
                return None
            
            # Create optional Position object if position data exists
            position = None
            if "position" in document and document["position"]:
                position = Position(
                    lat=document["position"]["lat"],
                    lng=document["position"]["lng"]
                )
                
            return Restaurant(
                id=str(document["_id"]),
                name=document["name"],
                img_url=document["img_url"],
                rating=document.get("rating"),
                type=document.get("type"),
                description=document.get("description"),
                position=position
            )
        except:
            return None