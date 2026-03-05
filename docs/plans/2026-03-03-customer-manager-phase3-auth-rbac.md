# 阶段 3: 认证与 RBAC 权限系统

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 实现用户认证系统、JWT Token 管理、RBAC 权限管理、权限检查中间件

**预计时间:** 5-7 天

**前置依赖:** 阶段 2: 数据库设计与迁移

**Architecture:** 
- 实现密码哈希工具(bcrypt)
- 实现 JWT Token 生成和验证
- 实现认证中间件(提取用户信息)
- 实现 RBAC 中间件(权限检查)
- 实现登录/登出/刷新 Token API

**Tech Stack:**
- 密码加密: bcrypt 4.1.1
- Token 管理: PyJWT 2.8.0
- 验证框架: Pydantic 2.5.0

---

## Task 10: 实现密码哈希工具

**Files:**
- Create: `backend/app/utils/password.py`
- Create: `backend/app/tests/test_password_utils.py`

**Step 1: 创建密码工具模块**

```python
# backend/app/utils/password.py
import bcrypt


def hash_password(password: str) -> str:
    """哈希密码"""
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False
```

**Step 2: 创建密码工具测试**

```python
# backend/app/tests/test_password_utils.py
import pytest
from app.utils.password import hash_password, verify_password


def test_hash_password():
    """测试密码哈希"""
    password = "test123"
    hashed = hash_password(password)
    
    assert hashed != password
    assert len(hashed) > 50
    assert hashed.startswith('$2b$')


def test_verify_password_correct():
    """测试验证正确密码"""
    password = "test123"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """测试验证错误密码"""
    password = "test123"
    hashed = hash_password(password)
    wrong_password = "wrong123"
    
    assert verify_password(wrong_password, hashed) is False
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_password_utils.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/utils/password.py backend/app/tests/test_password_utils.py
git commit -m "feat: implement password hash utility with tests"
```

---

## Task 11: 实现 JWT 工具

**Files:**
- Create: `backend/app/utils/jwt.py`
- Create: `backend/app/tests/test_jwt_utils.py`

**Step 1: 创建 JWT 工具模块**

```python
# backend/app/utils/jwt.py
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from app.config import settings


def create_access_token(user_id: int, role: str, permissions: list) -> str:
    """创建访问 Token"""
    now = datetime.utcnow()
    expire = now + timedelta(hours=settings.jwt_expire_hours)
    
    payload = {
        "user_id": user_id,
        "role": role,
        "permissions": permissions,
        "iat": now.timestamp(),
        "exp": expire.timestamp()
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return token


def decode_token(token: str) -> Optional[Dict]:
    """解码 Token"""
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
    except Exception:
        return None
```

**Step 2: 创建 JWT 工具测试**

```python
# backend/app/tests/test_jwt_utils.py
import pytest
from app.utils.jwt import create_access_token, decode_token


def test_create_and_decode_token():
    """测试创建和解码 Token"""
    user_id = 123
    role = "admin"
    permissions = ["*"]
    
    token = create_access_token(user_id, role, permissions)
    assert isinstance(token, str)
    assert len(token) > 0
    
    payload = decode_token(token)
    assert payload is not None
    assert payload["user_id"] == user_id
    assert payload["role"] == role
    assert payload["permissions"] == permissions


def test_decode_invalid_token():
    """测试解码无效 Token"""
    invalid_token = "invalid.token.string"
    payload = decode_token(invalid_token)
    assert payload is None
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_jwt_utils.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/utils/jwt.py backend/app/tests/test_jwt_utils.py
git commit -m "feat: implement JWT JWT utility with tests"
```

---

## Task 12: 实现认证中间件

**Files:**
- Create: `backend/app/middlewares/auth.py`
- Create: `backend/app/tests/test_auth_middleware.py`

**Step 1: 创建认证中间件**

```python
# backend/app/middlewares/auth.py
from sanic import Request, Sanic
from sanic.response import JSONResponse
from app.utils.jwt import decode_token


def attach_auth_middleware(app: Sanic):
    """附加认证中间件"""
    
    @app.middleware("request")
    async def extract_user(request: Request):
        """从请求中提取用户信息"""
        authorization = request.headers.get("Authorization", "")
        
        if not authorization.startswith("Bearer "):
            request.ctx.user = None
            return
        
        token = authorization.replace("Bearer ", "")
        payload = decode_token(token)
        
        if payload:
            request.ctx.user = {
                "user_id": payload["user_id"],
                "role": payload["role"],
                "permissions": payload.get("permissions", [])
            }
        else:
            request.ctx.user = None


def require_auth_middleware(app: Sanic):
    """要求认证中间件"""
    public_paths = ["/api/v1/auth/login", "/health"]
    
    
    @app.middleware("response")
    async def check_auth(request, response):
        """检查认证"""
        if request.path in public_paths:
            return response
        
        if hasattr(request.ctx, "user") and request.ctx.user is None:
            return JSONResponse(
                {
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "未授权访问"
                    }
                },
                status=401
            )
        
        return response
```

