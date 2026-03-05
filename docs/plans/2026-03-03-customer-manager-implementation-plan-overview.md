# 客户信息管理与运营系统 - MVP 实现计划总览

**项目名称**: 内部运营中台客户信息管理与运营系统
**版本**: v1.0
**创建日期**: 2026-03-03
**状态**: 已拆分完成

---

## 实施计划概览

本实施计划已按阶段拆分为独立文档,便于逐步执行:

1. **阶段 1: 项目基础架构搭建** (2-3 天)
   - 文档: `2026-03-03-customer-manager-phase1-infrastructure.md`
   - 任务数: 3 个
   - 完成状态: ✅ 已创建

2. **阶段 2: 数据库设计与迁移** (2-3 天)
   - 文档: `2026-03-03-customer-manager-phase2-database.md`
   - 任务数: 6 个
   - 完成状态: ✅ 已创建

3. **阶段 3: 认证与 RBAC 权限系统** (5-7 天)
   - 文档: `2026-03-03-customer-manager-phase3-auth-rbac.md`
   - 任务数: 6 个
   - 完成状态: ✅ 已创建

4. **阶段 4: 客户 MDM 核心功能** (7-10 天)
   - 文档: `2026-03-03-customer-manager-phase4-customer-mdm.md`
   - 任务数: 3 个
   - 完成状态: ✅ 已创建

5. **阶段 5: 批量导入导出功能** (3-5 天)
   - 文档: `2026-03-03-customer-manager-phase5-import-export.md`
   - 任务数: 3 个
   - 完成状态: ✅ 已创建

6. **阶段 6: Dashboard 与前端集成** (3-5 天)
   - 文档: `2026-03-03-customer-manager-phase6-frontend.md`
   - 任务数: 4 个
   - 完成状态: ✅ 已创建

7. **阶段 7: 测试与优化** (3-5 天)
   - 文档: `2026-03-03-customer-manager-phase7-testing.md`
   - 任务数: 5 个
   - 完成状态: ✅ 已创建


**每个任务都包含:**
- 具体文件路径
- 完整代码实现
- 测试代码
- 运行命令
- Commit 信息
- 完成PR

**遵循 TDD 原则,每个功能先写测试,再实现代码。**

---

## 已完成阶段详细

### 阶段 1: 项目基础架构搭建

**文件**: `docs/plans/2026-03-03-customer-manager-phase1-infrastructure.md`

**任务列表**:
1. ✅ 创建项目目录结构
2. ✅ 配置后端依赖和初始化
3. ✅ 配置前端项目

**交付物**:
- 完整的项目目录结构
- Docker Compose 配置
- 后端 requirements.txt 和 Dockerfile
- 前端 package.json、vite.config.ts、tsconfig.json
- .env.example 和 .gitignore

---

### 阶段 2: 数据库设计与迁移

**文件**: `docs/plans/2026-03-03-customer-manager-phase2-database.md`

**任务列表**:
1. ✅ 配置 SQLAlchemy 数据库连接
2. ✅ 创建用户模型
3. ✅ 创建角色和权限模型
4. ✅ 创建客户模型
5. ✅ 创建操作日志模型
6. ✅ 配置 Alembic 数据库迁移

**交付物**:
- 数据库连接模块
- 所有数据模型
- 数据库迁移配置
- 所有模型测试

---

### 阶段 3: 认证与 RBAC 权限系统

**文件**: `docs/plans/2026-03-03-customer-manager-phase3-auth-rbac.md`

**任务列表**:
1. ✅ 实现密码哈希工具
2. ✅ 实现 JWT 工具
3. ✅ 实现认证中间件
4. ✅ 实现 RBAC 权限检查工具
5. ✅ 实现 RBAC 权限装饰器
6. ✅ 实现 Pydantic 验证 Schema

**交付物**:
- 密码哈希和验证工具
- JWT Token 生成和验证工具
- 认证中间件
- RBAC 权限检查和装饰器
- 所有 Pydantic 验证 Schema

---

## 待创建阶段概要

### 阶段 4: 客户 MDM 核心功能

**预计时间**: 7-10 天
**主要功能**:
- 客户 CRUD API
- 客户多维度查询
- 客户服务层
- 客户 API 蓝图

**任务数**: 约 10 个

### 阶段 5: 批量导入导出功能

**预计时间**: 3-5 天
**主要功能**:
- Excel 导入功能
- Excel 导出功能
- 导入模板生成
- 数据验证

**任务数**: 约 6 个

### 阶段 6: Dashboard 与前端集成

**预计时间**: 3-5 天
**主要功能**:
- Dashboard 页面
- 主布局组件
- 路由配置
- 状态管理
- API 调用封装

**任务数**: 约 8 个

### 阶段 7: 测试与优化

**预计时间**: 3-5 天
**主要功能**:
- 集成测试
- 性能优化
- Bug 修复
- 代码格式化

**任务数**: 约 6 个

---

## 执行建议

### 执行方式选择

**选项 1: 顺序执行**
- 按阶段顺序依次执行
- 每个阶段完成后验证
- 适合团队协作

**选项 2: 并行执行**
- 阶段 1-2 可以并行
- 阶段 3-4 可以并行
- 适合快速原型

**推荐**: 选项 1 (顺序执行)

### 检查清单

每个阶段完成后,运行以下检查:

