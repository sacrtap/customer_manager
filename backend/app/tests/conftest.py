import os
import sys

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.config import settings


@pytest_asyncio.fixture
async def test_engine():
    """为每个测试创建独立的异步引擎"""
    engine = create_async_engine(
        settings.asyncpg_url,
        echo=settings.environment == "development",
        pool_pre_ping=True,
        pool_size=1,
        max_overflow=0,
    )
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def test_session(test_engine):
    """为每个测试创建会话，使用显式事务控制"""
    async_session_maker = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    session = async_session_maker()
    session.begin()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()
