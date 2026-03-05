# 阶段 1: 项目基础架构搭建

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 搭建项目基础架构,包括目录结构、Docker 配置、后端依赖、前端配置

**预计时间:** 2-3 天

**Architecture:** 
- 创建后端和前端的目录结构
- 配置 Docker Compose 编排
- 初始化后端依赖和配置
- 初始化前端项目配置

**Tech Stack:**
- 后端: Python 3.11, Sanic, SQLAlchemy 2.0
- 前端: Vue 3, Vite, TypeScript, Arco Design
- 部署: Docker, Docker Compose

---

## Task 1: 创建项目目录结构

**Files:**
- Create: `backend/README.md`
- Create: `frontend/README.md`
- Create: `docker-compose.yml`
- Create: `.env.example`
- Create: `.gitignore`

**Step 1: 创建后端目录结构**

```bash
# 执行以下命令创建目录结构
mkdir -p backend/{app/{blueprints,models,services,schemas,utils,middlewares},migrations,tests}
mkdir -p frontend/{src/{views,components,api,stores,router,types,layouts},public}
```

**Step 2: 创建前端子目录**

```bash
# 创建前端子目录
mkdir -p frontend/src/views/{customer,system}
mkdir -p frontend/src/views/login
```

**Step 3: 创建 docker-compose.yml**

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:18
    container_name: customer_manager_db
    environment:
      POSTGRES_USER: ${DB_USER:-customer_manager}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
      POSTGRES_DB: ${DB_NAME:-customer_manager}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-customer_manager}"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: customer_manager_backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER:-customer_manager}:${DB_PASSWORD:-changeme}@postgres:5432/${DB_NAME:-customer_manager}
      - JWT_SECRET=${JWT_SECRET:-your-secret-key}
      - ENVIRONMENT=${ENVIRONMENT:-development}
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
    command: python -m sanic main.app --host 0.0.0.0 --port 8000 --workers 4 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: customer_manager_frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

**Step 4: 创建 .env.example**

```bash
DB_USER=customer_manager
DB_PASSWORD=your_secure_password
DB_NAME=customer_manager
JWT_SECRET=your_jwt_secret_key_here
ENVIRONMENT=development
```

**Step 5: 创建 .gitignore**

```bash
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.venv
env/
venv/
ENV/
*.cover
.pytest_cache/
htmlcov/
.tox/
.hypothesis/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*
dist/
dist-ssr/
*.local

# Environment
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Logs
logs/
*.log

# Database
*.db
*.sqlite3

# OS
.DS_Store
Thumbs.db
```

**Step 6: Commit**

```bash
git add .
git commit -m "feat: create project directory structure"
```

---

## Task 2: 配置后端依赖和初始化

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/Dockerfile`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`

**Step 1: 创建 requirements.txt**

```txt
# Web Framework
sanic==23.6.0
sanic-ext==23.6.0

# Database
sqlalchemy[asyncio]==2.0.25
asyncpg==0.29.0
alembic==1.12.1

# Validation
pydantic==2.5.0
pydantic-settings==2.1.0
email-validator==2.1.0

# Authentication
pyjwt==2.8.0
bcrypt==4.1.1

# Utils
python-dateutil==2.8.2
openpyxl==3.1.2

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2

# Development
black==23.12.0
isort==5.13.2
```

**Step 2: 创建后端 Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "sanic", "main.app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

**Step 3: 创建应用配置文件**

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://customer_manager:changeme@localhost:5432/customer_manager"
    
    # JWT
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_expire_hours: int = 2
    
    # Environment
    environment: str = "development"
    
    # Pagination
    default_page_size: int = 20
    max_page_size: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
```

**Step 4: 创建应用初始化文件**

```python
# backend/app/__init__.py
from sanic import Sanic
from sanic.response import json
from .config import settings
import os


def create_app():
    """应用工厂函数"""
    app = Sanic("customer_manager")
    
    # 加载配置
    app.config.update(
        DATABASE_URL=settings.database_url,
        JWT_SECRET=settings.jwt_secret,
        ENVIRONMENT=settings.environment
    )
    
    # 注册蓝图
    # register_blueprints(app)
    
    # 注册中间件
    # register_middlewares(app)
    
    # 健康检查端点
    @app.get("/health")
    async def health_check(request):
        return json({
            "status": "healthy",
            "version": "1.0.0"
        })
    
    return app


app = create_app()
```

**Step 5: 创建主入口文件**

```python
# backend/main.py
from app import app

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        workers=4,
        debug=True
    )
```

**Step 6: Commit**

```bash
git add backend/
git commit -m "feat: configure backend dependencies and initialization"
```

---

## Task 3: 配置前端项目

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/tsconfig.json`
- Create: `frontend/Dockerfile`
-` frontend/.nginx.conf`

**Step 1: 创建 package.json**

```json
{
  "name": "customer-manager-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vue-tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore"
  },
  "dependencies": {
    "vue": "^3.3.11",
    "vue-router": "^4.2.5",
    "pinia": "^2.1.7",
    "@arco-design/web-vue": "^2.54.0",
    "axios": "^1.6.2",
    "dayjs": "^1.11.10"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "typescript": "^5.3.3",
    "vue-tsc": "^1.8.27",
    "vite": "^5.0.10",
    "@types/node": "^20.10.6"
  }
}
```

**Step 2: 创建 vite.config.ts**

```typescript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

**Step 3: 创建 tsconfig.json**

```json
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "preserve",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["src/**/*.ts", "src/**/*.d.ts", "src/**/*.tsx", "src/**/*.vue"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
```

**Step 4: 创建前端 Dockerfile**

```dockerfile
# 构建阶段
FROM node:18-alpine as build

WORKDIR /app

# 复制 package.json 和 package-lock.json
COPY package.json ./
COPY package-lock.json* ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建
RUN npm run build

# 生产阶段
FROM nginx:alpine

# 复制 nginx 配置
COPY .nginx.conf /etc/nginx/conf.d/default.conf

# 复制构建产物
COPY --from=build /app/dist /usr/share/nginx/html

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]
```

**Step 5: 创建 nginx 配置**

```nginx
server {
    listen 80;
    server_name localhost;

    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
}
```

**Step 6: 创建基础前端文件**

```html
<!-- frontend/index.html -->
<!DOCTYPE html>
<html lang="zh-CN">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>客户运营中台</title>
  </head>
  <body>
    <div id="app"></div>
    <script type="module" src="/src/main.ts"></script>
  </body>
</html>
```

```typescript
// frontend/src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.mount('#app')
```

```vue
<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
</script>
```

**Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: configure frontend project"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 1 即可视为完成:

- [ ] 项目目录结构已创建
- [ ] Docker Compose 配置文件已创建
- [ ] .env.example 文件已创建
- [ ] .gitignore 文件已创建
- [ ] 后端 requirements.txt 已创建
- [ ] 后端 Dockerfile 已创建
- [ ] 后端应用配置文件已创建
- [ ] 后端初始化文件已创建
- [ ] 前端 package.json 已创建
- [ ] 前端 vite.config.ts 已创建
- [ ] 前端 tsconfig.json 已创建
- [ ] 前端 Dockerfile 已创建
- [ ] 前端 nginx 配置已创建
- [ ] 所有文件已提交到 Git

---

## 下一步

完成阶段 1 后,请继续执行 **阶段 2: 数据库设计与迁移**

`docs/plans/2026-03-03-customer-manager-phase2-database.md`
