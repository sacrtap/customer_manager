from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    db_type: str = "postgresql"  # mysql 或 postgresql
    db_user: str = "postgres"
    db_password: str = ""
    db_name: str = "customer_manager"
    db_host: str = "localhost"
    db_port: str = "5432"  # PostgreSQL 默认 5432

    # 测试数据库配置 - 使用 PostgreSQL
    test_db_type: str = "postgresql"
    test_db_user: str = "postgres"
    test_db_password: str = ""
    test_db_name: str = "customer_manager_test"
    test_db_host: str = "localhost"
    test_db_port: str = "5432"

    @property
    def database_url(self) -> str:
        if self.db_type == "mysql":
            return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def asyncpg_url(self) -> str:
        # 测试数据库 URL
        if self.test_db_type == "sqlite":
            return f"sqlite+aiosqlite:///{self.test_db_name}"
        elif self.test_db_type == "mysql":
            return f"mysql+aiomysql://{self.test_db_user}:{self.test_db_password}@{self.test_db_host}:{self.test_db_port}/{self.test_db_name}"
        else:
            return f"postgresql+asyncpg://{self.test_db_user}:{self.test_db_password}@{self.test_db_host}:{self.test_db_port}/{self.test_db_name}"

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
