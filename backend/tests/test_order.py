import pytest
from httpx import AsyncClient
from bson import ObjectId

class TestOrderEndpoints:
    
    @pytest.mark.asyncio
    async def test_create_order(self, async_client, setup_test_db):
        """Test POST /v1/order/ endpoint"""
        restaurant_id = setup_test_db["restaurant_id"]
        response = await async_client.post(
            "/v1/order/", 
            json={"restaurant_id": restaurant_id}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "order_id" in data
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_create_order_invalid_restaurant(self, async_client, setup_test_db):
        """Test POST /v1/order/ with an invalid restaurant ID"""
        nonexistent_id = str(ObjectId())
        response = await async_client.post(
            "/v1/order/", 
            json={"restaurant_id": nonexistent_id}
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Restaurant not found"

    @pytest.mark.asyncio
    async def test_join_order(self, async_client, setup_test_db):
        """Test PUT /v1/order/{order_id} endpoint"""
        order_id = setup_test_db["order_id"]
        response = await async_client.put(f"/v1/order/{order_id}")
        
        assert response.status_code == 201
        data = response.json()
        assert "user_id" in data

    @pytest.mark.asyncio
    async def test_join_nonexistent_order(self, async_client, setup_test_db):
        """Test PUT /v1/order/{order_id} with nonexistent order ID"""
        nonexistent_id = str(ObjectId())
        response = await async_client.put(f"/v1/order/{nonexistent_id}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Order not found"

    @pytest.mark.asyncio
    async def test_get_user_order(self, async_client, setup_test_db):
        """Test GET /v1/order/{order_id}/{user_id} endpoint"""
        order_id = setup_test_db["order_id"]
        user_id = setup_test_db["user_id"]
        
        response = await async_client.get(f"/v1/order/{order_id}/{user_id}")
        
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) == 1
        assert products[0]["name"] == "Test Burger"
        assert products[0]["quantity"] == 2
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_user_order(self, async_client, setup_test_db):
        """Test GET /v1/order/{order_id}/{user_id} with nonexistent user ID"""
        order_id = setup_test_db["order_id"]
        nonexistent_user_id = str(ObjectId())
        
        response = await async_client.get(f"/v1/order/{order_id}/{nonexistent_user_id}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "User not found for order"

    @pytest.mark.asyncio
    async def test_modify_user_order_create(self, async_client, setup_test_db):
        """Test PUT /v1/order/{order_id}/{user_id} to add a new product"""
        order_id = setup_test_db["order_id"]
        user_id = setup_test_db["user_id"]
        product_id = setup_test_db["product_ids"][1]  # Test Pizza
        
        payload = {
            "product_id": product_id,
            "quantity": 1,
            "ingredients": ["Dough", "Tomato sauce", "Mozzarella"]
        }
        
        response = await async_client.put(
            f"/v1/order/{order_id}/{user_id}", 
            json=payload
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "Created"
        
    @pytest.mark.asyncio
    async def test_modify_user_order_update(self, async_client, setup_test_db):
        """Test PUT /v1/order/{order_id}/{user_id} to update an existing product"""
        order_id = setup_test_db["order_id"]
        user_id = setup_test_db["user_id"]
        product_id = setup_test_db["product_ids"][0]  # Test Burger
        
        payload = {
            "product_id": product_id,
            "quantity": 3,  # Changing quantity from 2 to 3
            "ingredients": ["Beef patty", "Cheese"]  # Changing ingredients
        }
        
        response = await async_client.put(
            f"/v1/order/{order_id}/{user_id}", 
            json=payload
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "Updated"
        
    @pytest.mark.asyncio
    async def test_modify_user_order_delete(self, async_client, setup_test_db):
        """Test PUT /v1/order/{order_id}/{user_id} to delete a product"""
        order_id = setup_test_db["order_id"]
        user_id = setup_test_db["user_id"]
        product_id = setup_test_db["product_ids"][0]  # Test Burger
        
        payload = {
            "product_id": product_id,
            "quantity": 0,  # Setting quantity to 0 should delete the product
            "ingredients": ["Beef patty", "Cheese", "Lettuce"]
        }
        
        response = await async_client.put(
            f"/v1/order/{order_id}/{user_id}", 
            json=payload
        )
        
        assert response.status_code == 200
        assert response.json()["status"] == "Deleted"
        
    @pytest.mark.asyncio
    async def test_modify_nonexistent_order(self, async_client, setup_test_db):
        """Test PUT /v1/order/{order_id}/{user_id} with nonexistent order ID"""
        nonexistent_id = str(ObjectId())
        user_id = setup_test_db["user_id"]
        product_id = setup_test_db["product_ids"][0]
        
        payload = {
            "product_id": product_id,
            "quantity": 1,
            "ingredients": ["Beef patty", "Cheese", "Lettuce"]
        }
        
        response = await async_client.put(
            f"/v1/order/{nonexistent_id}/{user_id}", 
            json=payload
        )
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Order not found"