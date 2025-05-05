from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from database import db
from routers import router
from utils import env
from cache.redis.cache import refresh_all_cache
from database.repositories.restuarant import RestaurantRepository
from database.repositories.product import ProductRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database is already connected at import time, but we can reconnect if needed
    if db.db is None:
        db.db = db.Database()
    print("FastAPI application started")

    # Refresh Redis cache on startup
    async def fetch_restaurants():
        # Returns list of dicts for cache
        return [r.model_dump() for r in await RestaurantRepository.list_restaurants()]

    async def fetch_products_by_restaurant(restaurant_id: str):
        return await ProductRepository.list_all_products_by_restaurant(restaurant_id)

    await refresh_all_cache(fetch_restaurants, fetch_products_by_restaurant)

    yield
    # Shutdown: Close database connection
    db.db.close_db_connection()
    print("FastAPI application shutdown")

try:
    DEBUG = env.DEBUG
except AttributeError:
    DEBUG = False

app = FastAPI(
    title="MiPedido API",
    description="API for MiPedido restaurant ordering service",
    version="1.0.0",
    debug=DEBUG,
    lifespan=lifespan
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the router
app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)