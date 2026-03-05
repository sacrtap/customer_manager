"""
Billing Service 测试 - 直接测试服务层
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import pytest_asyncio
import uuid

from app.models.billing import Billing
from app.models.customer import Customer
from app.services.billing_service import BillingService


@pytest_asyncio.fixture(scope="function")
async def setup_test_billings(session: AsyncSession):
    """创建测试结算记录"""
    # 先创建客户
    customer = Customer(
        name="测试客户",
        code=f"BILL_TEST_{uuid.uuid4()}",
        sales_rep_id=1,
        tier_level="A",
        health_score=80,
    )
    session.add(customer)
    await session.flush()

    # 创建结算记录
    billings = [
        Billing(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            customer_name=customer.name,
            amount=1000.00 + i * 100,
            status="completed" if i % 2 == 0 else "pending",
            billing_date=datetime.now() - timedelta(days=i),
        )
        for i in range(5)
    ]

    for billing in billings:
        session.add(billing)
    await session.flush()

    yield {"customer": customer, "billings": billings}


@pytest.mark.asyncio
async def test_get_billing_list(session, setup_test_billings):
    """测试获取结算记录列表"""
    result = await BillingService.get_billing_list(
        session=session,
        page=1,
        size=10,
    )

    assert "items" in result
    assert "total" in result
    assert "page" in result
    assert "page_size" in result

    assert result["total"] == 5
    assert len(result["items"]) == 5
    assert result["page"] == 1
    assert result["page_size"] == 10


@pytest.mark.asyncio
async def test_get_billing_list_pagination(session, setup_test_billings):
    """测试分页获取结算记录"""
    result = await BillingService.get_billing_list(
        session=session,
        page=1,
        size=2,
    )

    assert result["total"] == 5
    assert len(result["items"]) == 2
    assert result["page"] == 1
    assert result["page_size"] == 2


@pytest.mark.asyncio
async def test_get_billing_list_filter_by_status(session, setup_test_billings):
    """测试按状态筛选结算记录"""
    result = await BillingService.get_billing_list(
        session=session,
        page=1,
        size=10,
        status="completed",
    )

    assert result["total"] <= 5
    for item in result["items"]:
        assert item["status"] == "completed"


@pytest.mark.asyncio
async def test_get_billing_list_filter_by_customer(session, setup_test_billings):
    """测试按客户筛选结算记录"""
    customer_id = setup_test_billings["customer"].id

    result = await BillingService.get_billing_list(
        session=session,
        page=1,
        size=10,
        customer_id=customer_id,
    )

    assert result["total"] == 5
    for item in result["items"]:
        assert item["customer_id"] == customer_id


@pytest.mark.asyncio
async def test_create_billing(session, setup_test_billings):
    """测试创建结算记录"""
    customer = setup_test_billings["customer"]

    billing = await BillingService.create_billing(
        session=session,
        customer_id=customer.id,
        customer_name=customer.name,
        amount=2000.00,
        billing_date=datetime.now(),
        billing_id=str(uuid.uuid4()),
    )

    assert billing.customer_id == customer.id
    assert billing.customer_name == customer.name
    assert billing.amount == 2000.00
    assert billing.status == "pending"
    assert billing.id is not None


@pytest.mark.asyncio
async def test_get_billing_list_empty(session):
    """测试空数据的结算记录列表"""
    result = await BillingService.get_billing_list(
        session=session,
        page=1,
        size=10,
    )

    assert result["total"] == 0
    assert len(result["items"]) == 0
    assert result["page"] == 1
    assert result["page_size"] == 10
