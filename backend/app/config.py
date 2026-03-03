from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_name: str = "customer_manager"
    db_host: str = "localhost"
    db_port: str = "5432"

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def asyncpg_url(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 2

    environment: str = "development"

    default_page_size: int = 20
    max_page_size: int = 100

    class Config:
        env_file = "../.env"
        case_sensitive = False


settings = Settings()
