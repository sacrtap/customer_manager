# Phase 1.5 后端 API 开发错误处理与经验总结

## 遇到的问题及解决方案

### 1. Python 版本问题

**问题**: 使用 `python` 命令时默认使用 Python 2.7，导致语法错误。
```
SyntaxError: invalid syntax
  File "app/__init__.py", line 22
    async def init_db():
```

**原因**: macOS 系统默认 python 指向 Python 2.7。

**解决方案**: 
- 始终使用 `python3` 或虚拟环境中的 `python`
- 在虚拟环境中：`source venv/bin/activate && python ...`

**经验**: 
- 在 backend 目录执行 Python 命令前，必须先激活虚拟环境
- 所有命令应使用：`source venv/bin/activate && python <command>`

### 2. 数据库驱动兼容性问题

**问题**: 测试使用 SQLite，但现有模型使用 PostgreSQL 特定的 JSONB 类型。
```
sqlalchemy.exc.CompileError: Compiler <SQLiteTypeCompiler> can't render element of type JSONB
```

**原因**: 
- SQLite 不支持 JSONB 类型
- 项目中的 price_bands 等表使用了 JSONB

**解决方案**:
1. 测试配置使用与生产相同的数据库类型（MySQL 或 PostgreSQL）
2. 更新 config.py 添加测试数据库配置：
```python
@property
def asyncpg_url(self) -> str:
    if self.test_db_type == "mysql":
        return f"mysql+aiomysql://{self.test_db_user}:{self.test_db_password}@{self.test_db_host}:{self.test_db_port}/{self.test_db_name}"
    else:
        return f"postgresql+asyncpg://{self.test_db_user}:{self.test_db_password}@{self.test_db_host}:{self.test_db_port}/{self.test_db_name}"
```

**经验**:
- 测试数据库应该与生产数据库使用相同的类型
- 避免在测试中使用 SQLite，除非所有模型都兼容 SQLite

### 3. SQLAlchemy 连接池配置问题

**问题**: SQLite 不支持连接池配置。
```
TypeError: Invalid argument(s) 'pool_size','max_overflow' sent to create_engine()
```

**原因**: 
- create_async_engine 时传入了 pool_size 和 max_overflow 参数
- SQLite 的 StaticPool 不支持这些参数

**解决方案**:
在 conftest.py 中根据数据库类型判断是否使用池配置：
```python
@pytest_asyncio.fixture(scope="function")
async def test_engine():
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
    # ...
```

**经验**:
- 连接池配置需要根据数据库类型区分
- MySQL/PostgreSQL 需要池配置，SQLite 不需要

### 4. 模型循环导入问题

**问题**: Customer 和 Billing 模型互相引用导致循环导入。

**原因**: 
- Customer 模型需要引用 Billing
- Billing 模型需要引用 Customer

**解决方案**:
使用 TYPE_CHECKING 进行前向引用：
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .customer import Customer

class Billing(Base):
    customer: Mapped["Customer"] = relationship(
        back_populates="billings", 
        foreign_keys=[customer_id]
    )
```

**经验**:
- 使用 TYPE_CHECKING 避免运行时循环导入
- 使用字符串类型注解进行前向引用
- 明确指定 foreign_keys 避免歧义

### 5. Sanic 应用重复注册问题

**问题**: 多次创建 app 时出现 SanicException。
```
sanic.exceptions.SanicException: Sanic app name "customer_manager" already in use.
```

**原因**: Sanic 默认会注册应用名称，不允许重复。

**解决方案**:
- 在测试代码中使用唯一的应用名称
- 或者清除注册表：`Sanic._app_registry = {}`

**经验**:
- 在测试中创建多个 Sanic 应用实例时，需要使用不同的名称
- 最好避免多次创建应用实例

### 6. 测试 fixture 中的会话管理

**问题**: 测试fixture中的数据库会话管理不当导致数据不持久化。

**原因**: 
- 根据 AGENTS.md，Sanic 测试客户端与异步 SQLAlchemy 不兼容
- test_session.flush() 不会被 await，数据不会提交

**解决方案**:
- 通过 API 创建测试数据，而不是直接使用 session
- 每个测试使用独立的 API 调用来创建和验证数据
- 使用 UUID 生成唯一值避免约束冲突

**经验** (来自 AGENTS.md):
```python
@pytest.mark.asyncio
async def test_xxx(app):
    token = create_access_token(TEST_USER_ID, "admin", ["permission"])
    # 通过 API 创建依赖数据
    config_response, _ = await app.test_client.post("/api/v1/price-configs", ...)
    # 执行测试操作
    request, response = await app.test_client.post("/api/v1/price-bands", ...)
