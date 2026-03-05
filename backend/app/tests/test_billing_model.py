"""
Billing 模型测试
"""

import pytest
import uuid
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_billing_model_creation(test_session: AsyncSession):
    """测试创建账单记录"""
    from app.models.billing import Billing
    from app.models.customer import Customer

    # 创建测试客户
    customer = Customer(
        name="Test Customer",
        code=f"TEST{uuid.uuid4().hex[:8]}",
        sales_rep_id=1,
        tier_level="A",
        status="active",
    )
    test_session.add(customer)
    await test_session.flush()

    # 创建账单记录
    billing = Billing(
        id=str(uuid.uuid4()),
        customer_id=customer.id,
        customer_name=customer.name,
        amount=1000.50,
        status="pending",
        billing_date=datetime.now(),
    )

    test_session.add(billing)
    await test_session.flush()
    await test_session.refresh(billing)

    # 验证账单记录创建成功
    assert billing.id is not None
    assert billing.customer_id == customer.id
    assert billing.customer_name == "Test Customer"
    assert billing.amount == 1000.50
    assert billing.status == "pending"
    assert billing.billing_date is not None


@pytest.mark.asyncio
async def test_billing_model_relationships(test_session: AsyncSession):
    """测试账单与客户的关联关系"""
    from app.models.billing import Billing
    from app.models.customer import Customer

    # 创建测试客户
    customer = Customer(
        name="Test Customer",
        code=f"TEST{uuid.uuid4().hex[:8]}",
        sales_rep_id=1,
        tier_level="A",
        status="active",
    )
    test_session.add(customer)
    await test_session.flush()

    # 创建多个账单记录
    billings = [
        Billing(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            customer_name=customer.name,
            amount=100.00,
            status="completed",
            billing_date=datetime.now(),
        ),
        Billing(
            id=str(uuid.uuid4()),
            customer_id=customer.id,
            customer_name=customer.name,
            amount=200.00,
            status="pending",
            billing_date=datetime.now(),
        ),
    ]

    for billing in billings:
        test_session.add(billing)

    await test_session.flush()
    await test_session.refresh(customer)

    # 验证关联关系
    assert len(customer.billings) == 2
    assert customer.billings[0].customer_id == customer.id
    assert customer.billings[1].customer_id == customer.id

    # 验证双向关联
    for billing in customer.billings:
        assert billing.customer.id == customer.id


@pytest.mark.asyncio
async def test_billing_model_constraints(test_session: AsyncSession):
    """测试账单模型的约束"""
    from app.models.billing import Billing
    from sqlalchemy.exc import IntegrityError

    # 测试缺少必需字段
    with pytest.raises(IntegrityError):
        billing = Billing(
            id=str(uuid.uuid4()),
            # 缺少 customer_id
            customer_name="Test Customer",
            amount=100.00,
            status="pending",
            billing_date=datetime.now(),
        )
        test_session.add(billing)
        await test_session.flush()

    await test_session.rollback()

    # 测试状态枚举值验证
    with pytest.raises(Exception):
        billing = Billing(
            id=str(uuid.uuid4()),
            customer_id=1,
            customer_name="Test Customer",
            amount=100.00,
            status="invalid_status",  # 无效的状态值
            billing_date=datetime.now(),
        )
        test_session.add(billing)
        await test_session.flush()


@pytest.mark.asyncio
async def test_billing_to_dict(test_session: AsyncSession):
    """测试账单的 to_dict 方法"""
    from app.models.billing import Billing
    from app.models.customer import Customer
    from datetime import datetime

    # 创建测试客户和账单
    customer = Customer(
        name="Test Customer",
        code=f"TEST{uuid.uuid4().hex[:8]}",
        sales_rep_id=1,
        tier_level="A",
        status="active",
    )
    test_session.add(customer)
    await test_session.flush()

    billing_date = datetime.now()
    billing = Billing(
        id=str(uuid.uuid4()),
        customer_id=customer.id,
        customer_name=customer.name,
        amount=1234.56,
        status="completed",
        billing_date=billing_date,
    )

    test_session.add(billing)
    await test_session.flush()
    await test_session.refresh(billing)

    # 测试 to_dict 方法
    billing_dict = billing.to_dict()

    assert billing_dict["id"] == billing.id
    assert billing_dict["customer_id"] == customer.id
    assert billing_dict["customer_name"] == "Test Customer"
    assert billing_dict["amount"] == 1234.56
    assert billing_dict["status"] == "completed"
    assert billing_dict["billing_date"] == billing_date.isoformat()
    assert "created_at" in billing_dict
