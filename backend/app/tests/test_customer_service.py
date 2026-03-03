import uuid
import pytest
from app.database import async_session_maker
from app.services.customer_service import CustomerService


@pytest.mark.asyncio
async def test_create_customer(test_session):
    """测试创建客户"""
    code = f"CUST{uuid.uuid4().hex[:6].upper()}"
    data = {
        "name": "测试客户",
        "code": code,
        "industry": "科技",
        "sales_rep_id": 1,
        "tier_level": "A",
        "annual_consumption": 500000.00,
        "contact_person": "张三",
        "contact_phone": "13800138000",
    }

    customer = await CustomerService.create_customer(test_session, data, 1)

    assert customer.id is not None
    assert customer.name == "测试客户"
    assert customer.code == code


@pytest.mark.asyncio
async def test_list_customers(test_session):
    """测试查询客户列表"""
    filters = {"industries": ["科技"], "tier_levels": ["A", "B"]}

    # 先创建一些客户
    for i in range(5):
        data = {
            "name": f"客户{i}",
            "sales_rep_id": 1,
            "industry": "科技",
            "tier_level": "A" if i < 3 else "B",
        }
        await CustomerService.create_customer(test_session, data, 1)

    # 查询
    result = await CustomerService.list_customers(
        session=test_session,
        filters=filters,
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert "items" in result
    assert "total" in result
    assert len(result["items"]) <= 10