```

## 新增的最佳实践

### 1. 配置文件结构

支持多数据库类型的配置：
```python
class Settings(BaseSettings):
    db_type: str = "mysql"  # 支持切换
    test_db_type: str = "mysql"  # 测试数据库类型
    
    @property
    def database_url(self) -> str:
        if self.db_type == "mysql":
            return f"mysql+aiomysql://{...}"
        else:
            return f"postgresql+asyncpg://{...}"
```

### 2. 服务层模式

使用服务层封装业务逻辑：
```python
class HealthService:
    @staticmethod
    async def get_dashboard_stats(session: AsyncSession) -> Dict[str, Any]:
        # 业务逻辑
        pass
```

优点：
- 蓝图只负责 HTTP 处理
- 业务逻辑可测试
- 易于复用

### 3. 统一的响应格式

所有 API 使用统一的响应格式：
```json
{
  "data": { ... },
  "timestamp": "2026-03-05T10:30:00Z"
}
```

实现：
```python
return json({
    "data": result,
    "timestamp": datetime.utcnow().isoformat(),
})
```

### 4. 权限装饰器

使用装饰器保护端点：
```python
@health_bp.get("/dashboard")
@require_permissions("dashboard.view")
async def get_health_dashboard(request: Request):
    pass
```

### 5. 数据库迁移命名规范

迁移文件命名格式：
```
{revision_id}_{description}.py
例如：b2c3d4e5f6g7_add_customer_health_fields_and_billing_table.py
```

迁移文件内容：
- 包含 upgrade() 和 downgrade() 函数
- 明确指定所有索引和外键
- 包含详细的注释

## 测试开发规则更新

基于本次开发经验，在 AGENTS.md 测试开发规则基础上补充：

### 9. **数据库配置规则**
- 测试数据库类型应与生产数据库一致
- 不要在测试中使用 SQLite 测试 PostgreSQL/MySQL 特定的功能
- 连接池配置需要根据数据库类型判断是否应用

### 10. **模型关系规则**
- 双向关联使用 TYPE_CHECKING 避免循环导入
- 明确指定 foreign_keys 参数
- 使用 back_populates 保持双向同步

### 11. **服务层规则**
- 业务逻辑封装在服务类中
- 服务方法接受 AsyncSession 作为参数
- 服务类使用静态方法或依赖注入

### 12. **配置文件规则**
- 使用 pydantic-settings 管理配置
- 支持通过环境变量覆盖配置
- 数据库 URL 使用属性方法动态生成

## 提交规范

提交消息格式：
```
type(scope): subject

body (optional)

Technical stack:
- technologies used
```

示例：
```
feat(backend): Phase 1.5 Health + Billing API 开发

- 新增 Customer 健康度字段 (last_active_at, health_score)
- 创建 Billing 模型和结算记录功能
- 实现 GET /api/v1/health/dashboard 端点

技术栈:
- Sanic + SQLAlchemy Async + aiomysql
- pytest-asyncio 异步测试
- Alembic 数据库迁移
```

## 检查清单

开发新 API 时的检查清单：

- [ ] 创建/更新模型
- [ ] 创建服务层（如需要）
- [ ] 创建蓝图
- [ ] 在 `__init__.py` 中注册蓝图
- [ ] 添加权限装饰器
- [ ] 创建数据库迁移
- [ ] 编写单元测试
- [ ] 更新 conftest.py（如需要）
- [ ] 验证导入无错误
- [ ] 运行测试
- [ ] 提交代码

## 参考资料

- [Sanic 文档](https://sanic.dev/)
- [SQLAlchemy Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [Alembic 文档](https://alembic.sqlalchemy.org/)
