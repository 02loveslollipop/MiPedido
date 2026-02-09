import pytest
import pytest_asyncio
import asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
from bson import ObjectId
from typing import Any, Dict, List

# Ensure backend package is importable when running tests from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from database.db import Database, db


@pytest.fixture
def test_client():
    """
    Create a test client for the FastAPI app
    """
    with TestClient(app) as client:
        yield client


# Let pytest_asyncio handle the event loop management
@pytest_asyncio.fixture
async def async_client():
    """
    Create an async client for the FastAPI app
    """
    async with AsyncClient(app=app, base_url="http://127.0.0.1") as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def setup_test_db():
    """
    Setup a test database for testing and clean up after test
    """
    # Store the original database configuration
    original_db = db.db
    original_client = db.client

    # Create a test database connection
    test_db_name = "test_mipedido"
    
    # Connect to test database
    db.client = AsyncIOMotorClient(db.settings.mongodb_url)
    db.db = db.client[test_db_name]
    
    # Clear test database
    collections = await db.db.list_collection_names()
    for collection in collections:
        await db.db.drop_collection(collection)
    
    # Create test data
    test_data = await setup_test_data()
    
    yield test_data
    
    # Clean up - restore original database connection and drop test database
    await db.client.drop_database(test_db_name)
    db.db = original_db
    db.client = original_client


async def setup_test_data():
    """
    Create test data in database
    """
    # Create test restaurant
    restaurant_id = str(ObjectId())
    await db.db["restaurants"].insert_one({
        "_id": ObjectId(restaurant_id),
        "name": "Test Restaurant",
        "img_url": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=400&h=300"
    })
    
    print(f"Test restaurant created with ID: {restaurant_id}")
    
    # Create test products
    product_ids = []
    products = [
        {
            "name": "Test Burger",
            "description": "A delicious test burger",
            "price": 9.99,
            "img_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=200",
            "restaurant_id": restaurant_id,
            "ingredients": ["Beef patty", "Cheese", "Lettuce", "Tomato"]
        },
        {
            "name": "Test Pizza",
            "description": "A delicious test pizza",
            "price": 12.99,
            "img_url": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=300&h=200",
            "restaurant_id": restaurant_id,
            "ingredients": ["Dough", "Tomato sauce", "Mozzarella", "Basil"]
        }
    ]
    
    print(f"Test products created: {products}")
    
    for product in products:
        result = await db.db["products"].insert_one(product)
        product_ids.append(str(result.inserted_id))
    
    # Create a test order
    order_id = str(ObjectId())
    user_id = str(ObjectId())
    another_user_id = str(ObjectId())
    
    await db.db["orders"].insert_one({
        "_id": ObjectId(order_id),
        "restaurant_id": restaurant_id,
        "users": {
            user_id: {
                "products": [
                    {
                        "id": product_ids[0],
                        "name": "Test Burger",
                        "price": 9.99,
                        "img_url": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=300&h=200",
                        "quantity": 2,
                        "ingredients": ["Beef patty", "Cheese", "Lettuce"]
                    }
                ]
            }
        }
    })
    
    print(f"Test order created with ID: {order_id}")
    
    return {
        "restaurant_id": restaurant_id,
        "product_ids": product_ids,
        "order_id": order_id,
        "user_id": user_id,
        "another_user_id": another_user_id
    }