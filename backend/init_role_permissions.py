#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化角色权限脚本
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.database import async_session_maker
from app.models.role import Role

# 角色权限配置
ROLE_PERMISSIONS = {
    'admin': ['*'],  # 超级管理员拥有所有权限
    'manager': [
        'customer', 'customer.view', 'customer.create', 'customer.update', 
        'customer.delete', 'customer.import', 'customer.export',
        'user', 'user.view', 'user.create', 'user.update', 'user.delete',
        'system', 'system.log.view', 'system.backup',
        'rbac', 'rbac.role'
    ],
    'specialist': [
        'customer', 'customer.view', 'customer.create', 'customer.update',
        'customer.import', 'customer.export',
        'system.log.view'
    ],
    'sales': [
        'customer', 'customer.view', 'customer.view.self',
        'customer.export', 'customer.export.self'
    ]
}

async def init_permissions():
    """初始化角色权限"""
    async with async_session_maker() as session:
        for role_code, permissions in ROLE_PERMISSIONS.items():
            role = (await session.execute(
                select(Role).where(Role.code == role_code)
            )).scalar_one_or_none()
            
            if role:
                role.permissions = permissions
                print(f"✓ 更新角色 {role_code} 的权限：{len(permissions)} 个")
            else:
                print(f"⚠ 角色 {role_code} 不存在")
            
            await session.commit()

async def main():
    print("=" * 50)
    print("初始化角色权限")
    print("=" * 50)
    
    try:
        await init_permissions()
        print("\n" + "=" * 50)
        print("✓ 角色权限初始化完成")
        print("=" * 50)
    except Exception as e:
        print(f"\n✗ 初始化失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
