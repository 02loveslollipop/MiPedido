import pytest
from httpx import AsyncClient
from bson import ObjectId

class TestProductEndpoints:
    
    @pytest.mark.asyncio
    async def test_list_products(self, async_client, setup_test_db):
        """Test GET /v1/products/{restaurant_id} endpoint"""
        restaurant_id = setup_test_db["restaurant_id"]
        response = await async_client.get(f"/v1/products/{restaurant_id}")
        
        assert response.status_code == 200
        products = response.json()
        assert isinstance(products, list)
        assert len(products) == 2
        
        # Check product details
        product_names = [p["name"] for p in products]
        assert "Test Burger" in product_names
        assert "Test Pizza" in product_names
        
        # Check product structure
        for product in products:
            assert "id" in product
            assert "name" in product
            assert "description" in product
            assert "price" in product
            assert "img_url" in product
            assert "ingredients" in product
            assert isinstance(product["ingredients"], list)
    
    @pytest.mark.asyncio
    async def test_list_products_nonexistent_restaurant(self, async_client, setup_test_db):
        """Test GET /v1/products/{restaurant_id} with nonexistent restaurant ID"""
        nonexistent_id = str(ObjectId())
        response = await async_client.get(f"/v1/products/{nonexistent_id}")
        
        assert response.status_code == 404
        assert "error" in response.json() or "detail" in response.json()  # Check for error message in response