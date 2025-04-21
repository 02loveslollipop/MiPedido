from bson import ObjectId
from database import db
from models.order import OrderBase, UserOrder, OrderProduct
from typing import List

class OrderRepository:
    collection = db.db["orders"]
    
    async def create_order(restaurant_id: str) -> str: #returns the user
        order = {
            "restaurant_id": restaurant_id,
            "products": [],
            "status": "pending",
            "total_price": 0.0,
        }
        result = await OrderRepository.collection.insert_one(order)
        return str(result.inserted_id)