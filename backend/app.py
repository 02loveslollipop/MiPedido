from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

try:
    from database import db
except ModuleNotFoundError:
    # Some build contexts put database files at /app (as db.py) instead of /app/database
    from db import db
from routers import router
from utils import env
from database.repositories.restuarant import RestaurantRepository
from database.repositories.product import ProductRepository

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database is already connected at import time, but we can reconnect if needed
    if db.db is None:
        db.db = db.Database()
    print("FastAPI application started")

    # No cache refresh here; handled by external job

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

#This is a test

# Register the router
app.include_router(router)

# Health check endpoint
@app.get("/health")
async def health():
    return {"status": "ok"}

#This is a test

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000)
