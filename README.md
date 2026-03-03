# 客户信息管理与运营系统 - 部署使用说明

**项目版本**: v1.0
**部署日期**: 2026-03-03

---

## 项目概述

本系统是一个内部运营中台的客户信息管理与运营系统，提供客户MDM（主数据管理）、批量导入导出、用户认证、RBAC权限管理等核心功能。

### 技术栈

**后端**:
- Python 3.11
- Sanic 24+ Web框架
- SQLAlchemy 2.0 ORM（异步）
- PostgreSQL 18 数据库
- Pydantic 2.5 数据验证
- PyJWT 2.8 JWT认证
- Bcrypt 4.1 密码加密
- Alembic 数据库迁移
- pytest 8.0 测试框架

**前端**:
- Vue 3 Composition API
- Vite 5 构建工具
- TypeScript
- Arco Design Vue UI库
- Pinia 状态管理
- Vue Router 4 路由
- Axios HTTP客户端
- Playwright E2E测试

**DevOps**:
- Docker Compose 服务编排
- Nginx 反向代理

---

## 环境准备

### 后端环境

#### 方式1: 本地开发环境

**1. 安装Python 3.11**
```bash
# macOS (使用Homebrew)
brew install python@3.11

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv
```

**2. 创建并激活虚拟环境**
```bash
cd backend
python3.11 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

**3. 安装依赖**
```bash
pip install -r requirements.txt
```

**4. 配置环境变量**
```bash
# 复制环境配置文件
cp .env.example .env

# 编辑.env文件，设置以下变量：
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_NAME=customer_manager
JWT_SECRET=your_jwt_secret_key_here_change_this
ENVIRONMENT=development
```

**5. 数据库初始化**
```bash
# 确保PostgreSQL服务正在运行
# 启动方式：docker compose up -d postgres
# 或本地PostgreSQL：psql -U postgres

# 运行数据库迁移
alembic upgrade head

# 创建初始数据
python init_db.py
```

**6. 启动后端服务**
```bash
# 开发环境
python -m sanic main.app --host 0.0.0 --port 8000 --reload --workers 1

# 生产环境（使用gunicorn或uvicorn）
gunicorn -w 4 -b 0.0.0:8000 main:create_app
```

#### 方式2: Docker部署

```bash
# 构建后端镜像
docker build -t customer-manager-backend:latest .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

### 前端环境

#### 方式1: 本地开发环境

**1. 安装Node.js 18+**
```bash
# 访问 https://nodejs.org/

# macOS (使用Homebrew)
brew install node

# Ubuntu/Debian
curl -fsSL https://nodejs.org/setup_18.x | sudo -E bash -

# 验证安装
node -v  # 应该显示 v18.x.x 或更高
```

**2. 安装依赖**
```bash
cd frontend
npm install
```

**3. 配置环境变量**
```bash
# 创建 .env.local 文件（如果需要）
# API地址可以默认为 http://localhost:8000
```

**4. 启动开发服务器**
```bash
npm run dev

# 服务将在 http://localhost:5173 启动
# 热口映射到 http://localhost:8000（查看vite.config.ts）
```

**5. 构建生产版本**
```bash
npm run build

# 构建输出在 dist/ 目录
```

#### 方式2: Docker部署

```bash
# 构建前端镜像
docker build -t customer-manager-frontend:latest .

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f frontend
```

---

## Docker 部署

### 完整部署

```bash
# 构建所有镜像
docker-compose build

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 服务说明

#### PostgreSQL数据库
- 端口：5432
- 数据卷：postgres_data
- 初始化脚本：自动运行数据库迁移

#### 后端API
- 端口：8000
- 暴康检查：http://localhost:8000/health
- 需要连接到PostgreSQL
- 需要运行数据库迁移

#### 前端Web
- 端口：80
- Nginx反向代理到后端
- 静态文件：/etc/nginx/conf.d/customer-manager.conf
- 需要重启Nginx

### 目录映射
- `./backend` → `/app`（后端代码）
- `./frontend/dist` → `/usr/share/nginx/html`（前端静态文件）
- `postgres_data` → `/var/lib/postgresql/data`（数据库数据）

---

## 数据库迁移

### 新环境部署

```bash
# 1. 连接到数据库
docker exec -it postgres psql -U postgres -d customer_manager

# 2. 运行迁移（在容器中）
docker exec backend alembic upgrade head

# 3. 创建初始数据
docker exec backend python init_db.py
```

### 现有环境升级

```bash
# 1. 运行迁移
docker exec backend alembic upgrade head

# 2. 备份数据
docker exec postgres pg_dump -U postgres customer_manager > backup.sql
docker exec -i postgres psql -U postgres customer_manager < backup.sql
```

---

## 默认账号

⚠️ **生产环境部署后立即修改以下默认密码！**

| 用户名 | 默认密码 | 角色 | 说明 |
|---------|-----------|------|------|
| admin | admin123 | 系统管理员 | 超级管理员，拥有所有权限 |
| manager | manager123 | 运营经理 | 可管理客户、用户、查看日志 |
| specialist | specialist123 | 运运营专员 | 可管理客户、查看日志 |
| sales | sales123 | 销售人员 | 只能查看和编辑自己的客户 |

---

## 访问地址

### 本地开发环境

- **后端API**: http://localhost:8000
- **健康检查**: http://localhost:8000/health
- **前端应用**: http://localhost:5173

### Docker部署

- **后端API**: http://localhost:8000
- **前端应用**: http://localhost:80

**如果使用Nginx反向代理（生产）**：
- **后端API**: http://your-domain.com/api/v1
- **前端应用**: http://your-frontend-domain.com

---

## 健康检查

### 后端健康检查

```bash
curl http://localhost:8000/health

