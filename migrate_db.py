#!/usr/bin/env python3
"""
数据库迁移脚本 - 生产环境
用法：python migrate_db.py
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

# 导入并运行迁移
from backend.migrate_db import main

if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
