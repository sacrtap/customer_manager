import pytest
from sqlalchemy import text

from app.database import async_session_maker, engine, get_db_session


@pytest.mark.asyncio
async def test_database_connection(test_engine):
    """测试数据库连接"""
    async with test_engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_session():
    """测试获取数据库会话"""
    async for session in get_db_session():
        assert session is not None
        break  # 只测试第一次迭代