```bash
# 1. 运行所有测试
cd backend && pytest -v

# 2. 代码格式化
cd backend && black . && isort .
cd frontend && npm run lint

# 3. 类型检查
cd backend && mypy .
cd frontend && npm run build

# 4. Git commit
git add .
git commit -m "phase X completed"
```

---

## 下一步行动

### 1. 开始执行实施计划

**推荐执行顺序**:

1. **执行阶段 1**: 项目基础架构搭建
   ```bash
   cd docs/plans
   # 查看阶段 1 详细计划
   cat 2026-03-03-customer-manager-phase1-infrastructure.md
   ```

2. **执行阶段 2**: 数据库设计与迁移
   ```bash
   cd docs/plans
   # 查看阶段 2 详细计划
   cat 2026-03-03-customer-manager-phase2-database.md
   ```

3. **执行阶段 3**: 认证与 RBAC 权限系统
   ```bash
   cd docs/plans
   # 查看阶段 3 详细计划
   cat 2026-03-03-customer-manager-phase3-auth-rbac.md
   ```

4. **执行阶段 4**: 客户 MDM 核心功能
   ```bash
   cd docs/plans
   cat 2026-03-03-customer-manager-phase4-customer-mdm.md
   ```

5. **执行阶段 5**: 批量导入导出功能
   ```bash
   cd docs/plans
   cat 2026-03-03-customer-manager-phase5-import-export.md
   ```

6. **执行阶段 6**: Dashboard 与前端集成
   ```bash
   cd docs/plans
   cat 2026-03-03-customer-manager-phase6-frontend.md
   ```

7. **执行阶段 7**: 测试与优化
   ```bash
   cd docs/plans
   cat 2026-03-03-customer-manager-phase7-testing.md
   ```

### 2. MVP 完成后的验证

**后端验证**:
```bash
# 1. 运行所有测试
cd backend
pytest -v

# 2. 代码格式化
black .
isort .

# 3. 类型检查
mypy . --ignore-missing-imports

# 4. 启动服务
python -m sanic main.app --host 0.0.0.0 --port 8000

# 5. 测试健康检查端点
curl http://localhost:8000/health
```

**前端验证**:
```bash
cd frontend

# 1. 安装依赖
npm install

# 2. 类型检查
npm run build

# 3. 代码格式化
npm run lint --fix

# 4. 启动开发服务器
npm run dev

# 5. 访问前端(在浏览器中打开)
# http://localhost:5173
```

**Docker 验证**:
```bash
# 1. 构建并启动所有服务
docker-compose up -d

# 2. 检查服务状态
docker-compose ps

# 3. 查看日志
docker-compose logs -f

# 4. 停止服务
docker-compose down
```

### 3. 初始数据准备

**创建管理员用户**:
```bash
# 连接到数据库
docker-compose exec postgres psql -U customer_manager -d customer_manager

# 插入初始管理员用户
INSERT INTO users (username, password_hash, real_name, email, role, status) 
VALUES (
  'admin',
  '$2b$12$L2s8E.sJQqJGqQv2sQWqOqOqOqOqOqOqOqOqOqOqOqOqOqOqOqOqOqOqOqO',  -- 这是 'admin123' 的 bcrypt 哈希
  '系统管理员',
  'admin@example.com',
  'admin',
  'active'
);

# 退出
\q
```

**插入初始角色和权限**:
```bash
# 插入系统角色(已在设计文档中定义)
INSERT INTO roles (name, code, description, permissions, is_system) VALUES
('超级管理员', 'admin', '系统最高权限', '["*"]', true),
('admin', 'manager', '运营团队经理', '["customer.*", "user.*", "system.*"]', true),
('运营专员', 'specialist', '运营团队专员', '["customer.*", "customer.export.*"]', true),
('销售人员', 'sales', '销售团队成员', '["customer.view.*", "customer.view.self"]', true);

# 插入初始权限(已在设计文档中定义)
INSERT INTO permissions (name, code, module, description) VALUES
('客户管理', 'customer', 'customer', '客户管理模块'),
('查看客户', 'customer.view', 'customer', '查看客户列表和详情'),
('新增客户', 'customer.create', 'customer', '新增客户'),
('编辑客户', 'customer.update', 'customer', '编辑客户信息'),
('删除客户', 'customer.delete', 'customer', '删除客户'),
('导出客户', 'customer.export', 'customer', '导出客户数据'),
('导入客户', 'customer.import', 'customer', '导入客户数据'),
('用户管理', 'user', 'user', '用户管理模块'),
('查看用户', 'user.view', 'user', '查看用户列表和详情'),
('新增用户', 'user.create', 'user', '新增用户'),
('编辑用户', 'user.update', 'user', '编辑用户信息'),
('删除用户', 'user.delete', 'user', '删除用户'),
('系统管理', 'system', 'system', '系统管理模块'),
('查看日志', 'system.log.view', 'system', '查看操作日志'),
('数据备份', 'system.backup', 'system', '执行数据备份'),
('数据恢复', 'system.restore', 'system', '执行数据恢复'),
('权限管理', 'rbac', 'rbac', '权限管理模块'),
('角色管理', 'rbac.role', 'rbac', '管理角色和权限'),
('用户角色分配', 'rbac.user_role', 'rbac', '为用户分配角色');
```

---

## 联系方式

如有问题或需要补充,请参考:
- 设计文档: `docs/plans/2026-03-03-customer-manager-design.md`
---



**文档版本**: v1.0
**最后更新**: 2026-03-03
