from bson import ObjectId
from database import db
from models.restaurant import Restaurant, RestaurantCreate, RestaurantInDB
from typing import List

class RestaurantRepository:
    collection = db.db.db["restaurants"]
    
    @classmethod
    async def list_restaurants(cls) -> List[Restaurant]:
        restaurants = []
        cursor = cls.collection.find({}) # Get all restaurants
        async for document in cursor:
            restaurant = Restaurant(
                id=str(document["_id"]),
                name=document["name"],
                img_url=document["img_url"]
            )
            restaurants.append(restaurant)
        return restaurants

    @classmethod
    async def create_restaurant(cls, restaurant: RestaurantCreate) -> Restaurant:
        restaurant_dict = restaurant.model_dump()
        
        
        # Create document for insertion
        db_restaurant = restaurant_dict.copy()
        db_restaurant["img_url"] = str(db_restaurant["img_url"])
        
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
                
            return Restaurant(
                id=str(document["_id"]),
                name=document["name"],
                img_url=document["img_url"]
            )
        except:
            return None