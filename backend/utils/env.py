import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Application settings
    app_name: str = "MiPedido API"
    debug: bool = os.getenv("DEBUG", "False") == "True"
    secret_key: str = os.getenv("SECRET_KEY", "default_secret_key")
    
    # MongoDB settings
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name: str = os.getenv("DATABASE_NAME", "mipedido")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    
    blob_read_write_token: str | None = os.getenv("BLOB_READ_WRITE_TOKEN", "default_blob_token")
    gin_mode: str | None = os.getenv("GIN_MODE", "release")
    
    # JWT admin settings
    admin_public_key: str | None = os.getenv("ADMIN_PUBLIC_KEY", None)
    admin_private_key: str | None = os.getenv("ADMIN_PRIVATE_KEY", None)
    
    # Redis
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", 6379))
    redis_db: str = str(os.getenv("REDIS_DB", 0))
    redis_password: str | None = os.getenv("REDIS_PASSWORD", None)
    redis_decode_responses: bool = os.getenv("REDIS_DECODE_RESPONSES", "True") == "True"
    
    class Config:
        env_file = ".env"

settings = Settings()