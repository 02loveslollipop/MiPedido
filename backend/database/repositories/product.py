from bson import ObjectId
from database import db
from models.product import Product, ProductCreate, ProductInDB
from typing import List, Optional, Dict

class ProductRepository:
    collection = db.db.db["products"]
    
    @classmethod
    async def list_products_by_restaurant(cls, restaurant_id: str) -> List[Product]:
        """
        Get all active products for a specific restaurant
        """
        products = []
        # Only retrieve active products (or products without an active field for backward compatibility)
        cursor = cls.collection.find({
            "restaurant_id": restaurant_id,
            "$or": [
                {"active": True},
                {"active": {"$exists": False}}
            ]
        })
        
        async for document in cursor:
            product = Product(
                id=str(document["_id"]),
                name=document["name"],
                description=document["description"],
                price=document["price"],
                img_url=document["img_url"],
                ingredients=document.get("ingredients", [])
            )
            products.append(product)
            
        return products
    
    @classmethod
    async def get_product(cls, product_id: str) -> Optional[Product]:
        """
        Get a specific active product by ID
        """
        try:
            document = await cls.collection.find_one({
                "_id": ObjectId(product_id),
                "$or": [
                    {"active": True},
                    {"active": {"$exists": False}}
                ]
            })
            
            if not document:
                return None
                
            return Product(
                id=str(document["_id"]),
                name=document["name"],
                description=document["description"],
                price=document["price"],
                img_url=document["img_url"],
                ingredients=document.get("ingredients", [])
            )
        except Exception as e:
            raise e
            
    @classmethod
    async def create_product(cls, product: ProductCreate) -> Product:
        """
        Create a new product
        """
        product_dict = product.model_dump()
        
        # Create document for insertion
        db_product = product_dict.copy()
        db_product["img_url"] = str(db_product["img_url"])
        
        # Insert into database
        result = await cls.collection.insert_one(db_product)
        
        # Return the created product with ID
        return Product(
            id=str(result.inserted_id),
            name=product.name,
            description=product.description,
            price=product.price,
            img_url=product.img_url,
            ingredients=product.ingredients
        )
    
    @classmethod
    async def disable_product(cls, product_id: str, restaurant_id: str) -> Dict[str, str]:
        """
        Disables a product by setting its 'active' status to False
        """
        try:
            # Verify the product exists and belongs to the specified restaurant
            product = await cls.collection.find_one({
                "_id": ObjectId(product_id),
                "restaurant_id": restaurant_id
            })
            
            if not product:
                raise Exception("Product not found or does not belong to the restaurant")
                
            # Update the product to disable it
            result = await cls.collection.update_one(
                {"_id": ObjectId(product_id)},
                {"$set": {"active": False}}
            )
            
            if result.modified_count == 0:
                raise Exception("Failed to disable product")
                
            return {"status": "success", "message": "Disabled"}
            
        except Exception as e:
            raise e