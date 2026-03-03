from datetime import datetime

import pytest

from app.models.permission import Permission
from app.models.role import Role


@pytest.mark.asyncio
async def test_create_permission(test_session):
    """测试创建权限"""
    permission = Permission(
        name="查看客户",
        code="customer.view",
        module="customer",
        description="查看客户列表和详情",
    )
    test_session.add(permission)
    await test_session.commit()
    await test_session.refresh(permission)

    assert permission.id is not None
    assert permission.code == "customer.view"


@pytest.mark.asyncio
async def test_create_role(test_session):
    """测试创建角色"""
    role = Role(
        name="运营专员",
        code="specialist",
        description="运营团队专员",
        permissions=["customer.view", "customer.create"],
    )
    test_session.add(role)
    await test_session.commit()
    await test_session.refresh(role)

    assert role.id is not None
    assert role.permissions == ["customer.view", "customer.create"]


@pytest.mark.asyncio
async def test_user_role_association(test_session):
    """测试用户角色关联"""
    from app.models.user import User

    user = User(username="testuser", password_hash="hashed", real_name="测试用户")
    test_session.add(user)
    await test_session.commit()

    role = Role(name="测试角色", code="test_role", permissions=["*"])
    test_session.add(role)
    await test_session.commit()

    user_role = Role(user_id=user.id, role_id=role.id)
    test_session.add(user_role)
    await test_session.commit()

    assert user_role.user_id == user.id
    assert user_role.role_id == role.id