# 预期响应
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 前端服务检查

```bash
# 检查进程是否运行
ps aux | grep "python.*main.app"  # 后端
ps aux | grep "vite.*--host"  # 前端

# 检查端口是否监听
lsof -i :8000  # 后端
lsof -i :5173  # 前端开发
lsof -i :80    # 前端生产
```

### Docker服务检查

```bash
docker-compose ps

# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart
```

---

## 日志和监控

### 后端日志

**开发环境**：控制台输出

**生产环境**：
- Docker: `docker-compose logs -f backend`
- 系统日志：`/var/log/`（根据配置）

### 前端日志

**开发环境**：控制台输出

**生产环境**：
- Docker: `docker-compose logs -f frontend`
- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`

### 日志级别

生产环境可以通过以下环境变量调整：
- `LOG_LEVEL`: DEBUG, INFO, WARNING, ERROR

---

## 性能优化

### 后端优化

1. 使用异步数据库操作
2. 实现API响应缓存（Redis，可选）
3. 数据库连接池配置
4. 静态资源压缩
5. 启用Gunicorn或uWSGI生产服务器

### 前端优化

1. 生产环境构建优化
2. 启用CDN加速静态资源
3. 启用Gzip压缩传输
4. 启用浏览器缓存策略

---

## 安全配置

### 生产环境安全检查

1. [ ] 修改所有默认密码（admin123, manager123, specialist123, sales123）
2. [ ] 设置强密码策略（最小长度12，包含大小写字母、数字、特殊字符）
3. [ ] 配置HTTPS（生产环境强制）
4. [ ] 设置防火墙规则（仅开放必要端口：80, 8000, 5432）
5. [ ] 定期更新依赖（pip audit, npm audit）
6. [ ] 启用环境变量管理敏感信息（不提交到版本控制）
7. [ ] 启用日志监控系统（Sentry, ELK, CloudWatch等）
8. [ ] 实施数据备份策略

### 安全配置命令

```bash
# 1. 修改密码（通过前端或API）
# 2. 配置HTTPS证书
# 3. 设置防火墙
sudo ufw allow 80/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 5432/tcp
```

---

## 监控和告警

### 建议的监控指标

- 应用健康状态
- API响应时间
- 数据库连接池状态
- 错误率
- 活跃用户数

### 监控工具

- **系统**: Prometheus + Grafana
- **日志**: ELK Stack
- **告警**: AlertManager

---

## 故障排查

### 常见问题

**1. 数据库连接失败**
- 检查PostgreSQL服务状态
- 检查.env配置
- 检查数据库迁移状态

**2. API 401/403错误**
- 检查Token是否有效
- 检查用户权限
- 查看后端日志

**3. 前端路由404**
- 检查权限Token是否正确
- 检检查用户角色权限

**4. 前端样式问题**
- 检检查浏览器兼容性
- 清除浏览器缓存

**5. Docker容器问题**
- 检查容器日志
- 检查网络连接
- 检 检查卷映射

### 调试模式

```bash
# 后端调试
export LOG_LEVEL=DEBUG
python -m sanic main.app --host 0.0.0 --port 8000

# 前端调试（Vite自动支持）
npm run dev

# Docker调试（查看详细日志）
docker-compose logs -f
```

---

## 备份和恢复

### 数据库备份

```bash
# 备份
docker exec postgres pg_dump -U postgres customer_manager > backup_$(date +%Y%m%d).sql

# 恢复
docker exec -i postgres psql -U postgres customer_manager < backup_20260303.sql
```

### 配置备份

```bash
cp .env .env.backup
cp -r backend/ app/config.py config.py.backup
```

---

## 技术支持

### 相关文档

- **后端API文档**: http://localhost:8000/docs（如果配置了）
- **前端文档**: 前�端README.md
- **设计文档**: docs/plans/2026-03-03-customer-manager-design.md

### 常见问题

1. 查看AGENTS.md的开发规则
2. 查看各阶段的实施计划
3. 检查看项目文档

---

## 开发工作流

### 添加新功能

1. 创建或更新实施计划（docs/plans/）
2. 按计划执行开发任务
3. 编写单元测试
4. 更新AGENTS.md
5. Commit代码

### 修复Bug

1. 复现问题
2. 编写修复测试
3. 运行完整测试套件
4. 更新AGENTS.md
5. Commit修复

### 代码审查检查清单

- [ ] 遵循PEP8规范
- [ ] 类型提示完整
- [ ] 函数有文档字符串
- [ ] 错误处理完善
- [ ] 安全检查通过
- [ ] 测试覆盖率达标

---

## 快速开始

### 一键启动所有服务（Docker）

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 本地开发启动

```bash
# 启动后端（终端1）
cd backend
source venv/bin/activate
python -m sanic main.app --host 0.0.0 --port 8000 --reload

# 启动前端（终端2）
cd frontend
npm run dev
```

---

## 版本信息

- **项目版本**: v1.0
- **Python版本**: 3.11
- **Node版本**: 18.x
- **数据库**: PostgreSQL 18
- **前端**: Vue 3
- **测试框架**: pytest + Playwright

---

**更新日期**: 2026-03-03

**维护团队**: 开发团队

---

## 联系信息

如有问题或需要技术支持，请联系维护团队或查看项目文档。
