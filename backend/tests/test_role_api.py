"""
Role Service 测试 - 测试角色服务层
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.role import Role, UserRole
from app.models.user import User
from app.services.role_service import RoleService


@pytest_asyncio.fixture(scope="function")
async def setup_test_roles(session: AsyncSession):
    """创建测试角色数据"""
    roles = [
        Role(
            name=f"测试角色{i + 1}_{uuid.uuid4().hex[:4]}",
            code=f"ROLE_{uuid.uuid4().hex[:8]}",
            description=f"测试角色{i + 1}",
            permissions=["customer.view", "customer.edit"]
            if i % 2 == 0
            else ["customer.view"],
            is_system=False,
        )
        for i in range(4)
    ]

    for role in roles:
        session.add(role)
    await session.flush()

    yield {"roles": roles}


@pytest.mark.asyncio
async def test_list_roles(session, setup_test_roles):
    """测试获取角色列表"""
    result = await RoleService.list_roles(
        session=session,
        page=1,
        size=10,
    )

    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "size" in result

    assert result["total"] >= 4
    assert len(result["items"]) >= 4


@pytest.mark.asyncio
async def test_list_roles_pagination(session, setup_test_roles):
    """测试分页获取角色列表"""
    result = await RoleService.list_roles(
        session=session,
        page=1,
        size=2,
    )

    assert result["total"] >= 4
    assert len(result["items"]) == 2


@pytest.mark.asyncio
async def test_list_roles_filter_by_keyword(session, setup_test_roles):
    """测试按关键词搜索角色"""
    result = await RoleService.list_roles(
        session=session,
        page=1,
        size=10,
        keyword="测试角色",
    )

    assert result["total"] >= 4


@pytest.mark.asyncio
async def test_delete_role(session):
    """测试删除角色"""
    # 创建一个新角色用于删除测试 (避免外键约束)
    new_role = Role(
        name=f"待删除角色_{uuid.uuid4().hex[:4]}",
        code=f"DEL_{uuid.uuid4().hex[:8]}",
        description="用于删除测试",
        permissions=["test"],
        is_system=False,
    )
    session.add(new_role)
    await session.flush()

    result = await RoleService.delete_role(
        session=session,
        role_id=new_role.id,
    )

    assert result is True

    # 验证角色已被删除
    role = await RoleService.get_role(
        session=session,
        role_id=new_role.id,
    )

    assert role is None


@pytest.mark.asyncio
async def test_get_role_by_code(session, setup_test_roles):
    """测试根据编码获取角色"""
    role_code = setup_test_roles["roles"][0].code

    role = await RoleService.get_role_by_code(
        session=session,
        code=role_code,
    )

    assert role is not None
    assert role.code == role_code


@pytest.mark.asyncio
async def test_create_role(session):
    """测试创建角色"""
    new_role_data = {
        "name": f"新角色_{uuid.uuid4().hex[:4]}",
        "code": f"NEW_{uuid.uuid4().hex[:8]}",
        "description": "测试新角色",
        "permissions": ["customer.view", "customer.create"],
        "is_system": False,
    }

    role = await RoleService.create_role(
        session=session,
        data=new_role_data,
    )

    assert role is not None
    assert "新角色" in role.name


@pytest.mark.asyncio
async def test_update_role(session, setup_test_roles):
    """测试更新角色"""
    role_id = setup_test_roles["roles"][0].id

    update_data = {
        "name": f"更新后的角色名_{uuid.uuid4().hex[:4]}",
        "description": "更新后的描述",
        "permissions": ["customer.view", "customer.edit", "customer.delete"],
    }

    role = await RoleService.update_role(
        session=session,
        role_id=role_id,
        data=update_data,
    )

    assert role is not None
    assert "更新后的角色名" in role.name
    assert role.description == "更新后的描述"


@pytest.mark.asyncio
async def test_update_role_not_found(session):
    """测试更新不存在的角色"""
    update_data = {"name": "更新名字"}

    role = await RoleService.update_role(
        session=session,
        role_id=99999,
        data=update_data,
    )

    assert role is None


@pytest.mark.asyncio
async def test_delete_role(session, setup_test_roles):
    """测试删除角色"""
    role_id = setup_test_roles["roles"][-1].id

    result = await RoleService.delete_role(
        session=session,
        role_id=role_id,
    )

    assert result is True

    # 验证角色已被删除
    role = await RoleService.get_role(
        session=session,
        role_id=role_id,
    )

    assert role is None


@pytest.mark.asyncio
async def test_delete_system_role(session):
    """测试删除系统角色 (应该失败)"""
    system_role = Role(
        name="系统角色",
        code=f"SYSTEM_{uuid.uuid4().hex[:8]}",
        description="系统角色不能被删除",
        permissions=["*"],
        is_system=True,
    )
    session.add(system_role)
    await session.flush()

    result = await RoleService.delete_role(
        session=session,
        role_id=system_role.id,
    )

    assert result is False

    # 验证系统角色仍然存在
    role = await RoleService.get_role(
        session=session,
        role_id=system_role.id,
    )

    assert role is not None
    assert role.is_system is True
