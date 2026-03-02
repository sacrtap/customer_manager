import pytest
from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user():
    """测试创建用户"""
    async with async_session_maker() as session:
        user = User(
            username="testuser",
            password_hash="hashed_password",
            real_name="测试用户"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.real_name == "测试用户"


@pytest.mark.asyncio
async def test_user_to_dict():
    """测试用户转换为字典"""
    async with async_session_maker() as session:
        user = User(
            username="testuser2",
            password_hash="hashed_password",
            real_name="测试用户2"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == user.id
        assert user_dict["username"] == "testuser2"
        assert "password_hash" not in user_dict
