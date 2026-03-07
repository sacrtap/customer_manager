"""
User Service 测试 - 测试用户服务层
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.user import User
from app.models.role import Role, UserRole
from app.services.user_service import UserService


@pytest_asyncio.fixture(scope="function")
async def test_role(session: AsyncSession):
    """创建测试角色"""
    role = Role(
        name=f"TestRole_{uuid.uuid4()}",
        code=f"TEST_{uuid.uuid4().hex[:8]}",
        description="测试角色",
        permissions=["customer.view"],
    )
    session.add(role)
    await session.flush()
    yield role


@pytest_asyncio.fixture(scope="function")
async def setup_test_users(session: AsyncSession, test_role: Role):
    """创建测试用户数据"""
    users = [
        User(
            username=f"user_{uuid.uuid4().hex[:8]}",
            password_hash="hashed_password",
            real_name=f"用户{i + 1}",
            email=f"user{i + 1}@example.com",
            phone=f"1380000000{i}",
            status="active" if i % 2 == 0 else "inactive",
        )
        for i in range(5)
    ]

    for user in users:
        session.add(user)
    await session.flush()

    # 分配角色 (在 user flush 之后)
    for user in users:
        user_role = UserRole(user_id=user.id, role_id=test_role.id)
        session.add(user_role)

    await session.flush()
    yield {"users": users, "role": test_role}


@pytest.mark.asyncio
async def test_list_users(session, setup_test_users):
    """测试获取用户列表"""
    result = await UserService.list_users(
        session=session,
        page=1,
        size=10,
    )

    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "size" in result

    assert result["total"] >= 5
    assert len(result["items"]) >= 5
    assert result["page"] == 1
    assert result["size"] == 10


@pytest.mark.asyncio
async def test_list_users_pagination(session, setup_test_users):
    """测试分页获取用户列表"""
    result = await UserService.list_users(
        session=session,
        page=1,
        size=2,
    )

    assert result["total"] >= 5
    assert len(result["items"]) == 2
    assert result["page"] == 1
    assert result["size"] == 2


@pytest.mark.asyncio
async def test_list_users_filter_by_keyword(session, setup_test_users):
    """测试按关键词搜索用户"""
    result = await UserService.list_users(
        session=session,
        page=1,
        size=10,
        keyword="用户 1",
    )

    assert result["total"] >= 1


@pytest.mark.asyncio
async def test_get_user(session, setup_test_users):
    """测试获取用户详情"""
    user_id = setup_test_users["users"][0].id

    user = await UserService.get_user(
        session=session,
        user_id=user_id,
    )

    assert user is not None
    assert user.id == user_id
    assert "用户" in user.real_name


@pytest.mark.asyncio
async def test_get_user_not_found(session):
    """测试获取不存在的用户"""
    user = await UserService.get_user(
        session=session,
        user_id=99999,
    )

    assert user is None


@pytest.mark.asyncio
async def test_get_user_by_username(session, setup_test_users):
    """测试根据用户名获取用户"""
    username = setup_test_users["users"][0].username

    user = await UserService.get_user_by_username(
        session=session,
        username=username,
    )

    assert user is not None
    assert user.username == username


@pytest.mark.asyncio
async def test_create_user(session, test_role):
    """测试创建用户"""
    new_user_data = {
        "username": f"newuser_{uuid.uuid4().hex[:8]}",
        "password": "TestPass123!",
        "real_name": "新用户",
        "email": "newuser@example.com",
        "phone": "13900139000",
        "status": "active",
    }

    user = await UserService.create_user(
        session=session,
        data=new_user_data,
        role_ids=[test_role.id],
    )

    assert user is not None
    assert user.username == new_user_data["username"]
    assert user.real_name == "新用户"


@pytest.mark.asyncio
async def test_update_user(session, setup_test_users, test_role):
    """测试更新用户"""
    user_id = setup_test_users["users"][0].id

    update_data = {
        "real_name": "更新后的名字",
        "email": "updated@example.com",
        "phone": "13900000000",
    }

    user = await UserService.update_user(
        session=session,
        user_id=user_id,
        data=update_data,
        role_ids=[test_role.id],
    )

    assert user is not None
    assert user.real_name == "更新后的名字"
    assert user.email == "updated@example.com"


@pytest.mark.asyncio
async def test_update_user_not_found(session, test_role):
    """测试更新不存在的用户"""
    update_data = {"real_name": "更新名字"}

    user = await UserService.update_user(
        session=session,
        user_id=99999,
        data=update_data,
        role_ids=[test_role.id],
    )

    assert user is None


@pytest.mark.asyncio
async def test_delete_user(session, setup_test_users):
    """测试删除用户"""
    user_id = setup_test_users["users"][-1].id

    result = await UserService.delete_user(
        session=session,
        user_id=user_id,
    )

    assert result is True

    # 验证用户已被删除
    user = await UserService.get_user(
        session=session,
        user_id=user_id,
    )

    assert user is None


@pytest.mark.asyncio
async def test_delete_user_not_found(session):
    """测试删除不存在的用户"""
    result = await UserService.delete_user(
        session=session,
        user_id=99999,
    )

    assert result is False


@pytest.mark.asyncio
async def test_update_password(session, setup_test_users):
    """测试更新密码"""
    user_id = setup_test_users["users"][0].id

    result = await UserService.update_password(
        session=session,
        user_id=user_id,
        new_password="NewPass123!",
    )

    assert result is True
