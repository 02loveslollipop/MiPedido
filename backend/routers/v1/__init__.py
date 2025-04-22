# API package for organizing route handlers by model
from fastapi import APIRouter

# Create a router for all API endpoints
api_router = APIRouter()

# Import all routes
from .restaurant import router as restaurant_router
from .product import router as product_router
from .order import router as order_router
from .user import router as user_router

# Include all routers
api_router.include_router(restaurant_router)
api_router.include_router(product_router)
api_router.include_router(order_router)
api_router.include_router(user_router)