**Step 2: 创建认证中间件测试**

```python
# backend/app/tests/test_auth_middleware.py
import pytest
from sanic import Sanic, Request
from sanic.response import json
from app.middlewares.auth import attach_auth_middleware, require_auth_middleware
from app.utils.jwt import create_access_token


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    require_auth_middleware(app)
    
    @app.get("/protected")
    async def protected(request):
        return json({"user": request.ctx.user})
    
    @app.get("/public")
    async def public(request):
        return json({"message": "public"})
    
    return app


def test_public_endpoint_without_token(app):
    """测试公开端点不需要 Token"""
    request, response = app.test_client.get("/public")
    assert response.status == 200
    assert response.json["message"] == "public"


def test_protected_endpoint_without_token(app):
    """测试受保护端点需要 Token"""
    request, response = app.test_client.get("/protected")
    assert response.status == 401


def test_protected_endpoint_with_valid_token(app):
    """测试受保护端点有效 Token"""
    token = create_access_token(123, "admin", ["*"])
    
    request, response = app.test_client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status == 200
    assert response.json["user"]["user_id"] == 123
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_auth_middleware.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/middlewares/auth.py backend/app/tests/test_auth_middleware.py
git commit -m "feat: implement authentication middleware with tests"
```

---

## Task 13: 实现 RBAC 权限检查工具

**Files:**
- Create: `backend/app/utils/rbac.py`
- Create: `backend/app/tests/test_rbac_utils.py`

**Step 1: 创建 RBAC 工具模块**

```python
# backend/app/utils/rbac.py


def has_permission(user_permissions: list, required_permission: str) -> bool:
    """检查用户是否拥有所需权限"""
    # 超级管理员拥有所有权限
    if "*" in user_permissions:
        return True
    
    # 精确匹配
    if required_permission in user_permissions:
        return True
    
    # 通配符匹配 (例如: customer.* 匹配 customer.view)
    if "*" in required_permission:
        parts = required_permission.split(".*")
        if len(parts) == 2:
            prefix = parts[0]
            for perm in user_permissions:
                if perm.startswith(prefix):
                    return True
    
    return False


def check_rbac(user_role: str, user_permissions: list, required_permissions: list) -> bool:
    """检查 RBAC 权限"""
    # 超级管理员
    if user_role == "admin":
        return True
    
    # 检查所有必需权限
    for required in required_permissions:
        if not has_permission(user_permissions, required):
            return False
    
    return True
```

**Step 2: 创建 RBAC 工具测试**

```python
# backend/app/tests/test_rbac_utils.py
import pytest
from app.utils.rbac import has_permission, check_rbac


def test_has_permission_exact_match():
    """测试精确权限匹配"""
    user_permissions = ["customer.view", "customer.create"]
    assert has_permission(user_permissions, "customer.view") is True


def test_has_permission_wildcard_match():
    """测试通配符权限匹配"""
    user_permissions = ["customer.*", "user.view"]
    assert has_permission(user_permissions, "customer.create") is True


def test_has_permission_all_wildcard():
    """测试所有权限通配符"""
    user_permissions = ["*"]
    assert has_permission(user_permissions, "any.permission") is True


def test_check_rbac_admin():
    """测试管理员总是通过"""
    assert check_rbac("admin", [], ["any.permission"]) is True


def test_check_rbac_normal_user():
    """测试普通用户权限检查"""
    user_permissions = ["customer.view", "customer.create"]
    required_permissions = ["customer.view"]
    
    assert check_rbac("user", user_permissions, required_permissions) is True


def test_check_rbac_insufficient_permissions():
    """测试权限不足"""
    user_permissions = ["customer.view"]
    required_permissions = ["customer.delete"]
    
    assert check_rbac("user", user_permissions, required_permissions) is False
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_rbac_utils.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/utils/rbac.py backend/app/tests/test_rbac_utils.py
git commit -m "feat: implement RBAC utility functions with tests"
```

---

## Task 14: 实现 RBAC 装饰器

**Files:**
- Create: `backend/app/decorators/rbac.py`
- Create: `backend/app/tests/test_rbac_decorators.py`

**Step 1: 创建 RBAC 装饰器**

