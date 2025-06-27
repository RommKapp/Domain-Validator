import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./edv_database.db")
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    api_key: str = os.getenv("API_KEY", "your-secret-api-key")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    # Performance settings
    cache_ttl: int = 3600  # 1 hour
    batch_size: int = 100
    request_timeout: int = 5
    
    class Config:
        env_file = ".env"

settings = Settings()