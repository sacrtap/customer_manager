# 阶段 2: 数据库设计与迁移

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 配置 SQLAlchemy 数据库连接,创建所有数据模型(用户、角色、权限、客户、操作日志),配置 Alembic 数据库迁移

**预计时间:** 2-3 天

**前置依赖:** 阶段 1: 项目基础架构搭建

**Architecture:** 
- 使用 SQLAlchemy 2.0 异步 ORM
- 配置数据库连接和会话工厂
- 创建所有核心数据模型
- 配置 Alembic 迁移工具

**Tech Stack:**
- ORM: SQLAlchemy 2.0 (async)
- 驱动: asyncpg
- 迁移工具: Alembic 1.12.1

---

## Task 4: 配置 SQLAlchemy 数据库连接

**Files:**
- Create: `backend/app/database.py`
- Modify: `backend/app/__init__.py`

**Step 1: 创建数据库连接模块**

```python
# backend/app/database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings


class Base(DeclarativeBase):
    """ORM 基类"""
    pass


# 创建异步引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",
    future=True
)

# 创建异步会话工厂
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_db_session() -> AsyncSession:
    """获取数据库会话"""
    async with async_session_maker() as session:
        yield session
```

**Step 2: 更新应用初始化**

```python
# 在 backend/app/__init__.py 中添加
from .database import engine

async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 导入所有模型以确保它们被注册
        from .models import customer, user, role, permission, operation_log
        await conn.run_sync(Base.metadata.create_all)

def create_app():
    """应用工厂函数"""
    # ... 现有代码 ...
    
    # 初始化数据库
    @app.listener("before_server_start")
    async def setup_database(app):
        await init_db()
    
    return app
```

**Step 3: 创建数据库连接测试**

```python
# backend/app/tests/test_database.py
import pytest
from app.database import engine, async_session_maker, get_db_session


@pytest.mark.asyncio
async def test_database_connection():
    """测试数据库连接"""
    async with engine.connect() as conn:
        result = await conn.execute("SELECT 1")
        assert result.scalar() == 1


@pytest.mark.asyncio
async def test_get_db_session():
    """测试获取数据库会话"""
    async for session in get_db_session():
        assert session is not None
        break  # 只测试第一次迭代
```

**Step 4: 运行测试**

```bash
cd backend
pytest app/tests/test_database.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/database.py backend/app/__init__.py backend/app/tests/test_database.py
git commit -m "feat: configure SQLAlchemy database connection with tests"
```

---

## Task 5: 创建用户模型

**Files:**
- Create: `backend/app/models/__init__.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/tests/test_user_model.py`

**Step 1: 创建 models 初始化文件**

```python
# backend/app/models/__init__.py
# 导入所有模型以确保它们被 SQLAlchemy 注册
from .user import User
from .role import Role, UserRole
from .permission import Permission
from .customer import Customer
from .operation_log import OperationLog
```

**Step 2: 创建用户模型**

```python
# backend/app/models/user.py
from sqlalchemy import BigInteger, String, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from ..[database import Base
from datetime import datetime


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    real_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "username": self.username,
            "real_name": self.real_name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
```

**Step 3: 创建用户模型测试**

```python
# backend/app/tests/test_user_model.py
import pytest
from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User


@pytest.mark.asyncio
async def test_create_user():
    """测试创建用户"""
    async with async_session_maker() as session:
        user = User(
            username="testuser",
            password_hash="hashed_password",
            real_name="测试用户"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        assert user.id is not None
        assert user.username == "testuser"
        assert user.real_name == "测试用户"


@pytest.mark.asyncio
async def test_user_to_dict():
    """测试用户转换为字典"""
    async with async_session_maker() as session:
        user = User(
            username="testuser2",
            password_hash="hashed_password",
            real_name="测试用户2"
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        user_dict = user.to_dict()
        
        assert user_dict["id"] == user.id
        assert user_dict["username"] == "testuser2"
        assert "password_hash" not in user_dict
```

**Step 4: 运行测试**

```bash
cd backend
pytest app/tests/test_user_model.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/__init__.py backend/app/models/user.py backend/app/tests/test_user_model.py
git commit -m "feat: create user model with tests"
```

---

## Task 6: 创建角色和权限模型

