# 阶段 4: 客户 MDM 核心功能

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 实现客户主数据管理核心功能,包括客户 CRUD API、多维度查询、客户服务层

**预计时间:** 7-10 天

**前置依赖:** 阶段 3: 认证与 RBAC 权限系统

**Architecture:** 
- 创建客户服务层(业务逻辑)
- 实现客户 API 蓝图
- 支持多维度查询(关键词、销售、行业、状态、等级、金额范围、时间范围)
- 实现权限控制(销售只看自己客户)

**Tech Stack:**
- 服务层: Python 异步服务
- API: Sanic 蓝图
- 查询: SQLAlchemy 2.0 异步查询
- 验证: Pydantic

---

## Task 16: 创建客户服务层

**Files:**
- Create: `backend/app/services/customer_service.py`
- Create: `backend/app/tests/test_customer_service.py`

**Step 1: 创建客户服务层**

```python
# backend/app/services/customer_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict
from datetime import datetime

from app.models.customer import Customer
from app.database import async_session_maker


class CustomerService:
    """客户服务层"""
    
    @staticmethod
    async def create_customer(
        session: AsyncSession,
        data: Dict,
        created_by: int
    ) -> Customer:
        """创建客户"""
        customer = Customer(
            name=data["name"],
            code=data.get("code"),
            industry=data.get("industry"),
            sales_rep_id=data["sales_rep_id"],
            tier_level=data.get("tier_level", "D"),
            annual_consumption=data.get("annual_consumption", 0),
            status=data.get("status", "active"),
            contact_person=data.get("contact_person"),
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            address=data.get("address"),
            remark=data.get("remark")
        )
        
        session.add(customer)
        await session.commit()
        await session.refresh(customer)
        
        return customer
    
    @staticmethod
    async def get_customer(
        session: AsyncSession,
        customer_id: int,
        user_id: int,
        user_role: str
    ) -> Optional[Customer]:
        """获取客户详情"""
        query = select(Customer).where(Customer.id == customer_id)
        
        # 销售只能看自己客户
        if user_role == "sales":
            query = query.where(Customer.sales_rep_id == user_id)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_customer(
        session: AsyncSession,
        customer_id: int,
        data: Dict,
        user_id: int,
        user_role: str
    ) -> Optional[Customer]:
        """更新客户"""
        query = select(Customer).where(Customer.id == customer_id)
        
        # 销售只能看自己客户
        if user_role == "sales":
            query = query.where(Customer.sales_rep_id == user_id)
        
        result = await session.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return None
        
        # 更新字段
        if "name" in data:
            customer.name = data["name"]
        if "code" in data:
            customer.code = data["code"]
        if "industry" in data:
            customer.industry = data["industry"]
        if "tier_level" in data:
            customer.tier_level = data["tier_level"]
        if "annual_consumption" in data:
            customer.annual_consumption = data["annual_consumption"]
        if "status" in data:
            customer.status = data["status"]
        if "contact_person" in data:
            customer.contact_person = data["contact_person"]
        if "contact_phone" in data:
            customer.contact_phone = data["contact_phone"]
        if "contact_email" in data:
            customer.contact_email = data["contact_email"]
        if "address" in data:
            customer.address = data["address"]
        if "remark" in data:
            customer.remark = data["remark"]
        
        customer.updated_at = datetime.utcnow()
        
        await session.commit()
        await session.refresh(customer)
        
        return customer
    
    @staticmethod
    async def delete_customer(
        session: AsyncSession,
        customer_id: int,
        user_id: int,
        user_role: str
    ) -> bool:
        """删除客户"""
        query = select(Customer).where(Customer.id == customer_id)
        
        # 销售只能看自己客户
        if user_role == "sales":
            query = query.where(Customer.sales_rep_id == user_id)
        
        result = await session.execute(query)
        customer = result.scalar_one_or_none()
        
        if not customer:
            return False
        
        await session.delete(customer)
        await session.commit()
        
        return True
    
    @staticmethod
    async def list_customers(
        session: AsyncSession,
        filters: Dict,
        page: int,
        size: int,
        order_by: List[str]
    ) -> Dict:
        """分页查询客户列表"""
        query = select(Customer)
        
        # 应用过滤条件
        if "keyword" in filters and filters["keyword"]:
            keyword = filters["keyword"]
            query = query.where(
                or_(
                    Customer.name.ilike(f"%{keyword}%"),
                    Customer.code.ilike(f"%{keyword}%"),
                    Customer.contact_person.ilike(f"%{keyword}%")
                )
            )
        
        if "sales_rep_ids" in filters and filters["sales_rep_ids"]:
            query = query.where(Customer.sales_rep_id.in_(filters["sales_rep_ids"]))
        
        if "industries" in filters and filters["industries"]:
            query = query.where(Customer.industry.in_(filters["industries"]))
        
        if "status" in filters and filters["status"]:
            query = query.where(Customer.status.in_(filters["status"]))
        
        if "tier_levels" in filters and filters["tier_levels"]:
            query = query.where(Customer.tier_level.in_(filters["tier_levels"]))
        
        if "annual_consumption_min" in filters:
            query = query.where(Customer.annual_consumption >= filters["annual_consumption_min"])
        
        if "annual_consumption_max" in filters:
            query = query.where(Customer.annual_consumption <= filters["annual_consumption_max"])
        
        if "created_at_start" in filters:
            query = query.where(Customer.created_at >= filters["created_at_start"])
        
        if "created_at_end" in filters:
            query = query.where(Customer.created_at <= filters["created_at_end"])
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()
        
        # 应用排序
        for order in order_by:
            if order.endswith(" desc"):
                field = order.replace(" desc", "")
                column = getattr(Customer, field)
                query = query.order_by(column.desc())
            else:
                field = order.replace(" asc", "")
                column = getattr(Customer, field)
                query = query.order_by(column.asc())
        
        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)
        
        # 执行查询
        result = await session.execute(query)
        customers = result.scalars().all()
        
        return {
            "items": [customer.to_dict() for customer in customers],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }
```

