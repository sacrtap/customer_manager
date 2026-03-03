from datetime import datetime

import pytest
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
            contact_email="zhangsan@example.com",
        )
        session.add(customer)
        await session.commit()
        await session.refresh(customer)

        assert customer.id is not None
        assert customer.name == "测试客户"
        assert customer.code == "CUST001"
        assert customer.tier_level == "A"
        assert float(customer.annual_consumption) == 500000.00


@pytest.mark.asyncio
async def test_customer_to_dict():
    """测试客户转换为字典"""
    async with async_session_maker() as session:
        customer = Customer(name="测试客户 2", code="CUST002", sales_rep_id=1)
        session.add(customer)
        await session.commit()
        await session.refresh(customer)

        customer_dict = customer.to_dict()

        assert customer_dict["id"] == customer.id
        assert customer_dict["name"] == "测试客户 2"
        assert "sales_rep_id" in customer_dict
