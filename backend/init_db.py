#!/usr/bin/env python3
"""
初始化数据库脚本
创建初始角色、权限和管理员用户
"""

import sys
import os
import asyncio
import uuid
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User
from app.models.role import Role, UserRole
from app.models.permission import Permission
from app.utils.password import hash_password


async def init_permissions():
    """初始化权限"""
    permissions_data = [
        # 客户管理权限
        {
            "name": "查看客户",
            "code": "customer.view",
            "module": "customer",
            "description": "查看客户列表和详情",
        },
        {
            "name": "创建客户",
            "code": "customer.create",
            "module": "customer",
            "description": "创建新客户",
        },
        {
            "name": "编辑客户",
            "code": "customer.update",
            "module": "customer",
            "description": "编辑客户信息",
        },
        {
            "name": "删除客户",
            "code": "customer.delete",
            "module": "customer",
            "description": "删除客户",
        },
        {
            "name": "批量导入",
            "code": "customer.import",
            "module": "customer",
            "description": "批量导入客户数据",
        },
        {
            "name": "批量导出",
            "code": "customer.export",
            "module": "customer",
            "description": "批量导出客户数据",
        },
        # 用户管理权限
        {
            "name": "查看用户",
            "code": "user.view",
            "module": "user",
            "description": "查看用户列表和详情",
        },
        {
            "name": "创建用户",
            "code": "user.create",
            "module": "user",
            "description": "创建新用户",
        },
        {
            "name": "编辑用户",
            "code": "user.update",
            "module": "user",
            "description": "编辑用户信息",
        },
        {
            "name": "删除用户",
            "code": "user.delete",
            "module": "user",
            "description": "删除用户",
        },
        # 角色管理权限
        {
            "name": "角色管理",
            "code": "rbac.role",
            "module": "rbac",
            "description": "管理角色和权限",
        },
        # 系统管理权限
        {
            "name": "查看日志",
            "code": "system.log.view",
            "module": "system",
            "description": "查看操作日志",
        },
        {
            "name": "系统设置",
            "code": "system.settings",
            "module": "system",
            "description": "管理系统设置",
        },
    ]

    async with async_session_maker() as session:
        # 检查是否已存在权限
        existing = await session.execute(select(Permission).limit(1))
        if existing.scalar_one_or_none():
            print("权限数据已存在，跳过初始化")
            return

        # 创建权限
        for perm_data in permissions_data:
            permission = Permission(**perm_data)
            session.add(permission)

        await session.commit()
        print(f"✓ 创建了 {len(permissions_data)} 个权限")


async def init_roles():
    """初始化角色"""
    roles_data = [
        {
            "name": "系统管理员",
            "code": "admin",
            "description": "系统管理员，拥有所有权限",
            "permissions": ["*"],
            "is_system": True,
        },
        {
            "name": "运营经理",
            "code": "manager",
            "description": "运营经理，可以管理所有客户和用户",
            "permissions": [
                "customer.view",
                "customer.create",
                "customer.update",
                "customer.delete",
                "customer.import",
                "customer.export",
                "user.view",
                "system.log.view",
            ],
        },
        {
            "name": "运营专员",
            "code": "specialist",
            "description": "运营专员，可以管理和查看客户",
            "permissions": [
                "customer.view",
                "customer.create",
                "customer.update",
                "customer.import",
                "customer.export",
            ],
        },
        {
            "name": "销售人员",
            "code": "sales",
            "description": "销售人员，只能查看和编辑自己的客户",
            "permissions": ["customer.view", "customer.update"],
        },
    ]

    async with async_session_maker() as session:
        # 检查是否已存在角色
        existing = await session.execute(select(Role).limit(1))
        if existing.scalar_one_or_none():
            print("角色数据已存在，跳过初始化")
            return

        # 创建角色
        for role_data in roles_data:
            role = Role(**role_data)
            session.add(role)

        await session.commit()
        print(f"✓ 创建了 {len(roles_data)} 个角色")


async def init_admin_user():
    """初始化管理员用户"""
    admin_data = {
        "username": "admin",
        "password_hash": hash_password("admin123"),
        "real_name": "系统管理员",
        "email": "admin@example.com",
        "phone": "13800000000",
        "status": "active",
    }

    async with async_session_maker() as session:
        # 检查是否已存在管理员
        existing = await session.execute(select(User).where(User.username == "admin"))
        if existing.scalar_one_or_none():
            print("管理员用户已存在，跳过初始化")
            return

        # 创建管理员
        user = User(**admin_data)
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # 获取管理员角色
        admin_role = await session.execute(select(Role).where(Role.code == "admin"))
        admin_role = admin_role.scalar_one()

        # 分配角色
        user_role = UserRole(user_id=user.id, role_id=admin_role.id)
        session.add(user_role)
        await session.commit()

        print(f"✓ 创建了管理员用户: admin (密码: admin123)")
        print(f"✓ 分配了角色: {admin_role.name}")


async def main():
    """主函数"""
    print("=" * 50)
    print("数据库初始化")
    print("=" * 50)

    try:
        await init_permissions()
        await init_roles()
        await init_admin_user()

        print("\n" + "=" * 50)
        print("✓ 数据库初始化完成")
        print("=" * 50)
        print("\n默认管理员账号:")
        print("  用户名: admin")
        print("  密码: admin123")
        print("\n请及时修改默认密码！")

    except Exception as e:
        print(f"\n✗ 初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
