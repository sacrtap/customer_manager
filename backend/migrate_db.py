#!/usr/bin/env python3
"""
生产环境数据库迁移脚本
用于部署时自动运行数据库迁移
"""

import sys
import os
import asyncio
from pathlib import Path

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from app.database import async_session_maker, Base
from app.models.user import User
from sqlalchemy import select


def get_alembic_config() -> Config:
    """获取 Alembic 配置"""
    backend_dir = Path(__file__).parent
    alembic_cfg = Config(backend_dir / "alembic.ini")
    return alembic_cfg


async def check_migration_status():
    """检查迁移状态"""
    print("\n📋 检查数据库迁移状态...")

    alembic_cfg = get_alembic_config()
    script = ScriptDirectory.from_config(alembic_cfg)

    async with async_session_maker() as session:
        # 获取当前数据库版本
        from alembic.runtime.migration import MigrationContext

        # 创建同步引擎进行检查
        from sqlalchemy import create_engine
        from app.config import settings

        # 将 asyncpg URL 转换为 psycopg2 URL 用于检查
        sync_url = str(settings.database_url).replace(
            "postgresql+asyncpg://", "postgresql+psycopg2://"
        )

        try:
            sync_engine = create_engine(sync_url)
            with sync_engine.connect() as conn:
                context = MigrationContext.configure(conn)
                current_head = context.get_current_revision()
                heads = [head.revision for head in script.get_heads()]

                print(f"   当前数据库版本：{current_head or '无'}")
                print(f"   最新迁移版本：{heads[0] if heads else '无'}")

                if current_head and heads and current_head != heads[0]:
                    print(f"   ⚠️  数据库需要迁移")
                    return False
                elif not current_head:
                    print(f"   ⚠️  数据库为空，需要初始化")
                    return False
                else:
                    print(f"   ✅ 数据库已是最新版本")
                    return True
        except Exception as e:
            print(f"   ⚠️  无法检查迁移状态：{e}")
            return False


async def run_migrations():
    """运行数据库迁移"""
    print("\n🔄 运行数据库迁移...")

    alembic_cfg = get_alembic_config()

    try:
        # 运行迁移
        command.upgrade(alembic_cfg, "head")
        print("✅ 数据库迁移成功")
        return True
    except Exception as e:
        print(f"❌ 数据库迁移失败：{e}")
        return False


async def init_base_data():
    """初始化基础数据（权限、角色、管理员用户）"""
    print("\n📦 初始化基础数据...")

    try:
        # 导入初始化脚本
        from init_db import init_permissions, init_roles, init_admin_user

        await init_permissions()
        await init_roles()
        await init_admin_user()

        print("✅ 基础数据初始化成功")
        return True
    except Exception as e:
        print(f"❌ 基础数据初始化失败：{e}")
        return False


async def verify_database():
    """验证数据库状态"""
    print("\n🔍 验证数据库状态...")

    try:
        async with async_session_maker() as session:
            # 检查管理员用户
            admin = await session.execute(select(User).where(User.username == "admin"))
            admin_user = admin.scalar_one_or_none()

            if admin_user:
                print(f"   ✅ 管理员用户存在：{admin_user.real_name}")
            else:
                print(f"   ⚠️  管理员用户不存在")

            print("✅ 数据库验证通过")
            return True
    except Exception as e:
        print(f"❌ 数据库验证失败：{e}")
        return False


async def main():
    """主函数"""
    print("=" * 60)
    print("生产环境数据库迁移")
    print("=" * 60)

    # 检查迁移状态
    is_up_to_date = await check_migration_status()

    if is_up_to_date:
        print("\n✅ 数据库已是最新版本，跳过迁移")
    else:
        # 运行迁移
        migration_success = await run_migrations()
        if not migration_success:
            print("\n❌ 迁移失败，退出")
            sys.exit(1)

        # 初始化基础数据
        init_success = await init_base_data()
        if not init_success:
            print("\n❌ 基础数据初始化失败，退出")
            sys.exit(1)

    # 验证数据库
    verify_success = await verify_database()
    if not verify_success:
        print("\n❌ 数据库验证失败，退出")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("✅ 数据库迁移完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
