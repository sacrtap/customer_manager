"""
Customer Service 测试 - 测试客户服务层
参考 test_billing_api.py 模式直接测试服务层
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from app.models.customer import Customer
from app.models.user import User
from app.services.customer_service import CustomerService


@pytest_asyncio.fixture(scope="function")
async def test_sales_user(session: AsyncSession):
    """创建测试销售用户"""
    user = User(
        username=f"sales_{uuid.uuid4()}",
        password_hash="hashed_password",
        real_name="销售测试用户",
    )
    session.add(user)
    await session.flush()
    yield user


@pytest_asyncio.fixture(scope="function")
async def setup_test_customers(session: AsyncSession, test_sales_user: User):
    """创建测试客户数据"""
    customers = [
        Customer(
            name=f"测试客户{i + 1}",
            code=f"CUST_{uuid.uuid4().hex[:8]}",
            industry="科技" if i % 2 == 0 else "制造",
            sales_rep_id=test_sales_user.id,
            tier_level=["A", "B", "C", "D"][i % 4],
            annual_consumption=100000 * (i + 1),
            status="active" if i % 2 == 0 else "inactive",
            contact_person=f"联系人{i + 1}",
            contact_phone=f"1380000000{i}",
            contact_email=f"test{i + 1}@example.com",
            address=f"地址{i + 1}",
            remark=f"备注{i + 1}",
        )
        for i in range(6)
    ]

    for customer in customers:
        session.add(customer)
    await session.flush()

    yield {
        "customers": customers,
        "sales_user": test_sales_user,
    }


@pytest.mark.asyncio
async def test_list_customers(session, setup_test_customers):
    """测试获取客户列表"""
    result = await CustomerService.list_customers(
        session=session,
        filters={},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "size" in result

    assert result["total"] >= 6
    assert len(result["items"]) >= 6
    assert result["page"] == 1
    assert result["size"] == 10


@pytest.mark.asyncio
async def test_list_customers_pagination(session, setup_test_customers):
    """测试分页获取客户列表"""
    result = await CustomerService.list_customers(
        session=session,
        filters={},
        page=1,
        size=2,
        order_by=["created_at desc"],
    )

    assert result["total"] >= 6
    assert len(result["items"]) == 2
    assert result["page"] == 1
    assert result["size"] == 2


@pytest.mark.asyncio
async def test_list_customers_filter_by_industry(session, setup_test_customers):
    """测试按行业过滤客户"""
    result = await CustomerService.list_customers(
        session=session,
        filters={"industries": ["科技"]},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert result["total"] >= 3  # 至少 3 个科技行业客户


@pytest.mark.asyncio
async def test_list_customers_filter_by_status(session, setup_test_customers):
    """测试按状态过滤客户"""
    result = await CustomerService.list_customers(
        session=session,
        filters={"status": ["active"]},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert result["total"] >= 3  # 至少 3 个活跃客户


@pytest.mark.asyncio
async def test_get_customer(session, setup_test_customers):
    """测试获取客户详情"""
    customer_id = setup_test_customers["customers"][0].id
    user_id = setup_test_customers["sales_user"].id

    customer = await CustomerService.get_customer(
        session=session,
        customer_id=customer_id,
        user_id=user_id,
        user_role="sales",
    )

    assert customer is not None
    assert customer.id == customer_id
    assert "测试客户" in customer.name


@pytest.mark.asyncio
async def test_get_customer_not_found(session, test_sales_user):
    """测试获取不存在的客户"""
    customer = await CustomerService.get_customer(
        session=session,
        customer_id=99999,
        user_id=test_sales_user.id,
        user_role="sales",
    )

    assert customer is None


@pytest.mark.asyncio
async def test_create_customer(session, test_sales_user):
    """测试创建客户"""
    new_customer_data = {
        "name": "新客户",
        "code": f"CUST_NEW_{uuid.uuid4().hex[:8]}",
        "industry": "科技",
        "sales_rep_id": test_sales_user.id,
        "tier_level": "B",
        "annual_consumption": 500000,
        "status": "active",
        "contact_person": "张三",
        "contact_phone": "13800138000",
        "contact_email": "zhangsan@example.com",
        "address": "北京市朝阳区",
        "remark": "测试客户",
    }

    customer = await CustomerService.create_customer(
        session=session,
        data=new_customer_data,
        created_by=test_sales_user.id,
    )

    assert customer is not None
    assert customer.name == "新客户"


@pytest.mark.asyncio
async def test_update_customer(session, setup_test_customers):
    """测试更新客户"""
    customer_id = setup_test_customers["customers"][0].id
    user_id = setup_test_customers["sales_user"].id

    update_data = {
        "name": "更新后的客户名称",
        "contact_person": "新联系人",
        "contact_phone": "13900139000",
    }

    customer = await CustomerService.update_customer(
        session=session,
        customer_id=customer_id,
        data=update_data,
        user_id=user_id,
        user_role="sales",
    )

    assert customer is not None
    assert customer.name == "更新后的客户名称"
    assert customer.contact_person == "新联系人"


@pytest.mark.asyncio
async def test_update_customer_not_found(session, test_sales_user):
    """测试更新不存在的客户"""
    update_data = {"name": "更新名称"}

    customer = await CustomerService.update_customer(
        session=session,
        customer_id=99999,
        data=update_data,
        user_id=test_sales_user.id,
        user_role="sales",
    )

    assert customer is None


@pytest.mark.asyncio
async def test_delete_customer(session, setup_test_customers):
    """测试删除客户"""
    customer_id = setup_test_customers["customers"][-1].id
    user_id = setup_test_customers["sales_user"].id

    await CustomerService.delete_customer(
        session=session,
        customer_id=customer_id,
        user_id=user_id,
        user_role="sales",
    )

    # 验证客户已被删除
    customer = await CustomerService.get_customer(
        session=session,
        customer_id=customer_id,
        user_id=user_id,
        user_role="sales",
    )

    assert customer is None


@pytest.mark.asyncio
async def test_sales_can_only_view_own_customers(session, test_sales_user):
    """测试销售只能查看自己的客户"""
    # 创建另一个销售用户
    other_sales = User(
        username=f"other_sales_{uuid.uuid4()}",
        password_hash="hashed_password",
        real_name="其他销售",
    )
    session.add(other_sales)
    await session.flush()

    # 创建一个属于当前销售的客户
    customer = Customer(
        name="我的客户",
        code=f"CUST_{uuid.uuid4().hex[:8]}",
        sales_rep_id=test_sales_user.id,
        tier_level="A",
    )
    session.add(customer)
    await session.flush()

    # 其他销售应该看不到这个客户
    result = await CustomerService.get_customer(
        session=session,
        customer_id=customer.id,
        user_id=other_sales.id,
        user_role="sales",
    )

    assert result is None
