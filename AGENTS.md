# AGENTS.md

This file contains guidelines for agentic coding assistants working in this repository.

## 交互要求
- Thinking 思考过程用中文表述.
- Reply 回答也要用中文回复.
- 所有生成的文档都要使用中文，且符合中文的语法规范.
- Use context7 for all code generation and API documentation questions.
- 针对所有错误后修复成功的经验进行总结，把必要的经验写更新至AGENTS.md中，以避免再犯错.

## Project Status

This is a new customer_manager project. The codebase is currently being initialized.

## Build, Lint, and Test Commands

### Build
```bash
# Detect build system and provide appropriate command
# Examples (to be determined based on tech stack):
# npm run build
# python -m build
# cargo build
# make build
```

### Linting
```bash
# Run linter (to be determined based on tech stack):
# npm run lint
# ruff check
# cargo clippy
# make lint
```

### Formatting
```bash
# Format code (to be determined based on tech stack):
# npm run format
# black .
# cargo fmt
# make format
```

### Testing
```bash
# Run all tests (to be determined based on tech stack):
# npm test
# pytest
# cargo test
# make test
```

### Run Single Test
```bash
# Run specific test file (examples based on tech stack):
# npm test -- path/to/test.test.js
# pytest path/to/test.py
# cargo test test_name
```

## Code Style Guidelines

### General Principles
- Write clear, self-documenting code
- Keep functions small and focused on a single responsibility
- Follow existing patterns in the codebase
- Add comments only when necessary to explain complex logic

### Import Ordering
- Group imports: standard library → third-party → local modules
- Sort alphabetically within each group
- Separate groups with blank lines

### Formatting
- Use standard formatting for the chosen language
- Maximum line length: 100 characters (or language standard)
- Use meaningful indentation

### Type System
- Use type hints/annotations for all function parameters and return values
- Avoid `any` types; use specific types or interfaces
- Prefer strict type checking

### Naming Conventions
- **Variables/Functions**: `camelCase` (JavaScript/TypeScript) or `snake_case` (Python/Rust)
- **Classes/Types**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **File names**: `kebab-case` or `snake_case` depending on language conventions
- Use descriptive, meaningful names that explain purpose

### Error Handling
- Never silently swallow errors
- Use appropriate error types for the language
- Provide context in error messages (what happened and why)
- Handle errors at appropriate abstraction levels
- Log errors with sufficient context for debugging

### Function Design
- Default to pure functions when possible
- Limit function parameters to 3-5 (use objects for many parameters)
- Return early for guard clauses
- Use explicit returns rather than implicit ones

### Comments
- Write code that is self-explanatory
- Only comment "why", not "what"
- Keep comments up-to-date with code changes
- Use TODO/FIXME comments sparingly with context

### Testing Guidelines
- Write tests for all public APIs
- Aim for high test coverage on critical paths
- Use descriptive test names that explain what is being tested
- Arrange tests in Given-When-Then structure when appropriate
- Mock external dependencies
- Test edge cases and error conditions

### Testing Development Rules (测试开发规则)
**重要**：以下规则基于实际开发中的问题总结，必须严格遵守以避免重复错误。

1. **Git Worktree规则**
   - 使用git worktree时，所有文件操作（读取、写入、编辑）必须使用workdir参数指定正确的工作树目录
   - 否则文件会被创建在错误的目录（主目录而非工作树目录）

2. **异步测试规则** (pytest-asyncio + SQLAlchemy Async)
   - 每个测试使用独立引擎（function scope）避免连接池冲突
   - 使用async_sessionmaker创建会话工厂
   - 必须在pytest.ini中配置asyncio_mode=auto
   - conftest.py中正确使用@pytest_asyncio.fixture装饰器
   - 连接池配置：pool_size=1, max_overflow=0 (测试环境)

3. **Session管理规则**
   - 测试中使用flush()代替commit()保持数据在事务中
   - 使用嵌套事务（async with session.begin()）自动回滚
   - 标准模式：session.begin() -> yield -> rollback() -> close()
   - 不要在测试fixture中手动commit，会导致状态问题

4. **测试数据规则**
   - 使用UUID生成唯一标识符避免唯一性约束冲突
   - 重复运行测试时数据必须唯一（用户名、客户代码、权限代码等）

