from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from database import db
from routers import router
from utils import env

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database is already connected at import time, but we can reconnect if needed
    if db.db is None:
        db.connect_to_db()
    print("FastAPI application started")
    yield
    # Shutdown: Close database connection
    db.close_db_connection()
    print("FastAPI application shutdown")

app = FastAPI(
    title="MiPedido API",
    description="API for MiPedido restaurant ordering service",
    version="1.0.0",
    debug=True, #TODO: set to env.debug
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) # Set reload=True for development