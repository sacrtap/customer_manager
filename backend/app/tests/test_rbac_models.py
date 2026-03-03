import uuid
from datetime import datetime

import pytest

from app.models.permission import Permission
from app.models.role import Role


@pytest.mark.asyncio
async def test_create_permission(test_session):
    """测试创建权限"""
    suffix = uuid.uuid4().hex[:6]
    permission = Permission(
        name=f"查看客户_{suffix}",
        code=f"customer.view.{suffix}",
        module="customer",
        description="查看客户列表和详情",
    )
    test_session.add(permission)
    await test_session.flush()
    await test_session.refresh(permission)

    assert permission.id is not None
    assert f"customer.view" in permission.code


@pytest.mark.asyncio
async def test_create_role(test_session):
    """测试创建角色"""
    suffix = uuid.uuid4().hex[:6]
    role = Role(
        name=f"运营专员_{suffix}",
        code=f"specialist_{suffix}",
        description="运营团队专员",
        permissions=["customer.view", "customer.create"],
    )
    test_session.add(role)
    await test_session.flush()
    await test_session.refresh(role)

    assert role.id is not None
    assert role.permissions == ["customer.view", "customer.create"]


@pytest.mark.asyncio
async def test_user_role_association(test_session):
    """测试用户角色关联"""
    from app.models.role import UserRole
    from app.models.user import User

    suffix = uuid.uuid4().hex[:8]
    user = User(username=f"testuser_{suffix}", password_hash="hashed", real_name="测试用户")
    test_session.add(user)
    await test_session.flush()

    role = Role(name=f"测试角色_{suffix}", code=f"test_role_{suffix}", permissions=["*"])
    test_session.add(role)
    await test_session.flush()

    user_role = UserRole(user_id=user.id, role_id=role.id)
    test_session.add(user_role)
    await test_session.flush()

    assert user_role.user_id == user.id
    assert user_role.role_id == role.id