**Files:**
- Create: `backend/app/models/permission.py`
- Create: `backend/app/models/role.py`
- Create: `backend/app/tests/test_rbac_models.py`

**Step 1: 创建权限模型**

```python
# backend/app/models/permission.py
from sqlalchemy import BigInteger, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base
from datetime import datetime


class Permission(Base):
    """权限模型"""
    __tablename__ = "permissions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    module: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    parent_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("permissions.id"), nullable=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "module": self.module,
            "description": self.description,
            "is_active": self.is_active
        }
```

**Step 2: 创建角色模型**

```python
# backend/app/models/role.py
from sqlalchemy import BigInteger, String, Boolean, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base
from datetime import datetime
import json


class Role(Base):
    """角色模型"""
    __tablename__ = "roles"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    permissions: Mapped[dict] = mapped_column(JSON, default=lambda: [], nullable=False)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "permissions": self.permissions,
            "is_system": self.is_system
        }


class UserRole(Base):
    """用户角色关联表"""
    __tablename__ = "user_roles"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    role_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("roles.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
```

**Step 3: 创建 RBAC 模型测试**

```python
# backend/app/tests/test_rbac_models.py
import pytest
from datetime import datetime
from app.database import async_session_maker
from app.models.permission import Permission
from app.models.role import Role, UserRole


@pytest.mark.asyncio
async def test_create_permission():
    """测试创建权限"""
    async with async_session_maker() as session:
        permission = Permission(
            name="查看客户",
            code="customer.view",
            module="customer",
            description="查看客户列表和详情"
        )
        session.add(permission)
        await session.commit()
        await session.refresh(permission)
        
        assert permission.id is not None
        assert permission.code == "customer.view"


@pytest.mark.asyncio
async def test_create_role():
    """测试创建角色"""
    async with async_session_maker() as session:
        role = Role(
            name="运营专员",
            code="specialist",
            description="运营团队专员",
            permissions=["customer.view", "customer.create"]
        )
        session.add(role)
        await session.commit()
        await session.refresh(role)
        
        assert role.id is not None
        assert role.permissions == ["customer.view", "customer.create"]


@pytest.mark.asyncio
async def test_user_role_association():
    """测试用户角色关联"""
    async with async_session_maker() as session:
        # 创建用户
        from app.models.user import User
        user = User(
            username="testuser",
            password_hash="hashed",
            real_name="测试用户"
        )
        session.add(user)
        await session.commit()
        
        # 创建角色
        role = Role(
            name="测试角色",
            code="test_role",
            permissions=["*"]
        )
        session.add(role)
        await session.commit()
        
        # 创建关联
        user_role = UserRole(user_id=user.id, role_id=role.id)
        session.add(user_role)
        await session.commit()
        
        assert user_role.user_id == user.id
        assert user_role.role_id == role.id
```

**Step 4: 运行测试**

```bash
cd backend
pytest app/tests/test_rbac_models.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/models/permission.py backend/app/models/role.py backend/app/tests/test_rbac_models.py
git commit -m "feat: create RBAC models with tests"
```

---

## Task 7: 创建客户模型

**Files:**
- Create: `backend/app/models/customer.py`
- Create: `backend/app/tests/test_customer_model.py`

**Step 1: 创建客户模型**

```python
# backend/app/models/customer.py
from sqlalchemy import BigInteger, String, Numeric, DateTime, func, Text, Index
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base
from datetime import datetime


class Customer(Base):
    """客户模型"""
    __tablename__ = "customers"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=True, index=True)
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    sales_rep_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    tier_level: Mapped[str] = mapped_column(
        String(1), 
        default="D",
        nullable=False,
        index=True
    )
    annual_consumption: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    remark: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # 索引
    __table_args__ = (
        Index("idx_sales_tier", "sales_rep_id", "tier_level"),
    )
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "industry": self.industry,
            "sales_rep_id": self.sales_rep_id,
            "tier_level": self.tier_level,
            "annual_consumption": float(self.annual_consumption) if self.annual_consumption else 0,
            "status": self.status,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "address": self.address,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
```

**Step 2: 创建客户模型测试**

