# API package for organizing route handlers by model
from fastapi import APIRouter

# Create a router for all API endpoints
api_router = APIRouter()

# Import all routes
from .restaurant import router as restaurant_router
from .product import router as product_router
from .order import router as order_router
from .user import router as user_router
from .review import router as review_router
from .shortener import router as shortener_router
from .admin_restaurants import router as admin_restaurant_router
from .admin_products import router as admin_product_router
from .admin_users import router as admin_user_router
from .admin import router as admin_router
from .admin_logs import router as admin_log_router
from .blob_storage import router as blob_storage_router
from .search import router as search_router

# Include all routers
api_router.include_router(restaurant_router)
api_router.include_router(product_router)
api_router.include_router(order_router)
api_router.include_router(user_router)
api_router.include_router(review_router)
api_router.include_router(shortener_router)
api_router.include_router(admin_restaurant_router)
api_router.include_router(admin_product_router)
api_router.include_router(admin_user_router)
api_router.include_router(admin_router)
api_router.include_router(admin_log_router)
api_router.include_router(blob_storage_router)
api_router.include_router(search_router)