import pytest
from sqlalchemy import select

from app.models.user import User


@pytest.mark.asyncio
async def test_create_user(test_session):
    """测试创建用户"""
    user = User(username="testuser", password_hash="hashed_password", real_name="测试用户")
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    assert user.id is not None
    assert user.username == "testuser"
    assert user.real_name == "测试用户"


@pytest.mark.asyncio
async def test_user_to_dict(test_session):
    """测试用户转换为字典"""
    user = User(
        username="testuser2", password_hash="hashed_password", real_name="测试用户2"
    )
    test_session.add(user)
    await test_session.commit()
    await test_session.refresh(user)

    user_dict = user.to_dict()

    assert user_dict["id"] == user.id
    assert user_dict["username"] == "testuser2"
    assert "password_hash" not in user_dict
