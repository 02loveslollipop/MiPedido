from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from contextlib import asynccontextmanager

from database import db
from routers import router
from utils import env

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to the database
    db.connect_to_db()
    yield
    # Shutdown: Close database connection
    db.close_db_connection()

app = FastAPI(
    title=env.app_name,
    description="API for MiPedido restaurant ordering service",
    version="1.0.0",
    debug=env.debug,
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
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=env.debug)