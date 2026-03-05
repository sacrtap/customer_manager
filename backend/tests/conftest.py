"""
测试配置和 fixtures
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker
import pytest_asyncio

from app.config import settings
from app.database import Base, set_test_session
from app.models.customer import Customer
from app.models.billing import Billing
from app.models.user import User
from app.models.role import Role


# 测试数据库引擎
test_engine = create_async_engine(
    settings.asyncpg_url,
    echo=False,
    pool_pre_ping=True,
    pool_size=1,
    max_overflow=0,
)

# 异步会话工厂
async_session_maker = async_sessionmaker(
    test_engine, expire_on_commit=False, class_=AsyncSession
)


@pytest_asyncio.fixture(scope="function")
async def session():
    """创建独立的测试会话"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as test_session:
        set_test_session(test_session)
        yield test_session
        set_test_session(None)


@pytest_asyncio.fixture(scope="function")
async def test_user(session: AsyncSession):
    """创建测试用户"""
    import uuid
    from app.services.role_service import RoleService

    # 创建测试角色
    role = Role(
        id=str(uuid.uuid4()),
        name=f"TestRole_{uuid.uuid4()}",
        description="测试角色",
    )
    session.add(role)
    await session.flush()

    # 创建测试用户
    user = User(
        id=str(uuid.uuid4()),
        username=f"testuser_{uuid.uuid4()}",
        password="hashed_password",
        role_id=role.id,
        customer_code="TEST001",
    )
    session.add(user)
    await session.flush()

    yield user


def create_access_token(user_id: str, username: str, permissions: list[str]) -> str:
    """创建测试用的 JWT token"""
    import jwt
    from datetime import datetime, timedelta
    from app.config import settings

    payload = {
        "user_id": user_id,
        "username": username,
        "permissions": permissions,
        "exp": datetime.utcnow() + timedelta(hours=2),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


@pytest.fixture(scope="function")
async def app():
    """创建 Sanic 应用实例"""
    from sanic import Sanic
    from app import create_app

    # 清理已注册的应用
    Sanic._app_registry.clear()

    test_app = create_app()
    test_app.config.TESTING = True
    test_app.config.UF_WORKER_COUNT = 1
    test_app.config.UF_INET = True
    yield test_app
