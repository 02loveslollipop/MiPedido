import pytest
from httpx import AsyncClient
from bson import ObjectId

class TestRestaurantEndpoints:
    
    @pytest.mark.asyncio
    async def test_list_restaurants(self, async_client, setup_test_db):
        """Test GET /v1/restaurant/ endpoint"""
        response = await async_client.get("/v1/restaurant/")
        
        assert response.status_code == 200
        restaurants = response.json()
        assert isinstance(restaurants, list)
        assert len(restaurants) == 1
        assert restaurants[0]["name"] == "Test Restaurant"
        assert "id" in restaurants[0]
        assert "img_url" in restaurants[0]
    
    @pytest.mark.asyncio
    async def test_get_restaurant(self, async_client, setup_test_db):
        """Test GET /v1/restaurant/{restaurant_id} endpoint"""
        restaurant_id = setup_test_db["restaurant_id"]
        response = await async_client.get(f"/v1/restaurant/{restaurant_id}")
        
        assert response.status_code == 200
        restaurant = response.json()
        assert restaurant["name"] == "Test Restaurant"
        assert restaurant["id"] == restaurant_id
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_restaurant(self, async_client, setup_test_db):
        """Test GET /v1/restaurant/{restaurant_id} with nonexistent ID"""
        nonexistent_id = str(ObjectId())
        response = await async_client.get(f"/v1/restaurant/{nonexistent_id}")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Restaurant not found"
    
    @pytest.mark.asyncio
    async def test_create_restaurant(self, async_client, setup_test_db):
        """Test POST /v1/restaurant/ endpoint"""
        new_restaurant = {
            "name": "New Test Restaurant",
            "img_url": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=400&h=300"
        }
        
        response = await async_client.post("/v1/restaurant/", json=new_restaurant)
        
        assert response.status_code == 201
        created_restaurant = response.json()
        assert created_restaurant["name"] == "New Test Restaurant"
        assert "id" in created_restaurant