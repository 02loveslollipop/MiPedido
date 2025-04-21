# API package for organizing route handlers by model
from fastapi import APIRouter

# Create a router for all API endpoints
router = APIRouter()

# Import all routes
from .v1 import api_router as v1_router

# Include all routers
router.include_router(v1_router, prefix="/v1", tags=["v1"])