"""
测试配置和 fixture
"""

import os
import sys
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from sanic import Sanic
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings
from app.database import Base, get_db_session, set_test_session
from app.blueprints import (
    auth,
    customer,
    price_band,
    price_config,
    pricing_strategy,
    role,
    system,
)


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """为每个测试创建独立的异步引擎"""
    engine = create_async_engine(
        settings.asyncpg_url,
        echo=False,
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )

    # 创建所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # 清理所有表
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """为每个测试创建会话，使用显式事务控制"""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        # 设置测试会话覆盖，让蓝图使用此会话
        set_test_session(session)
        yield session
        # 清理测试会话覆盖
        set_test_session(None)


@pytest.fixture(scope="function")
def test_app(test_session) -> Generator[Sanic, None, None]:
    """创建测试用的 Sanic 应用"""

    # 创建测试应用
    app = Sanic(f"test_app_{os.getpid()}")

    # 配置
    app.config.update(
        DATABASE_URL=settings.database_url,
        JWT_SECRET=settings.jwt_secret,
        ENVIRONMENT=settings.environment,
    )

    # 挂载中间件
    from app.middlewares.auth import attach_auth_middleware

    attach_auth_middleware(app)

    # 注册蓝图
    from app.blueprints import (
        auth,
        customer,
        price_band,
        price_config,
        pricing_strategy,
        role,
        system,
    )

    app.blueprint(auth.auth_bp)
    app.blueprint(customer.customer_bp)
    app.blueprint(role.role_bp)
    app.blueprint(system.system_bp)
    app.blueprint(pricing_strategy.pricing_strategy_bp)
    app.blueprint(price_config.price_config_bp)
    app.blueprint(price_band.price_band_bp)

    @app.get("/health")
    async def health_check(request):
        return app.json({"status": "healthy", "version": "1.0.0"})

    yield app