**Step 2: 创建客户服务层测试**

```python
# backend/app/tests/test_customer_service.py
import pytest
from app.database import async_session_maker
from app.services.customer_service import CustomerService


@pytest.mark.asyncio
async def test_create_customer():
    """测试创建客户"""
    data = {
        "name": "测试客户",
        "code": "CUST001",
        "industry": "科技",
        "sales_rep_id": 1,
        "tier_level": "A",
        "annual_consumption": 500000.00,
        "contact_person": "张三",
        "contact_phone": "13800138000"
    }
    
    async with async_session_maker() as session:
        customer = await CustomerService.create_customer(session, data, 1)
        
        assert customer.id is not None
        assert customer.name == "测试客户"
        assert customer.code == "CUST001"


@pytest.mark.asyncio
async def test_list_customers():
    """测试查询客户列表"""
    filters = {
        "industries": ["科技"],
        "tier_levels": ["A", "B"]
    }
    
    async with async_session_maker() as session:
        # 先创建一些客户
        for i in range(5):
            data = {
                "name": f"客户{i}",
                "sales_rep_id": 1,
                "industry": "科技",
                "tier_level": "A" if i < 3 else "B"
            }
            await CustomerService.create_customer(session, data, 1)
        
        # 查询
        result = await CustomerService.list_customers(
            session=session,
            filters=filters,
            page=1,
            size=10,
            order_by=["created_at desc"]
        )
        
        assert "items" in result
        assert "total" in result
        assert len(result["items"]) <= 10
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_customer_service.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/services/customer_service.py backend/app/tests/test_customer_service.py
git commit -m "feat: implement customer service layer with tests"
```

---

## Task 17: 实现客户 API 蓝图

**Files:**
- Create: `backend/app/blueprints/customer.py`
- Create: `backend/app/tests/test_customer_api.py`

**Step 1: 创建客户 API 蓝图**

