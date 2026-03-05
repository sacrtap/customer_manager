#!/usr/bin/env python3
"""
数据库迁移脚本 - 添加客户转移功能

使用方法:
    cd backend
    source venv/bin/activate
    python migrations/002_add_customer_transfer.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings
from app.models.transfer import CustomerTransfer
from app.database import Base


async def migrate():
    """执行数据库迁移"""
    print(f"连接到数据库：{settings.database_url}")

    # 创建引擎
    if settings.asyncpg_url.startswith("sqlite"):
        engine = create_async_engine(settings.database_url, echo=True)
    else:
        engine = create_async_engine(
            settings.database_url,
            echo=True,
            pool_pre_ping=True,
        )

    try:
        # 创建所有表 (如果不存在)
        # 注意：这会自动创建 customer_transfers 表以及所有枚举类型
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("✅ 数据库迁移完成！")
        print("   - customer_transfers 表：创建新表")
        print("   - transfer_status_enum：创建枚举类型 (PostgreSQL)")
        print("   - 外键约束：customers, users")
        print("   - 索引：idx_transfer_status, idx_transfer_created_at")

    except Exception as e:
        print(f"❌ 迁移失败：{e}")
        raise
    finally:
        await engine.dispose()


async def rollback():
    """回滚迁移（仅用于开发环境）"""
    print("回滚迁移...")

    engine = create_async_engine(
        settings.database_url,
        echo=True,
    )

    try:
        async with engine.begin() as conn:
            # 删除 customer_transfers 表
            await conn.execute(text("DROP TABLE IF EXISTS customer_transfers CASCADE"))

            # 删除枚举类型
            if settings.db_type == "postgresql":
                await conn.execute(
                    text("DROP TYPE IF EXISTS transfer_status_enum CASCADE")
                )

        print("✅ 回滚完成！")
    except Exception as e:
        print(f"❌ 回滚失败：{e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="数据库迁移工具")
    parser.add_argument(
        "--action",
        choices=["migrate", "rollback"],
        default="migrate",
        help="执行迁移或回滚",
    )

    args = parser.parse_args()

    if args.action == "migrate":
        asyncio.run(migrate())
    else:
        asyncio.run(rollback())
