import pytest
from httpx import AsyncClient
from bson import ObjectId

class TestReviewEndpoints:
    
    @pytest.mark.asyncio
    async def test_create_review(self, async_client, setup_test_db):
        """Test POST /v1/review/ endpoint with valid data"""
        restaurant_id = setup_test_db["restaurant_id"]
        review_data = {
            "restaurant_id": restaurant_id,
            "rating": 4
        }
        
        response = await async_client.post("/v1/review/", json=review_data)
        
        assert response.status_code == 201
        review = response.json()
        assert review["restaurant_id"] == restaurant_id
        assert review["rating"] == 4
        assert review["status"] == "pending"
        assert "id" in review
        assert "created_at" in review
    
    @pytest.mark.asyncio
    async def test_create_review_invalid_rating(self, async_client, setup_test_db):
        """Test POST /v1/review/ endpoint with invalid rating"""
        restaurant_id = setup_test_db["restaurant_id"]
        review_data = {
            "restaurant_id": restaurant_id,
            "rating": 6  # Invalid rating > 5
        }
        
        response = await async_client.post("/v1/review/", json=review_data)
        
        assert response.status_code == 400
        assert "Rating must be between 1 and 5" in response.json()["detail"]
        
    @pytest.mark.asyncio
    async def test_create_review_nonexistent_restaurant(self, async_client, setup_test_db):
        """Test POST /v1/review/ endpoint with nonexistent restaurant"""
        nonexistent_id = str(ObjectId())
        review_data = {
            "restaurant_id": nonexistent_id,
            "rating": 4
        }
        
        response = await async_client.post("/v1/review/", json=review_data)
        
        assert response.status_code == 404
        assert "Restaurant not found" in response.json()["detail"]