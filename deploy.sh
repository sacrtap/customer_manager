#!/bin/bash

# =========================================
# Customer Manager 一键部署脚本
# =========================================

set -e

echo "========================================="
echo " Customer Manager 一键部署脚本"
echo "========================================="

# 检查依赖
echo "[1/6] 检查依赖..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 已安装"

# 环境配置
echo "[2/6] 配置环境..."
if [ ! -f .env ]; then
    echo "📋 复制环境配置文件..."
    cp .env.example .env
    echo "⚠️  请编辑 .env 文件修改配置，特别是："
    echo "   - DB_PASSWORD (数据库密码)"
    echo "   - JWT_SECRET (JWT 密钥)"
    echo ""
    read -p "是否继续？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

if [ ! -f backend/.env ]; then
    echo "📋 复制后端环境配置文件..."
    cp backend/.env.example backend/.env
fi

# 启动服务
echo "[3/6] 启动 Docker 服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

# 健康检查
echo "[4/6] 健康检查..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ 后端服务正常"
        break
    fi
    attempt=$((attempt + 1))
    echo "⏳ 等待后端启动... ($attempt/$max_attempts)"
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ 后端服务启动失败，请查看日志："
    docker-compose logs backend
    exit 1
fi

# 数据库迁移和初始化
echo "[5/6] 迁移数据库..."
docker-compose exec -T backend python backend/migrate_db.py

echo "✅ 数据库迁移完成"

# 完成
echo "[6/6] 部署完成!"
echo ""
echo "========================================="
echo " 🎉 部署成功!"
echo "========================================="
echo ""
echo "访问地址:"
echo "  前端：http://localhost:3000"
echo "  后端：http://localhost:8000"
echo ""
echo "默认管理员账号:"
echo "  用户名：admin"
echo "  密码：admin123"
echo ""
echo "⚠️  重要提示：请立即修改管理员密码！"
echo ""
echo "常用命令:"
echo "  docker-compose logs -f     # 查看日志"
echo "  docker-compose down        # 停止服务"
echo "  docker-compose ps          # 查看状态"
echo ""