5. **模块导入规则**
   - pytest.ini 仅配置（asyncio_mode），不导入模块
   - 所有模块导入在 conftest.py 中完成
   - 避免重复导入导致冲突

 6. **前端 E2E 测试规则** (Playwright + Arco Design)
    - 确保 main.ts 中全局注册所有使用的 UI 组件库（如 Arco Design）
    - 组件未注册会导致渲染失败，所有 E2E 测试失败
    - 使用浏览器调试模式（headed）观察实际渲染问题
    - 验证错误样式类需根据 UI 库实际输出调整（如 `.arco-form-item-error`）
    - 表单验证需使用 formRef.validate() 手动触发

 7. **路由权限守卫规则** (Vue Router)
    - 权限检查必须遍历用户权限数组，而非路由 meta.permissions 数组
    - 错误示例：`to.meta.permissions.some(perm => permissions.includes(perm))`
    - 正确示例：`permissions.some(perm => to.meta.permissions.includes(perm))`
    - 通配符'*'权限检查需在用户权限循环中判断，而非在路由权限循环中

 8. **后端 API 测试规则** (Sanic + SQLAlchemy Async + pytest-asyncio)
     - **架构限制**: Sanic 测试客户端使用同步模式，与异步 SQLAlchemy 不兼容
     - **已知问题**:
       - `RuntimeError: Event loop is closed` - 异步 SQLAlchemy 在 flush() 时事件循环已关闭
       - `test_session.flush()` 不会被 await，数据不会提交到数据库
       - 测试使用的事务隔离与 Sanic 蓝图的生产数据库连接不一致
       - `AttributeError: attached to a different loop` - 事件循环冲突
     - **根本原因**: Sanic 测试客户端创建自己的事件循环，与 SQLAlchemy 异步引擎的事件循环冲突
     - **解决方案**:
       - 使用异步测试函数 (`async def`) 并通过 API 创建测试数据
       - 避免在测试中使用 `test_session` 创建预置数据
       - 每个测试通过 API 独立创建所需数据（先创建 PriceConfig，再创建 PriceBand）
       - 使用 UUID 生成唯一代码避免唯一约束冲突
       - 使用 `create_access_token()` 生成测试 token
     - **测试模式**:
       ```python
       @pytest.mark.asyncio
       async def test_xxx(app):
           token = create_access_token(TEST_USER_ID, "admin", ["permission"])
           # 通过 API 创建依赖数据
           config_response, _ = await app.test_client.post("/api/v1/price-configs", ...)
           # 执行测试操作
           request, response = await app.test_client.post("/api/v1/price-bands", ...)
       ```
     - **替代方案**:
       - 使用集成测试直接测试 Service 层（不通过 HTTP）
       - 使用纯异步测试框架（如 aiohttp）替代 Sanic 测试客户端

 9. **数据库配置规则** (Phase 1.5 经验总结)
     - 测试数据库类型应与生产数据库一致（避免 SQLite 测试 PostgreSQL/MySQL 特性）
     - 连接池配置需要根据数据库类型判断是否应用
       ```python
       if settings.asyncpg_url.startswith("sqlite"):
           engine = create_async_engine(settings.asyncpg_url, echo=False)
       else:
           engine = create_async_engine(
               settings.asyncpg_url,
               echo=False,
               pool_pre_ping=True,
               pool_size=1,
               max_overflow=0,
           )
       ```
     - 使用 Python 虚拟环境：`source venv/bin/activate && python ...`
     - 不要在 macOS 系统 Python 2.7 上运行 Python 3 代码

 10. **模型关系规则** (Phase 1.5 经验总结)
      - 双向关联使用 `TYPE_CHECKING` 避免循环导入
        ```python
        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from .customer import Customer
        ```
      - 明确指定 `foreign_keys` 参数避免歧义
      - 使用 `back_populates` 保持双向同步

 11. **服务层规则** (Phase 1.5 经验总结)
      - 业务逻辑封装在服务类中（如 `HealthService`, `BillingService`）
      - 服务方法接受 `AsyncSession` 作为参数
      - 使用静态方法或依赖注入
      - 蓝图只负责 HTTP 处理，调用服务层执行业务逻辑

 12. **配置文件规则** (Phase 1.5 经验总结)
      - 使用 `pydantic-settings` 管理配置
      - 支持通过环境变量覆盖配置
      - 数据库 URL 使用属性方法动态生成
      - 支持多数据库类型切换（`db_type` 配置）
      ```python
      @property
      def database_url(self) -> str:
          if self.db_type == "mysql":
              return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
          else:
              return f"postgresql+asyncpg://{...}"
      ```

 13. **Python 虚拟环境规则** (Phase 1.5 经验总结)
      - 所有 Python 命令必须在虚拟环境中执行
      - 检查命令：`which python` 应指向 venv 目录
      - 激活虚拟环境：`source venv/bin/activate`
      - 避免使用系统 Python（Python 2.7）

### Security
- Never commit secrets, API keys, or credentials
- Validate and sanitize all user inputs
- Follow principle of least privilege
- Keep dependencies updated

## Additional Notes

- This file should be updated as the project grows
- Check for technology-specific configuration files for additional conventions
- When adding new features, maintain consistency with existing code style
