import pytest
from datetime import datetime
from app.database import async_session_maker
from app.models.permission import Permission
from app.models.role import Role, UserRole


@pytest.mark.asyncio
async def test_create_permission():
    """测试创建权限"""
    async with async_session_maker() as session:
        permission = Permission(
            name="查看客户",
            code="customer.view",
            module="customer",
            description="查看客户列表和详情"
        )
        session.add(permission)
        await session.commit()
        await session.refresh(permission)
        
        assert permission.id is not None
        assert permission.code == "customer.view"


@pytest.mark.asyncio
async def test_create_role():
    """测试创建角色"""
    async with async_session_maker() as session:
        role = Role(
            name="运营专员",
            code="specialist",
            description="运营团队专员",
            permissions=["customer.view", "customer.create"]
        )
        session.add(role)
        await session.commit()
        await session.refresh(role)
        
        assert role.id is not None
        assert role.permissions == ["customer.view", "customer.create"]


@pytest.mark.asyncio
async def test_user_role_association():
    """测试用户角色关联"""
    async with async_session_maker() as session:
        from app.models.user import User
        user = User(
            username="testuser",
            password_hash="hashed",
            real_name="测试用户"
        )
        session.add(user)
        await session.commit()
        
        role = Role(
            name="测试角色",
            code="test_role",
            permissions=["*"]
        )
        session.add(role)
        await session.commit()
        
        user_role = UserRole(user_id=user.id, role_id=role.id)
        session.add(user_role)
        await session.commit()
        
        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