```python
# backend/app/tests/test_customer_model.py
import pytest
from datetime import datetime
from sqlalchemy import select
from app.database import async_session_maker
from app.models.customer import Customer


@pytest.mark.asyncio
async def test_create_customer():
    """测试创建客户"""
    async with async_session_maker() as session:
        customer = Customer(
            name="测试客户",
            code="CUST001",
            industry="科技",
            sales_rep_id=1,
            tier_level="A",
            annual_consumption=500000.00,
            status="active",
            contact_person="张三",
            contact_phone="13800138000",
            contact_email="zhangsan@example.com"
        )
        session.add(customer)
        await session.commit()
        await await session.refresh(customer)
        
        assert customer.id is not None
        assert customer.name == "测试客户"
        assert customer.code == "CUST001"
        assert customer.tier_level == "A"
        assert float(customer.annual_consumption) == 500000.00


@pytest.mark.asyncio
async def test_customer_to_dict():
    """测试客户转换为字典"""
    async with async_session_maker() as session:
        customer = Customer(
            name="测试客户2",
            code="CUST002",
            sales_rep_id=1
        )
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        
        customer_dict = customer.to_dict()
        
        assert customer_dict["id"] == customer.id
        assert customer_dict["name"] == "测试客户2"
        assert "sales_rep_id" in customer_dict
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_customer_model.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/models/customer.py backend/app/tests/test_customer_model.py
git commit -m "feat: create customer model with tests"
```

---

## Task 8: 创建操作日志模型

**Files:**
- Create: `backend/app/models/operation_log.py`
- Create: `backend/app/tests/test_operation_log_model.py`

**Step 1: 创建操作日志模型**

```python
# backend/app/models/operation_log.py
from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base
from datetime import datetime
import json


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=True)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    old_value: Mapped[dict] = mapped_columnar(JSON, nullable=True)
    new_value: Mapped[dict] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operation_type": self.operation_type,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
```

**Step 2: 创建操作日志测试**

```python
# backend/app/tests/test_operation_log_model.py
import pytest
from datetime import datetime
from app.database import async_session_maker
from app.models.operation_log import OperationLog


@pytest.mark.asyncio
async def test_create_operation_log():
    """测试创建操作日志"""
    async with async_session_maker() as session:
        log = OperationLog(
            user_id=1,
            operation_type="customer.create",
            target_type="customer",
            target_id=100,
            new_value={"name": "测试客户"},
            ip_address="192.168.1.1"
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)
        
        assert log.id is not None
        assert log.operation_type == "customer.create"
        assert log.target_id == 100
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_operation_log_model.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/models/operation_log.py backend/app/tests/test_operation_log_model.py
git commit -m "feat: create operation log model with tests"
```

---

## Task 9: 配置 Alembic 数据库迁移

**Files:**
- Create: `backend/alembic.ini`
- Create: `backend/migrations/env.py`
- Create: `backend/migrations/script.py.mako`

**Step 1: 创建 alembic.ini**

```ini
# backend/alembic.ini
[alembic]
script_location = migrations
prepend_sys_path = .
version_path_separator = os
sqlalchemy.url = postgresql+asyncpg://customer_manager:changeme@localhost:5432/customer_manager

[post_write_hooks]

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

**Step 2: 创建迁移环境配置**

```python
# backend/migrations/env.py
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.database import Base
from app.config import settings

# 导入所有模型
from app.models import customer, user, role, permission, operation_log

config = context.config

fileConfig(config.config_file_name)

target_metadata = Base.metadata


def需要的函数在下一步...]
```

**Step 3: 生成初始迁移**

```bash
cd backend
alembic revision --autogenerate -m "initial schema"
```

**Step 4: Commit**

```bash
git add backend/alembic.ini backend/migrations/
git commit -m "feat: configure Alembic database migrations"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 2 即可视为完成:

- [ ] 数据库连接模块已创建并测试
- [ ] 用户模型已创建并测试
- [ ] 角色模型已创建并测试
- [ ] 权限模型已创建并测试
- [ ] 客户模型已创建并测试
- [ ] 操作日志模型已创建并测试
- [ ] Alembic 迁移已配置
- [ ] 初始迁移已生成
- [ ] 所有测试通过

---

## 下一步

完成阶段 2 后,请继续执行 **阶段 3: 认证与 RBAC 权限系统**

文档: `docs/plans/2026-03-03-customer-manager-phase3-auth-rbac.md`
