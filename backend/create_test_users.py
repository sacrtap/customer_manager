#!/usr/bin/env python3
"""
创建测试用户脚本
"""

import sys
import os
import asyncio
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User
from app.models.role import Role, UserRole
from app.utils.password import hash_password


async def create_test_users():
    """创建测试用户"""
    # 读取测试用户数据
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "test-e2e",
        "fixtures",
        "users.json",
    )

    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    test_users = data["test_users"]

    async with async_session_maker() as session:
        # 获取所有角色
        roles = {}
        for role_code in ["admin", "manager", "specialist", "sales"]:
            role_result = await session.execute(
                select(Role).where(Role.code == role_code)
            )
            role = role_result.scalar_one_or_none()
            if role:
                roles[role_code] = role

        # 创建用户
        for user_data in test_users:
            # 检查用户是否已存在
            existing = await session.execute(
                select(User).where(User.username == user_data["username"])
            )
            if existing.scalar_one_or_none():
                print(f"用户 {user_data['username']} 已存在，跳过")
                continue

            # 创建用户
            user = User(
                username=user_data["username"],
                password_hash=hash_password(user_data["password"]),
                real_name=user_data["real_name"],
                email=user_data["email"],
                phone=user_data["phone"],
                status=user_data["status"],
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)

            # 分配角色
            role_code = user_data.get("role", "user")
            if role_code in roles:
                user_role = UserRole(user_id=user.id, role_id=roles[role_code].id)
                session.add(user_role)
                await session.commit()
                print(f"✓ 创建了测试用户：{user_data['username']} (角色：{role_code})")
            else:
                print(f"⚠ 用户 {user_data['username']} 的角色 {role_code} 不存在")


async def main():
    """主函数"""
    print("=" * 50)
    print("创建测试用户")
    print("=" * 50)

    try:
        await create_test_users()

        print("\n" + "=" * 50)
        print("✓ 测试用户创建完成")
        print("=" * 50)

    except Exception as e:
        print(f"\n✗ 创建失败：{e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