```python
# backend/app/decorators/rbac.py
from functools import wraps
from sanic import Request
from sanic.response import JSONResponse
from app.utils.rbac import check_rbac


def require_permissions(*permissions):
    """RBAC 权限装饰器"""
    def decorator(f):
        @wraps(f)
        async def wrapper(request: Request, *args, **kwargs):
            # 检查用户是否已认证
            if not hasattr(request.ctx, "user") or request.ctx.user is None:
                return JSONResponse(
                    {"error": {"code": "UNAUTHORIZED", "message": "未授权访问"}},
                    status=401
                )
            
            user = request.ctx.user
            user_role = user.get("role", "")
            user_permissions = user.get("permissions", [])
            
            # 检查权限
            if not check_rbac(user_role, user_permissions, list(permissions)):
                return JSONResponse(
                    {"error": {"code": "FORBIDDEN", "message": "权限不足"}},
                    status=403
                )
            
            # 权限检查通过,执行原函数
            return await f(request, *args, **kwargs)
        
        return wrapper
    return decorator
```

**Step 2: 创建 RBAC 装饰器测试**

```python
# backend/app/tests/test_rbac_decorators.py
import pytest
from sanic import Sanic
from sanic.response import json
from app.decorators.rbac import require_permissions


def test_require_permissions_with_valid_permission():
    """测试有效权限"""
    app = Sanic("test_app")
    
    @app.get("/customer/list")
    @require_permissions("customer.view")
    async def list_customers(request):
        return json({"data": []})
    
    # 模拟已认证用户
    @app.middleware("request")
    async def mock_auth(request):
        request.ctx.user = {
            "user_id": 1,
            "role": "user",
            "permissions": ["customer.view"]
        }
    
    request, response = app.test_client.get("/customer/list")
    assert response.status == 200


def test_require_permissions_without_permission():
    """测试无权限"""
    app = Sanic("test_app")
    
    @app.get("/customer/list")
    @require_permissions("customer.view")
    async def list_customers(request):
        return json({"data": []})
    
    # 模拟已认证用户(无权限)
    @app.middleware("request")
    async def mock_auth(request):
        request.ctx.user = {
            "user_id": 1,
            "role": "user",
            "permissions": []
        }
    
    request, response = app.test_client.get("/customer/list")
    assert response.status == 403
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_rbac_decorators.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/decorators/rbac.py backend/app/tests/test_rbac_decorators.py
git commit -m "feat: implement RBAC permission decorators with tests"
```

---

## Task 15: 实现 Pydantic 验证 Schema

**Files:**
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/schemas/user.py`
- Create: `backend/app/schemas/common.py`
- Create: `backend/app/tests/test_schemas.py`

**Step 1: 创建认证 Schema**

```python
# backend/app/schemas/auth.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class LoginRequest(BaseModel):
    """登录请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class LoginResponse(BaseModel):
    """登录响应"""
    token: str
    user: dict
    permissions: list


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""
    refresh_token: str
```

**Step 2: 创建用户 Schema**

```python
# backend/app/schemas/user.py
from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class UserCreateRequest(BaseModel):
    """创建用户请求"""
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: str = Field("active", regex="^(active|inactive)$")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""
    real_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, regex="^(active|inactive)$")


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    real_name: str
    email: Optional[str]
    phone: Optional[str]
    status: str
    created_at: str
    updated_at: str
```

**Step 3: 创建通用 Schema**

```python
# backend/app/schemas/common.py
from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    """错误响应"""
    code: str
    message: str
    details: Optional[list] = None
    timestamp: str
    path: str


class SuccessResponse(BaseModel):
    """成功响应"""
    data: dict
    timestamp: str
```

**Step 4: 创建 Schema 测试**

```python
# backend/app/tests/test_schemas.py
import pytest
from pydantic import ValidationError
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreateRequest


def test_login_request_valid():
    """测试有效的登录请求"""
    data = {
        "username": "testuser",
        "password": "test123"
    }
    request = LoginRequest(**data)
    assert request.username == "testuser"


def test_login_request_invalid_password():
    """测试无效密码"""
    data = {
        "username": "testuser",
        "password": "123"  # 太短
    }
    with pytest.raises(ValidationError):
        LoginRequest(**data)


def test_user_create_request_valid():
    """测试有效的创建用户请求"""
    data = {
        "username": "newuser",
        "password": "newpass123",
        "real_name": "新用户"
    }
    request = UserCreateRequest(**data)
    assert request.username == "newuser"
```

**Step 5: 运行测试**

```bash
cd backend
pytest app/tests/test_schemas.py -v
```

Expected: PASS

**Step 6: Commit**

```bash
git add backend/app/schemas/ backend/app/tests/test_schemas.py
git commit -m "rfeat: implement Pydantic validation schemas with tests"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 3 即可视为完成:

- [ ] 密码哈希工具已实现并测试
- [ ] JWT 工具已实现并测试
- [ ] 认证中间件已实现并测试
- [ ] RBAC 权限检查工具已实现并测试
- [ ] RBAC 权限装饰器已实现并测试
- [ ] Pydantic 验证 Schema 已创建并测试
- [ ] 所有测试通过

---

## 下一步

完成阶段 3 后,请继续执行 **阶段 4: 客户 MDM 核心功能**

文档: `docs/plans/2026-03-03-customer-manager-phase4-customer-mdm.md`
