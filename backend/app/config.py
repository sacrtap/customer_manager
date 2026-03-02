from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://customer_manager:changeme@localhost:5432/customer_manager"
    
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 2
    
    environment: str = "development"
    
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
