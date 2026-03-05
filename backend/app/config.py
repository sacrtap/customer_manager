from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database settings
    db_type: str = "mysql"  # mysql 或 postgresql
    db_user: str = "root"
    db_password: str = "root"
    db_name: str = "customer_manager"
    db_host: str = "localhost"
    db_port: str = "3306"  # MySQL 默认 3306

    # 测试数据库配置
    test_db_type: str = "mysql"
    test_db_user: str = "root"
    test_db_password: str = "root"
    test_db_name: str = "customer_manager_test"
    test_db_host: str = "localhost"
    test_db_port: str = "3306"

    @property
    def database_url(self) -> str:
        if self.db_type == "mysql":
            return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def asyncpg_url(self) -> str:
        # 测试数据库 URL
        if self.test_db_type == "mysql":
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