```python
# backend/app/blueprints/customer.py
from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from datetime import datetime

from app.database import get_db_session
from app.services.customer_service import CustomerService
from app.decorators.rbac import require_permissions
from app.schemas.customer import (
    CustomerCreateRequest,
    CustomerUpdateRequest
)


customer_bp = Blueprint("customer", url_prefix="/api/v1/customers")


@customer_bp.get("/")
@require_permissions("customer.view")
async def list_customers(request: Request):
    """客户列表 API"""
    # 解析查询参数
    try:
        params = CustomerQuerySchema(**request.args)
    except Exception as e:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            },
            status=400
        )
    
    # 构建过滤条件
    filters = {}
    if params.keyword:
        filters["keyword"] = params.keyword
    if params.sales_rep_ids:
        filters["sales_rep_ids"] = params.sales_rep_ids
    if params.industries:
        filters["industries"] = params.industries
    if params.status:
        filters["status"] = params.status
    if params.tier_levels:
        filters["tier_levels"] = params.tier_levels
    if params.annual_consumption_min:
        filters["annual_consumption_min"] = params.annual_consumption_min
    if params.annual_consumption_max:
        filters["annual_consumption_max"] = params.annual_consumption_max
    if params.created_at_start:
        filters["created_at_start"] = params.created_at_start
    if params.created_at_end:
        filters["created_at_end"] = params.created_at_end
    
    # 销售只能看自己客户
    user = request.ctx.user
    if user["role"] == "sales":
        filters["sales_rep_ids"] = [user["user_id"]]
    
    # 排序
    order_by = []
    if params.sort_field:
        direction = "desc" if params.sort_desc else "asc"
        order_by.append(f"{params.sort_field} {direction}")
    else:
        order_by.append("created_at desc")
    
    # 查询
    async for session in get_db_session():
        result = await CustomerService.list_customers(
            session=session,
            filters=filters,
            page=params.page,
            size=params.size,
            order_by=order_by
        )
        
        return json({
            "data": result,
            "timestamp": datetime.utcnow().isoformat()
        })


@customer_bp.post("/")
@require_permissions("customer.create")
async def create_customer(request: Request):
    """创建客户 API"""
    try:
        data = CustomerCreateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            },
            status=400
        )
    
    user = request.ctx.user
    
    async for session in get_db_session():
        # 创建客户
        customer = await CustomerService.create_customer(
            session=session,
            data=data.dict(),
            created_by=user["user_id"]
        )
        
        return json({
            "data": customer.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })


@customer_bp.get("/<customer_id:int>")
@require_permissions("customer.view")
async def get_customer(request: Request, customer_id: int):
    """获取客户详情 API"""
    user = request.ctx.user
    
    async for session in get_db_session():
        customer = await CustomerService.get_customer(
            session=session,
            customer_id=customer_id,
            user_id=user["user_id"],
            user_role=user["role"]
        )
        
        if not customer:
            return JSONResponse(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "客户不存在"
                    }
                },
                status=404
            )
        
        return json({
            "data": customer.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })


@customer_bp.put("/<customer_id:int>")
@require_permissions("customer.update")
async def update_customer(request: Request, customer_id: int):
    """更新客户 API"""
    try:
        data = CustomerUpdateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            },
            status=400
        )
    
    user = request.ctx.user
    
    async for session in get_db_session():
        customer = await CustomerService.update_customer(
            session=session,
            customer_id=customer_id,
            data=data.dict(exclude_unset=True),
            user_id=user["user_id"],
            user_role=user["role"]
        )
        
        if not customer:
            return JSONResponse(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "客户不存在"
                    }
                },
                status=404
            )
        
        return json({
            "data": customer.to_dict(),
            "timestamp": datetime.utcnow().isoformat()
        })


@customer_bp.delete("/<customer_id:int>")
@require_permissions("customer.delete")
async def delete_customer(request: Request, customer_id: int):
    """删除客户 API"""
    user = request.ctx.user
    
    async for session in get_db_session():
        success = await CustomerService.delete_customer(
            session=session,
            customer_id=customer_id,
            user_id=user["user_id"],
            user_role=user["role"]
        )
        
        if not success:
            return JSONResponse(
                {
                    "error": {
                        "code": "NOT_FOUND",
                        "message": "客户不存在或无权限"
                    }
                },
                status=404
            )
        
        return json({
            "data": {"message": "客户删除成功"},
            "timestamp": datetime.utcnow().isoformat()
        })
```

**Step 2: 创建客户 API 测试**

```python
# backend/app/tests/test_customer_api.py
import pytest
from sanic import Sanic
from app.blueprints.customer import customer_bp
from app.middlewares.auth import attach_auth_middleware


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    app.blueprint(customer_bp)
    return app


@pytest.mark.asyncio
async def test_list_customers_without_token(app):
    """测试列表 API 无 Token"""
    request, response = app.test_client.get("/api/v1/customers")
    assert response.status == 401


@pytest.mark.asyncio
async def test_list_customers_with_token(app):
    """测试列表 API 有效 Token"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(1, "admin", ["*"])
    
    request, response = app.test_client.get(
        "/api/v1/customers",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status == 200
    assert "data" in response.json
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_customer_api.py -v
```

Expected: PASS

**Step 4: 注册蓝图到应用**

```python
# 在 backend/app/__init__.py 中添加
from .blueprints import customer

def create_app():
    """应用工厂函数"""
    app = Sanic("customer_manager")
    
    # ... 现有代码 ...
    
    # 注册蓝图
    app.blueprint(customer.customer_bp)
    
    return app
```

**Step 5: Commit**

```bash
git add backend/app/blueprints/customer.py backend/app/tests/test_customer_api.py backend/app/__init__.py
git commit -m "feat: implement customer API blueprint with tests"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 4 即可视为完成:

- [ ] 客户服务层已实现并测试
- [ ] 客户 API 蓝图已实现并测试
- [ ] 客户 CRUD 功能完整(创建/读取/更新/删除)
- [ ] 多维度查询功能完整
- [ ] 权限控制已实现(销售只看自己客户)
- [ ] 所有测试通过
- [ ] 蓝图已注册到应用

---

## 下一步

完成阶段 4 后,请继续执行 **阶段 5: 批量导入导出功能**

文档: `docs/plans/2026-03-03-customer-manager-phase5-import-export.md`
