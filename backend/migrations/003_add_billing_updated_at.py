#!/usr/bin/env python3
"""
数据库迁移脚本 - 为 billings 表添加 updated_at 字段

使用方法:
    cd backend
    source venv/bin/activate
    python migrations/003_add_billing_updated_at.py
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import settings


async def migrate():
    """执行数据库迁移"""
    print(f"连接到数据库：{settings.database_url}")

    # 创建引擎
    engine = create_async_engine(
        settings.database_url,
        echo=True,
        pool_pre_ping=True,
    )

    try:
        async with engine.begin() as conn:
            # 为 billings 表添加 updated_at 字段
            if settings.db_type == "postgresql":
                await conn.execute(
                    text("""
                        ALTER TABLE billings 
                        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    """)
                )
            else:
                await conn.execute(
                    text("""
                        ALTER TABLE billings 
                        ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    """)
                )

        print("✅ 数据库迁移完成！")
        print("   - billings 表：添加 updated_at 字段")

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
            # 删除 updated_at 字段
            await conn.execute(
                text("ALTER TABLE billings DROP COLUMN IF EXISTS updated_at")
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
