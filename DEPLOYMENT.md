# Customer Manager 部署文档

## 快速部署 (Docker Compose)

### 1. 环境准备

确保已安装：
- Docker 20.10+
- Docker Compose 2.0+
- Git

### 2. 克隆项目

```bash
git clone <repository-url> customer_manager
cd customer_manager
```

### 3. 环境配置

复制环境变量文件并修改配置：

```bash
cp .env.example .env
cp backend/.env.example backend/.env
```

编辑 `.env` 文件，修改以下关键配置：

```bash
# 数据库配置
DB_USER=customer_manager
DB_PASSWORD=<强密码>
DB_NAME=customer_manager

# JWT 密钥 (生产环境必须修改)
JWT_SECRET=<随机生成的强密钥>

# 环境配置
ENVIRONMENT=production
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

### 5. 数据库初始化

```bash
# 进入后端容器
docker-compose exec backend bash

# 运行数据库迁移
python init_db.py

# 初始化角色权限
python init_role_permissions.py

# 创建测试用户 (可选)
python create_test_users.py

# 退出容器
exit
```

### 6. 验证部署

访问以下地址验证服务：

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000/api/v1/health
- **数据库**: localhost:5432

默认管理员账号：
- 用户名：`admin`
- 密码：`admin123` (生产环境请立即修改)

---

## 服务说明

### PostgreSQL 数据库

- **端口**: 5432
- **数据持久化**: Docker volume (`postgres_data`)
- **健康检查**: 每 10 秒检测数据库连接

### Backend (Sanic API)

- **端口**: 8000
- **工作模式**: 4 个 worker 进程
- **依赖服务**: PostgreSQL

### Frontend (Nginx)

- **端口**: 3000
- **静态文件**: Vue 3 构建产物
- **API 代理**: 自动转发 `/api` 请求到后端

---

## 常用命令

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 停止并删除数据卷 (危险操作!)
docker-compose down -v

# 重启服务
docker-compose restart

# 重启单个服务
docker-compose restart backend

# 查看日志
docker-compose logs -f backend

# 进入容器
docker-compose exec backend bash
docker-compose exec frontend sh
docker-compose exec psql psql -U customer_manager

# 重新构建
docker-compose build --no-cache
```

---

## 生产环境部署

### 1. 修改 docker-compose.yml

生产环境建议：
- 使用固定的镜像版本
- 配置外部 PostgreSQL 数据库
- 使用 Nginx 反向代理
- 配置 SSL 证书
- 限制资源使用 (CPU/内存)

### 2. 环境变量管理

生产环境禁止使用默认密钥：

```bash
# 生成随机 JWT 密钥
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 使用 .env.production 文件
cp .env.example .env.production
```

### 3. 数据备份

```bash
# 备份数据库
docker-compose exec postgres pg_dump -U customer_manager customer_manager > backup.sql

# 恢复数据库
docker-compose exec -T postgres psql -U customer_manager customer_manager < backup.sql
```

### 4. 监控与日志

建议配置：
- 集中式日志 (ELK/Loki)
- 应用监控 (Prometheus/Grafana)
- 健康检查端点 (`/api/v1/health`)

---

## 故障排查

### 后端无法启动

```bash
# 查看后端日志
docker-compose logs backend

# 检查数据库连接
docker-compose exec backend python -c "from app.database import get_db; import asyncio; asyncio.run(get_db().execute('SELECT 1'))"
```

### 前端无法访问

```bash
# 检查前端构建
docker-compose logs frontend

# 验证 API 连接
curl http://localhost:8000/api/v1/health
```

### 数据库迁移失败

```bash
# 删除旧迁移并重新迁移
docker-compose exec backend bash
rm -rf backend/migrations/versions/*
python init_db.py
```

---

## 性能优化

### 1. 数据库索引

确保以下字段已建立索引：
- `customers.created_at`
- `customers.status`
- `customers.sales_owner_id`
- `billings.customer_id`

### 2. 缓存配置

生产环境建议配置 Redis 缓存：
- JWT token 黑名单
- 查询结果缓存
- 会话缓存

### 3. 静态资源 CDN

前端构建产物可部署到 CDN：
```bash
# 修改 vite.config.ts 的 base 配置
base: 'https://cdn.example.com/'
```

---

## 安全建议

1. **修改默认密钥**: JWT_SECRET 必须使用随机强密钥
2. **HTTPS**: 生产环境必须配置 SSL
3. **防火墙**: 仅开放必要端口 (80/443)
4. **定期更新**: 及时应用安全补丁
5. **访问控制**: 配置 IP 白名单

---

## 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建并重启
docker-compose up -d --build

# 运行数据库迁移
docker-compose exec backend python init_db.py
```
