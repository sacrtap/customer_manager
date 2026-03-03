import sys
import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings

_test_engine = None
_test_async_session_maker = None


@pytest.fixture(scope="session")
def test_engine():
    """为测试会话创建引擎"""
    global _test_engine, _test_async_session_maker
    if _test_engine is None:
        _test_engine = create_async_engine(
            settings.asyncpg_url,
            echo=settings.environment == "development",
            pool_pre_ping=True,
            pool_size=20,
            max_overflow=40,
        )
        _test_async_session_maker = async_sessionmaker(
            _test_engine, class_=AsyncSession, expire_on_commit=False
        )
    return _test_engine


@pytest_asyncio.fixture
async def test_session(test_engine):
    """为每个测试创建会话"""
    async with _test_async_session_maker() as session:
        yield session
        await session.close()
