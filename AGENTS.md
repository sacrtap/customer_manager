# AGENTS.md

## 交互要求
- Thinking/Reply 均使用中文
- Use context7 for code generation/API docs
- 错误修复后总结更新至本文件
- 项目有关键技术变更时，需及时更新 AGENTS.md

## Project Status
Customer Manager - 客户管理系统 (Vue 3 + TypeScript + Sanic + SQLAlchemy Async + PostgreSQL)

## 文档编辑
- 所有文档均采用 Markdown 格式
- 代码示例采用反引号 (```) 包裹
- 文档编写以中文为主，关键术语可保留

## Build, Lint, Test Commands

### Backend (Python 3.11+)
```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt

# 测试
pytest                              # 全部测试
pytest tests/test_health_api.py     # 单个文件
pytest tests/test_health_api.py::test_health_check -v  # 单个函数
pytest -k "transfer" -v             # 关键字匹配

# Lint & Format
black . --check && isort . --check-only
black . && isort .                  # 格式化
```

### Frontend (Node.js 18+)
```bash
cd frontend
npm install
npm run dev                         # 开发模式
npm run build                       # 构建
npm run lint                        # Linting
```

### E2E Tests (Playwright)
```bash
cd frontend
npx playwright test                 # 全部测试
npx playwright test tests/e2e/example.spec.ts  # 单个文件
npx playwright test --headed        # 有头调试
```

## Code Style Guidelines

### Naming
- **JS/TS**: `camelCase` (变量/函数), `PascalCase` (类/类型), `UPPER_SNAKE_CASE` (常量)
- **Python**: `snake_case` (变量/函数), `PascalCase` (类), `UPPER_SNAKE_CASE` (常量)
- **Files**: `kebab-case` 或 `snake_case`

### Imports
- 顺序：标准库 → 第三方 → 本地模块
- 组内按字母排序，组间空行分隔

### Types
- 禁止 `any`，使用具体类型
- 函数参数和返回值必须有类型注解
- TypeScript 启用 strict 模式

### Error Handling
- 禁止静默吞掉错误
- 错误信息包含上下文（发生了什么 + 原因）
- 使用语言特定的错误类型

## Testing Rules (重要)

1. **Git Worktree**: 文件操作必须使用 `workdir` 参数指定正确目录

2. **异步测试** (pytest-asyncio + SQLAlchemy Async):
   - 每个测试使用独立引擎 (function scope)
   - `pytest.ini` 配置 `asyncio_mode = auto`
   - 测试环境连接池：`pool_size=1, max_overflow=0`

3. **Session 管理**:
   - 使用 `flush()` 代替 `commit()` 保持事务
   - 标准模式：`session.begin() → yield → rollback() → close()`
   - 禁止在 fixture 中手动 commit

4. **测试数据**:
   - 使用 UUID 生成唯一标识符
   - 重复运行时数据必须唯一（用户名、代码等）

5. **后端 API 测试**:
   - Sanic 测试客户端与异步 SQLAlchemy 不兼容
   - 使用异步测试函数并通过 API 创建数据
   - 禁止在测试中使用 `test_session` 创建预置数据
   - 模式：
   ```python
   @pytest.mark.asyncio
   async def test_xxx(app):
       token = create_access_token(TEST_USER_ID, "admin", ["perm"])
       config_response, _ = await app.test_client.post("/api/v1/price-configs", ...)
       request, response = await app.test_client.post("/api/v1/price-bands", ...)
   ```

6. **前端 E2E**:
   - main.ts 必须全局注册 Arco Design 组件
   - 使用 `--headed` 模式调试渲染问题
   - 表单验证使用 `formRef.validate()` 手动触发

7. **路由权限守卫**:
   - 遍历用户权限数组，而非路由 permissions 数组
   - 正确：`permissions.some(perm => to.meta.permissions.includes(perm))`

8. **模型关系**:
   - 双向关联使用 `TYPE_CHECKING` 避免循环导入
   - 明确指定 `foreign_keys` 和 `back_populates`

9. **虚拟环境**:
   - 所有 Python 命令必须在 venv 中执行
   - `source venv/bin/activate && python ...`

10. **路由与菜单同步**:
    - 新增页面时需同时更新 `router/index.ts` 和 `MainLayout.vue`
    - 路由 path 与菜单 key 需保持一致（如 `/transfers/create` 对应 `transfer-create`）
    - 权限配置需检查组件是否存在（如 `Permissions.vue`）
    - 兼容旧路径时使用 redirect 重定向

## Tech Stack

### Frontend
Vue 3 + TypeScript + Arco Design + Pinia + Vue Router + Axios + ECharts + Vite + Playwright

### Backend
Sanic 23.6.0 + SQLAlchemy 2.0 Async + PostgreSQL (asyncpg) + Alembic + Pydantic 2 + JWT + pytest-asyncio

## Arco Design CSS 变量 (前端样式规范)

**颜色**:
- `var(--color-primary)` - 主色 (#165DFF)
- `var(--color-primary-light-1)` - 主色浅色背景
- `var(--color-success)` - 成功色 (#00B42A)
- `var(--color-warning)` - 警告色 (#FF7D00)
- `var(--color-danger)` - 危险色 (#F53F3F)

**背景**:
- `var(--color-bg-1)` - 主背景 (white)
- `var(--color-bg-2)` - 次级背景 (#F7F8FA)
- `var(--color-fill-2)` - 填充背景

**文本**:
- `var(--color-text-1)` - 主文本 (#1D2129)
- `var(--color-text-2)` - 次级文本
- `var(--color-text-3)` - 辅助文本 (#86909C)

**边框/圆角**:
- `var(--color-border)` - 边框色 (#E5E6EB)
- `var(--border-radius-medium)` - 中等圆角 (4px)
- `var(--border-radius-large)` - 大圆角 (8px)

**使用规范**:
- 禁止使用自定义渐变 (`linear-gradient`)
- 使用 `border: 1px solid var(--color-border)` 代替阴影
- `variables.scss` 仅保留颜色变量供 JS 逻辑引用

## Security
- 禁止提交密钥/凭证
- 验证所有用户输入
- 最小权限原则
