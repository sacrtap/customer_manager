from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator, Optional

from .config import settings


class Base(DeclarativeBase):
    """ORM 基类"""

    pass


engine = create_async_engine(
    settings.database_url, echo=settings.environment == "development", future=True
)

async_session_maker = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

# 测试会话覆盖 (用于测试)
_test_session_override: Optional[AsyncSession] = None


def set_test_session(session: Optional[AsyncSession]):
    """设置测试会话覆盖"""
    global _test_session_override
    _test_session_override = session


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话"""
    # 如果设置了测试会话，使用测试会话
    if _test_session_override is not None:
        yield _test_session_override
        return

    # 否则使用正常会话
    async with async_session_maker() as session:
        yield session
