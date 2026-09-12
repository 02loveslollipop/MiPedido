from bson import ObjectId
from database import db
from models.order import OrderBase, UserOrder, OrderProduct, OrderInDBCreate, OrderCreatedResponse, JoinOrderResponse, FinalOrderProduct, OrderCompletedResponse
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from fastapi import HTTPException

ORDER_NOT_FOUND = "Order not found"

class OrderRepository:
    collection = db.db.db["orders"]
    
    @classmethod
    async def create_order(cls, restaurant_id: str) -> OrderCreatedResponse:
        """
        Creates an empty order in a restaurant and returns the order id and the user id
        """
        try:
            # Create new user ID
            new_user_id = str(ObjectId())
            
            # Create order document
            order_document = {
                "restaurant_id": restaurant_id,
                "users": {
                    new_user_id: {
                        "products": []
                    }
                }
            }
            
            # Insert into database
            result = await cls.collection.insert_one(order_document)
            
            # Create response
            response = OrderCreatedResponse(
                order_id=str(result.inserted_id),
                user_id=new_user_id
            )
            
            return response
        except Exception as e:
            raise e
    
    @classmethod
    async def join_order(cls, order_id: str) -> Optional[Dict[str, str]]:
        """
        Adds a user to an existing order. Returns the user id and restaurant id.
        """
        try:
            # Verify order exists and handle possible invalid ObjectId
            try:
                order_obj_id = ObjectId(order_id)
            except Exception as e:
                # If the order_id is not a valid ObjectId, return None
                print(f"Invalid ObjectId format: {order_id}")
                raise e
                
            order = await cls.collection.find_one({"_id": order_obj_id})
            if not order:
                return None
            
            # Create new user ID
            new_user_id = str(ObjectId())
            
            # Update order with new user
            update_result = await cls.collection.update_one(
                {"_id": order_obj_id},
                {"$set": {f"users.{new_user_id}": {"products": []}}}
            )
            
            if update_result.modified_count == 0:
                return None
                
            return {"user_id": new_user_id, "restaurant_id": order["restaurant_id"]}
        except Exception as e:
            raise e
    
    @classmethod
    async def _get_and_validate_product(cls, product_id: str, ingredients: list[str]) -> Dict[str, Any]:
        """Validates that a product exists and any requested ingredients are valid."""
        product_collection = db.db.db["products"]
        product = await product_collection.find_one({
            "_id": ObjectId(product_id),
            "$or": [
                {"active": True},
                {"active": {"$exists": False}}
            ]
        })
        
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        if ingredients:
            valid_ingredients = set(product.get("ingredients", []))
            for ingredient in ingredients:
                if ingredient not in valid_ingredients:
                    raise HTTPException(status_code=400, detail=f"Invalid ingredient: {ingredient}")
        return product

    @classmethod
    async def _apply_order_modification(
        cls,
        order_id: str,
        user_oid: ObjectId,
        order: Dict[str, Any],
        product_id: str,
        product: Dict[str, Any],
        quantity: int,
        ingredients: list[str]
    ) -> Dict[str, str]:
        """Updates or deletes user products within an order."""
        user_products = order["users"][str(user_oid)]["products"]
        existing_product_index = next(
            (idx for idx, p in enumerate(user_products) if p.get("id") == product_id),
            None
        )
        
        if quantity == 0:
            if existing_product_index is not None:
                user_products.pop(existing_product_index)
                await cls.collection.update_one(
                    {"_id": ObjectId(order_id)},
                    {"$set": {f"users.{str(user_oid)}.products": user_products}}
                )
                return {"status": "success", "message": "Deleted"}
            return {"status": "success", "message": "Nothing to delete"}
        
        product_data = {
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "img_url": product["img_url"],
            "quantity": quantity,
            "ingredients": ingredients or []
        }
        
        if existing_product_index is not None:
            user_products[existing_product_index] = product_data
            await cls.collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {f"users.{str(user_oid)}.products": user_products}}
            )
            return {"status": "success", "message": "Updated"}
        
        user_products.append(product_data)
        await cls.collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {f"users.{str(user_oid)}.products": user_products}}
        )
        return {"status": "success", "message": "Created"}

    @classmethod
    async def modify_order(cls, order_id: str, user_id: str, product_id: str, quantity: int, ingredients: list[str]) -> Dict[str, str]:
        """
        Modifies an order for a specific user.
        Returns a status dictionary with a status and message.
        """
        try:
            # Get the order from the database
            order = await cls.collection.find_one({"_id": ObjectId(order_id)})
            if not order:
                raise HTTPException(status_code=404, detail=ORDER_NOT_FOUND)
            
            # Check if the user exists in the order
            user_oid = ObjectId(user_id)
            if str(user_oid) not in order["users"]:
                raise HTTPException(status_code=404, detail="User not found in order")
            
            product = await cls._get_and_validate_product(product_id, ingredients)
            return await cls._apply_order_modification(order_id, user_oid, order, product_id, product, quantity, ingredients)
        except Exception as e:
            raise e
    
    @classmethod
    async def get_user_order(cls, order_id: str, user_id: str) -> Dict[str, Any]:
        """
        Returns the order products for a specific user
        """
        try:
            # Check if the order exists
            try:
                order_obj_id = ObjectId(order_id)
            except Exception as e:
                raise e
                
            order = await cls.collection.find_one({"_id": order_obj_id})
            if not order:
                raise HTTPException(status_code=404, detail=ORDER_NOT_FOUND)
            
            # Check if the user exists in the order
            if user_id not in order["users"]:
                raise HTTPException(status_code=404, detail="User not found in order")
            
            # Return the user's products
            user_products = order["users"][user_id]["products"]
            return {"status": "success", "data": user_products}
        except Exception as e:
            raise e
    
    @classmethod
    async def fulfill_order(cls, order_id: str) -> Dict[str, Any]:
        """
        Mark an order as fulfilled by a business user.
        Returns a status dictionary with status, message, and fulfilled_at date.
        """
        try:
            # Get the order from the database
            order = await cls.collection.find_one({"_id": ObjectId(order_id)})
            if not order:
                return {"status": "error", "message": ORDER_NOT_FOUND}
            
            # Check if order is already fulfilled
            if order.get("fulfilled_at"):
                return {"status": "error", "message": "Order already fulfilled"}
            
            # Check if order has been finalized
            if order.get("status") != "finalized":
                return {"status": "error", "message": "Order must be finalized before fulfillment"}
            
            # Set the fulfilled_at date and date_completed
            fulfilled_at = datetime.now()
            
            # Update the order in the database
            await cls.collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": "fulfilled", "fulfilled_at": fulfilled_at, "date_completed": fulfilled_at}}
            )
            
            return {
                "status": "success", 
                "message": "Fulfilled",
                "fulfilled_at": fulfilled_at
            }
            
        except Exception as e:
            print(f"Error fulfilling order: {e}")
            return {"status": "error", "message": str(e)}
    
    @classmethod
    async def finalize_order(cls, order_id: str) -> dict:
        """
        Finalizes an order and returns the final order with aggregated products.
        This makes the order ready for fulfillment but doesn't mark it as fulfilled yet.
        An order can be finalized multiple times as long as it hasn't been fulfilled.
        """
        try:
            # Get the order from the database
            order = await cls.collection.find_one({"_id": ObjectId(order_id)})
            if not order:
                return {"status": "error", "message": ORDER_NOT_FOUND}
            
            # Check if order is already fulfilled
            if order.get("fulfilled_at"):
                return {"status": "error", "message": "Order already fulfilled", "code": 409}
            
            # Aggregate products across all users
            aggregated_products = {}
            total_quantity = 0
            
            # Iterate through all users and their products
            for user_id, user_data in order["users"].items():
                for product in user_data["products"]:
                    # Create a unique key for each product + ingredients combination
                    ingredients_key = ",".join(sorted(product["ingredients"]))
                    product_key = f"{product['id']}|{ingredients_key}"
                    
                    if product_key not in aggregated_products:
                        aggregated_products[product_key] = {
                            "id": product["id"],
                            "name": product["name"],
                            "price_per_unit": product["price"],
                            "img_url": product["img_url"],
                            "quantity": 0,
                            "ingredients": product["ingredients"]
                        }
                    
                    # Increment quantity and update total
                    aggregated_products[product_key]["quantity"] += product["quantity"]
                    total_quantity += product["quantity"]
            
            # Calculate total prices
            products_list = []
            total_price = 0
            
            for product_key, product_data in aggregated_products.items():
                # Calculate total price for this product
                product_total = product_data["price_per_unit"] * product_data["quantity"]
                product_data["total_price"] = product_total
                total_price += product_total
                
                # Add to products list
                products_list.append(product_data)
            
            # Create the response
            result = {
                "products": products_list,
                "total_price": total_price,
                "total_quantity": total_quantity
            }
            
            # Update the order in the database to mark it as finalized
            await cls.collection.update_one(
                {"_id": ObjectId(order_id)},
                {"$set": {"status": "finalized"}}
            )
            
            return {"status": "success", "data": result}
            
        except Exception as e:
            print(f"Error finalizing order: {e}")
            return {"status": "error", "message": str(e)}