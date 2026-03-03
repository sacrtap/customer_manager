# 客户信息管理与运营系统 - 系统设计文档

**项目名称**: 内部运营中台客户信息管理与运营系统
**设计版本**: v1.0
**创建日期**: 2026-03-03
**设计者**: OpenCode AI Assistant
**状态**: 已确认

---

## 目录

1. [执行摘要](#执行摘要)
2. [系统架构设计](#系统架构设计)
3. [数据库设计](#数据库设计)
4. [API 设计](#api-设计)
5. [前端组件设计](#前端组件设计)
6. [数据流程设计](#数据流程设计)
7. [部署与运维设计](#部署与运维设计)
8. [实施计划](#实施计划)

---

## 执行摘要

### 项目背景

内部运营中台客户信息管理与运营系统是一个企业内部 Web 应用,旨在解决客户数据分散、运营效率低下、客户流失风险高的核心问题。

**核心问题**:
- 1320 个客户数据分散在 Excel 中,缺乏统一管理
- 运营团队每月花费 3 天手工生成结算单,数据不准确
- 193 个僵尸账号(14.6%)未被识别,客户流失风险高
- 93.6% 的客户未进行价值评级,无法精细化运营

**核心价值**:
- 客户数据集中管理,告别 Excel 分散模式
- 多维度查询,快速定位客户
- 数据权限控制,保障数据安全
- RBAC 权限管理,灵活配置用户权限

### 技术选型

| 层级   | 技术栈                                          | 说明            |
| ------ | ----------------------------------------------- | --------------- |
| 前端   | Vue 3 + Vite + TypeScript + Arco Design + Pinia | 企业级 SPA 应用 |
| 后端   | Python 3.11 + Sanic + SQLAlchemy 2.0 + Pydantic | 异步 Web 框架   |
| 数据库 | PostgreSQL 18                                   | 关系型数据库    |
| 部署   | Docker + Docker Compose                         | 容器化部署      |

### 实施策略

**一期 MVP (2.5 个月)**:
- 基础系统能力(认证/权限/RBAC/日志/备份)
- 客户主数据管理(MDM)
  - 多维度查询
  - 增删改查
  - 批量导入导出

**二期 (后续 6 个月)**:
- 客户健康度监控
- 客户价值评估
- 客户转移功能
- 设备与定价数据管理
- 结算自动化引擎

---

## 系统架构设计

### 整体架构

采用前后端分离的模块化单体架构:

```
┌─────────────────────────────────────────────────────────────┐
│                        前端层                              │
│                  Vue 3 SPA (Vite)                           │
│ 中间件: Nginx 静态文件服务                               │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP/RESTful
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        应用层                              │
│                  Sanic (Python 3.11)                        │
│  - 蓝图模块: customer, auth, system, rbac               │
│  - 服务层: 业务逻辑封装                                   │
│  - 验证层: Pydantic 数据验证                             │
└─────────────────────────────────────────────────────────────┘
                            │ SQLAlchemy ORM
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                        数据层                              │
│                PostgreSQL 18 (UTF-8)                        │
│  - 核心表: customers, users, roles, permissions          │
│  - 索引优化: 复合索引,覆盖索引                         │
└─────────────────────────────────────────────────────────────┘
```

### 前端架构

**目录结构**:
```
frontend/
├── src/
│   ├── views/              # 页面视图模块
│   │   ├── Login.vue              # 登录页
│   │   ├── Dashboard.vue           # Dashboard 页
│   │   ├── Profile.vue            # 个人信息页
│   │   ├── ChangePassword.vue      # 修改密码页
│   │   ├── customer/              # 客户管理
│   │   │   ├── CustomerList.vue
│   │   │   ├── CustomerDetail.vue
│   │   │   └── CustomerImport.vue
│   │   └── system/                # 系统管理
│   │       ├── UserManage.vue
│   │       ├── RoleManage.vue     # 角色管理
│   │       └── LogView.vue
│   ├── layouts/             # 布局组件
│   │   └── MainLayout.vue        # 主布局
│   ├── components/          # 公共组件
│   │   ├── CommonTable.vue
│   │   ├── SearchBar.vue
│   │   └── Pagination.vue
│   ├── api/                # API 调用封装
│   │   ├── customer.ts
│   │   └── auth.ts
│   ├── stores/             # Pinia 状态管理
│   │   └── user.ts
│   ├── router/             # 路由配置
│   │   └── index.ts
│   ├── types/              # TypeScript 类型定义
│   │   └── api.ts
│   └── main.ts
├── package.json
└── vite.config.ts
```

### 后端架构

**目录结构**:
```
backend/
├── app/
│   ├── __init__.py       # Sanic 应用工厂
│   ├── config.py          # 配置管理
│   ├── blueprints/        # 蓝图模块
│   │   ├── customer.py    # 客户管理
│   │   ├── auth.py       # 认证授权
│   │   ├── system.py     # 系统管理
│   │   └── rbac.py       # RBAC 权限管理
│   ├── models/            # SQLAlchemy 模型
│   │   ├── customer.py
│   │   ├── user.py
│   │   ├── role.py
│   │   ├── permission.py
│   │   └── operation_log.py
│   ├── services/          # 业务逻辑层
│   │   ├── customer_service.py
│   │   ├── auth_service.py
│   │   └── rbac_service.py
│   ├── schemas/           # Pydantic 验证模式
│   │   ├── customer.py
│   │   ├── user.py
│   │   └── common.py
│   ├── utils/             # 工具函数
│   │   ├── auth.py        # JWT 工具
│   │   ├── pagination.py  # 分页工具
│   │   └── excel.py       # Excel 处理
│   └── middlewares/       # 中间件
│       ├── auth.py        # 认证中间件
│       ├── rbac.py        # RBAC 中间件
│       ├── logging.py     # 日志中间件
│       └── error.py       # 错误处理中间件
├── migrations/            # Alembic 数据库迁移
├── tests/                 # 测试用例
├── requirements.txt
└── main.py               # 应用入口
```

---

## 数据库设计

### 核心数据表

#### 1. 客户表 (customers)

```sql
CREATE TABLE customers (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL,                          -- 客户名称
    code VARCHAR(50) UNIQUE,                              -- 客户编码
    industry VARCHAR(100),                               -- 行业
    sales_rep_id BIGINT NOT NULL,                        -- 负责销售 ID
    tier_level VARCHAR(1) DEFAULT 'D' CHECK (tier_level IN ('S', 'A', 'B', 'C', 'D')),
    annual_consumption DECIMAL(15, 2) DEFAULT 0,         -- 年消费金额
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    contact_person VARCHAR(100),                          -- 联系人
    contact_phone VARCHAR(20),                            -- 联系电话
    contact_email VARCHAR(255),                           -- 联系邮箱
    address TEXT,                                        -- 地址
    remark TEXT,                                         -- 备注
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    INDEX idx_sales_rep (sales_rep_id),
    INDEX idx_code (code),
    INDEX idx_tier (tier_level),
    INDEX idx_status (status),
    INDEX idx_sales_tier (sales_rep_id, tier_level)
);
```

#### 2. 用户表 (users)

```sql
CREATE TABLE users (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    INDEX idx_status (status)
);
```

#### 3. 角色表 (roles)

```sql
CREATE TABLE roles (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(50) NOT NULL UNIQUE,              -- 角色名称
    code VARCHAR(50) NOT NULL UNIQUE,              -- 角色代码
    description VARCHAR(255),                       -- 角色描述
    permissions JSONB NOT NULL DEFAULT '[]',         -- 权限列表
    is_system BOOLEAN DEFAULT FALSE,                 -- 是否系统角色(不可删除)
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    INDEX idx_code (code)
);

-- 初始化系统角色
INSERT INTO roles (name, code, description, permissions, is_system) VALUES
('超级管理员', 'admin', '系统最高权限', '["*"]', true),
('运营经理', 'manager', '运营团队经理', '["customer.*", "user.*", "system.*"]', true),
('运营专员', 'specialist', '运营团队专员', '["customer.*", "customer.export.*"]', true),
('销售人员', 'sales', '销售团队成员', '["customer.view.*", "customer.view.self"]', true);
```

#### 4. 用户角色关联表 (user_roles)

```sql
CREATE TABLE user_roles (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    role_id BIGINT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    UNIQUE KEY uk_user_role (user_id, role_id),
    INDEX idx_user (user_id),
    INDEX idx_role (role_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(id) ON DELETE CASCADE
);
```

#### 5. 权限定义表 (permissions)

```sql
CREATE TABLE permissions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(100) NOT NULL UNIQUE,           -- 权限名称
    code VARCHAR(100) NOT NULL UNIQUE,           -- 权限代码
    module VARCHAR(50) NOT NULL,                -- 所属模块
    description VARCHAR(255),                    -- 权限描述
    parent_id BIGINT,                           -- 父权限 ID (用于权限树)
    is_active BOOLEAN DEFAULT TRUE,               -- 是否启用
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    INDEX idx_module (module),
    INDEX idx_parent (parent_id),
    FOREIGN KEY (parent_id) REFERENCES permissions(id)
);

-- 初始化权限
INSERT INTO permissions (name, code, module, description) VALUES
-- 客户管理权限
('客户管理', 'customer', 'customer', '客户管理模块'),
('查看客户', 'customer.view', 'customer', '查看客户列表和详情'),
('新增客户', 'customer.create', 'customer', '新增客户'),
('编辑客户', 'customer.update', 'customer', '编辑客户信息'),
('删除客户', 'customer.delete', 'customer', '删除客户'),
('导出客户', 'customer.export', 'customer', '导出客户数据'),
('导入客户', 'customer.import', 'customer', '导入客户数据'),

-- 用户管理权限
('用户管理', 'user', 'user', '用户管理模块'),
('查看用户', 'user.view', 'user', '查看用户列表和详情'),
('新增用户', 'user.create', 'user', '新增用户'),
('编辑用户', 'user.update', 'user', '编辑用户信息'),
('删除用户', 'user.delete', 'user', '删除用户'),

-- 系统管理权限
('系统管理', 'system', 'system', '系统管理模块'),
('查看日志', 'system.log.view', 'system', '查看操作日志'),
('数据备份', 'system.backup', 'system', '执行数据备份'),
('数据恢复', 'system.restore', 'system', '执行数据恢复'),

-- RBAC 管理权限
('权限管理', 'rbac', 'rbac', '权限管理模块'),
('角色管理', 'rbac.role', 'rbac', '管理角色和权限'),
('用户角色分配', 'rbac.user_role', 'rbac', '为用户分配角色');
```

#### 6. 操作日志表 (operation_logs)

```sql
CREATE TABLE operation_logs (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id BIGINT NOT NULL,
    operation_type VARCHAR(100) NOT NULL,
    target_type VARCHAR(100),
    target_id BIGINT,
    old_value JSONB,
    new_value JSONB,
    ip_address VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW NOW(),

    INDEX idx_user (user_id),
    INDEX idx_type (operation_type),
    INDEX idx_created (created_at DESC)
);
```

### 数据库索引策略

1. **复合索引**: `(sales_rep_id, tier_level)` 用于查询销售的高价值客户
2. **唯一索引**: `customer.code` 用于快速查找
3. **覆盖索引**: 针对高频查询优化

---

## API 设计

### API 规范

- **风格**: RESTful
- **版本**: `/api/v1/`
- **认证**: JWT Bearer Token
- **响应格式**: 统一 JSON 格式

### 统一响应格式

**成功响应**:
```json
{
  "data": {
    "id": 12345,
    "name": "XX 科技公司"
  },
  "timestamp": "2026-03-03T10:00:00Z"
}
```

**错误响应**:
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "数据验证失败",
    "details": [
      {
        "field": "customer_name",
        "message": "客户名称不能为空"
      }
    ],
    "timestamp": "2026-03-03T10:00:00Z",
    "path": "/api/v1/customers"
  }
}
```

### 核心 API 端点

#### 认证模块
```
POST   /api/v1/auth/login           # 用户登录
POST   /api/v1/auth/refresh         # 刷新 Token
POST   /api/v1/auth/logout          # 用户登出
GET    /api/v1/auth/me              # 获取当前用户信息
```

#### 客户管理模块
```
GET    /api/v1/customers                # 客户列表(多维度查询)
POST   /api/v1/customers                # 新增客户
GET    /api/v1/customers/{id}           # 客户详情
PUT    /api/v1/customers/{id}           # 更新客户
DELETE /api/v1/customers/{id}           # 删除客户
POST   /api/v1/customers/import          # 批量导入(Excel)
GET    /api/v1/customers/export          # 批量导出(Excel)
GET    /api/v1/customers/import-template  # 下载导入模板
```

#### 系统管理模块
```
GETGET    /api/v1/system/users              # 用户列表
POST   /api/v1/system/users              # 新增用户
PUT    /api/v1/system/users/{id}         # 更新用户
DELETE /api/v1/system/users/{id}         # 删除用户
GET    /api/v1/system/logs               # 操作日志
POST   /api/v1/system/backup            # 手动备份

GET    /api/v1/system/roles              # 角色列表
POST   /api/v1/system/roles              # 创建创建角色
PUT    /api/v1/system/roles/{id}         # 更新角色
DELETE /api/v1/system/roles/{id}         # 删除角色
GET    /api/v1/system/permissions        # 权限列表
POST   /api/v1/system/users/{id}/roles   # 分配角色
```

#### RBAC 管理模块
```
GET    /api/rbac/roles                # 角色列表
POST   /api/rbac/roles                # 创建角色
GET    /api/rbac/roles/{id}           # 角色详情
PUT    /api/rbac/roles/{id}           # 更新角色
DELETE /api/rbac/roles/{id}           # 删除角色
POST   /api/rbac/roles/{id}/permissions  # 为角色分配权限

GET    /api/rbac/permissions           # 权限列表(树形结构)
GET    /api/rbac/permissions/{id}      # 权限详情

GET    /api/rbac/users/{user_id}/roles          # 获取用户角色
POST   /api/rbac/users/{user_id}/roles          # 为用户分配角色
DELETE /api/rbac/users/{user_id}/roles/{role_id}  # 移除用户角色
```

### 客户查询参数 Schema

```python
class CustomerQuerySchema(BaseModel):
    # 分页参数
    page: int = 1
    size: int = 20

    # 基础搜索
    keyword: Optional[str] = None  # 模糊搜索(客户名称/编码/联系人)

    # 高级筛选
    sales_rep_ids: Optional[List[int]] = None   # 所属销售 ID 列表
    industries: Optional[List[str]] = None     # 行业列表
    status: Optional[List[str]] = None         # 客户状态列表
    tier_levels: Optional[List[str]] = None    # 价值等级列表(S/A/B/C/D)

    # 数值范围
    annual_consumption_min: Optional[float] = None  # 年消费金额最小值
    annual_consumption_max: Optional[float] = None  # 年消费金额最大值

    # 时间范围
    created_at_start: Optional[datetime] = None
    created_at_end: Optional[datetime] = None
    updated_at_start: Optional[datetime] = None
    updated_at_end: Optional[datetime] = None

    # 排序
    sort_field: Optional[str] = None    # 排序字段(name/created_at/updated_at/annual_consumption)
    sort_desc: bool = False             # 是否降序
```

---

## 前端组件设计

### 核心页面组件

#### 1. 主布局 (MainLayout.vue)

**功能**:
- 顶部导航栏(应用标题、用户信息、退出登录)
- 侧边栏菜单(功能导航)
- 内容区域(路由页面渲染)
- 响应式设计

#### 2. Dashboard 页面 (Dashboard.vue)

**功能**:
- 欢迎卡片(用户信息、角色展示)
- 快捷入口卡片(客户管理、批量导入、操作日志、用户管理)
- 最近操作记录列表
- 权限控制(根据用户权限显示/隐藏功能)

#### 3. 客户列表页 (CustomerList.vue)

**功能**:
- 多维度查询
  - 关键词模糊搜索(客户名称/编码/联系人)
  - 所属销售筛选
  - 行业筛选
  - 客户状态筛选
  - 价值等级筛选(S/A/B/C/D)
  - 年消费金额范围
  - 创建时间范围
  - 更新时间范围
- 分页展示
- 字段排序(客户名称/创建时间/更新时间/年消费)
- 行操作(查看/编辑/删除)

#### 4. 客户详情页 (CustomerDetail.vue)

**功能**:
- 基本信息展示和编辑
- 联系信息管理
- 操作历史记录

#### 5. 客户导入页 (CustomerImport.vue)

**功能**:
- Excel 文件上传
- 数据验证
- 错误报告生成
- 导入进度展示

#### 6. 用户管理页 (UserManage.vue)

**功能**:
- 用户列表
- 用户增删改查
- 角色分配
- 权限管理

#### 7. 角色管理页 (RoleManage.vue)

**功能**:
- 角色列表
- 角色增删改查
- 权限分配(树形结构)
- 权限管理

#### 8. 日志查看页 (LogView.vue)

**功能**:
- 操作日志列表
- 日志查询和筛选
- 日志详情查看

#### 9. 个人信息页 (Profile.vue)

**功能**:
- 查看和编辑个人信息
- 修改密码

#### 10. 修改密码页 (ChangePassword.vue)

**功能**:
- 输入原密码
- 设置新密码
- 确认新密码

### 公共组件

- **CommonTable**: 通用表格(支持分页、排序、行选择)
- **SearchBar**: 搜索栏(支持多种输入类型)
- **StatCard**: 统计卡片
- **Pagination**: 分页组件

---

## 数据流程设计

### 核心业务流程

#### 1. 用户登录流程
```
用户输入用户名密码
    ↓
前端验证
    ↓
提交后端 API
    ↓
后端验证用户名密码
    ↓
生成 JWT Token
    ↓
返回用户信息和权限列表
    ↓
前端保存到本地存储
    ↓
跳转到 Dashboard
```

#### 2. 退出登录流程
```
用户点击退出登录
    ↓
前端弹出确认对话框
    ↓
用户确认
    ↓
调用后端登出 API
    ↓
清除服务器端 Token
    ↓
前端清除本地存储
    ↓
跳转到登录页
```

#### 3. 客户数据创建流程
```
用户填写表单
    ↓
前端验证 (Pydantic Schema)
    ↓
提交后端 API
    ↓
后端验证 (Pydantic)
    ↓
创建客户记录
    ↓
记录操作日志
    ↓
返回成功响应
```

#### 4. 客户多维度查询流程
```
用户输入查询条件
    ↓
前端构建查询参数
    ↓
提交后端 API
    ↓
后端应用权限过滤
    ↓
应用查询条件
    ↓
执行分页查询
    ↓
返回结果
```

#### 5. 批量导入流程
```
上传 Excel 文件
    ↓
前端验证文件格式
    ↓
上传到后端
    ↓
后端解析 Excel
    ↓
数据验证
    ↓
批量插入数据库
    ↓
记录操作日志
    ↓
返回导入结果
```

#### 6. RBAC 权限检查流程
```
用户发起请求
    ↓
中间件验证 JWT Token
    ↓
提取用户信息
    ↓
检查用户权限
    ↓
权限通过 → 继续处理请求
    ↓
权限拒绝 → 返回 403 Forbidden
```

---

## 部署与运维设计

### Docker Compose 部署架构

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:18
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: customer_manager
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER}"]
      interval: 10s

  backend:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql+asyncpg://${DB_USER}:${DB_PASSWORD}@postgres:5432/customer_manager
      - JWT_SECRET=${JWT_SECRET}
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    build: ./frontend
    ports:
      - "80:80"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### 环境配置

**.env 文件**:
```bash
DB_USER=customer_manager
DB_PASSWORD=your_secure_password
JWT_SECRET=your_jwt_secret_key_here
ENVIRONMENT=production
```

### 数据备份策略

**每日自动备份**:
```bash
#!/bin/bash
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U ${DB_USER} customer_manager > ${BACKUP_DIR}/backup_${DATE}.sql

# 保留最近 30 天的备份
find ${BACKUP_DIR} -name "backup_*.sql" -mtime +30 -delete
```

---

## 实施计划

### MVP 开发计划((一期, 2.5 个月)

| 阶段       | 时间        | 目标                    | 交付物                       |
| ---------- | ----------- | ----------------------- | ---------------------------- |
| **Sprint 1-2** | 第 1-4 周   | 基础架构 + 认证系统     | 用户认证、权限管理、操作日志、RBAC |
| **Sprint 3-4** | 第 5-8 周   | 客户 MDM 核心           | 客户增删改查、列表展示       |
| **Sprint 5-6** | 第 9-12 周  | 批量导入导出 + 用户管理 | Excel 导入导出、用户管理、角色管理 |
| **Sprint 7**   | 第 13-14 周 | 测试优化 + 数据迁移     | 测试修复、性能优化           |
| **上线准备**   | 第 15 周    | 数据迁移、培训、上线    | 系统上线、用户培训           |

### 关键里程碑

- 第 4 周: 基础架构完成,认证系统可用
- 第 8 周: 客户 MDM 核心功能完成
- 第 12 周: 批量导入导出和用户管理完成
- 第 14 周: 集成测试完成,准备上线
- 第 15 周: 系统上线,数据迁移完成

### 二期计划(后续 6 个月)

1. 客户健康度监控(僵尸账号识别、风险预警)
2. 客户价值评估(定级规则配置、自动重算)
3. 客户转移功能
4. 设备与定价数据管理(3 种结算模式)
5. 结算自动化引擎

---

## 附录

### A. 权限矩阵

| 功能         | Admin | 经理 | 专员 | 销售       |
| ------------ | ----- | ---- | ---- | ---------- |
| 客户列表查看 | ✅    | ✅   | ✅   | ✅(仅自己) |
| 客户详情查看 | ✅    | ✅   | ✅   | ✅(仅自己) |
| 客户新增     | ✅    | ✅   | ✅   | ❌         |
| 客户编辑     | ✅    | ✅   | ✅   | ❌         |
| 客户删除     | ✅    | ✅   | ✅   | ❌         |
| 数据导出     | ✅    | ✅   | ✅   | ✅(仅自己) |
| 数据导入     | ✅    | ✅   | ✅   | ❌         |
| 用户管理     | ✅    | ❌   | ❌   | ❌         |
| 角色管理     | ✅    | ❌   | ❌   | ❌         |
| 权限管理     | ✅    | ❌   | ❌   | ❌         |
| 系统设置     | ✅    | ❌   | ❌   | ❌         |

### B. 数据迁移计划

**迁移目标**: 将 1320 个客户数据从 Excel 迁移至 PostgreSQL,数据完整性≥99%

**迁移策略**: 三阶段迁移法
- 阶段 1: 迁移准备(第 4-6 周)
- 阶段 2: 迁移演练(第 7-9 周,3 轮)
- 阶段 3: 正式迁移(第 15 周)

### C. 技术债务管理

**已知妥协**:
1. 定时轮询替代 WebSocket(预警延迟最高 5 分钟)
2. 基础可访问性(满足基本需求)
3. 现代浏览器支持(不支持 IE11)

**未来优化机会**:
1. 实时通知(用户量增长后升级为 WebSocket)
2. 高级可访问性(提升到 WCAG AA)
3. 缓存优化(引入 Redis 缓存)
4. 读写分离(数据量增长后考虑主从复制)

---

**文档版本**: v1.0
**最后更新**: 2026-03-03
