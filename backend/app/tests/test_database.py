import pytest
from app.database import engine, async_session_maker, get_db_session


@pytest.mark.asyncio
async def test_database_connection():
    """测试数据库连接"""
    async with engine.connect() as conn:
        result = await conn.execute("SELECT 1")
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_session():
    """测试获取数据库会话"""
    async for session in get_db_session():
        assert session is not None
        break  # 只测试第一次迭代
