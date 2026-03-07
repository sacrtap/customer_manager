#!/bin/bash

# =========================================
# Customer Manager 快速启动脚本 (开发环境)
# =========================================

set -e

echo "========================================="
echo " Customer Manager 快速启动"
echo "========================================="

# 检查 PostgreSQL 是否运行
echo "[1/4] 检查 PostgreSQL..."
if ! command -v psql &> /dev/null; then
    echo "⚠️  PostgreSQL 未安装，请使用 Docker 启动"
    echo "运行：docker-compose up -d postgres"
    exit 1
fi

# 启动数据库
echo "[2/4] 启动 PostgreSQL..."
docker-compose up -d postgres
sleep 3

# 初始化数据库
echo "[3/4] 初始化数据库..."
cd backend
source venv/bin/activate || true
python migrate_db.py
cd ..

# 启动服务
echo "[4/4] 启动应用服务..."
echo ""
echo "💡 提示：使用以下命令启动服务"
echo ""
echo "后端 (终端 1):"
echo "  cd backend && source venv/bin/activate && python -m sanic main.app --reload"
echo ""
echo "前端 (终端 2):"
echo "  cd frontend && npm run dev"
echo ""
echo "或者使用 Docker Compose 启动所有服务:"
echo "  docker-compose up -d"
echo ""
echo "访问地址:"
echo "  前端开发：http://localhost:5173"
echo "  后端 API：http://localhost:8000"
echo ""
