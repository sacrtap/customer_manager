"""
Customer Transfer Service 测试
测试 Service 层功能，绕过 Sanic 测试客户端与异步 SQLAlchemy 的兼容性问题
"""

import pytest
import uuid
from datetime import datetime

from app.models.transfer import CustomerTransfer
from app.models.customer import Customer
from app.models.user import User
from app.services.transfer_service import TransferService


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_create_transfer(test_session):
    """测试创建转移申请"""
    # 创建测试用户
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        password_hash="hashed_password",
        real_name="From Sales",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        password_hash="hashed_password",
        real_name="To Sales",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    # 创建测试客户
    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
        tier_level="C",
    )
    test_session.add(customer)
    await test_session.flush()

    # 创建转移
    transfer_data = {
        "customer_id": customer.id,
        "to_sales_rep_id": to_sales_rep.id,
        "reason": "测试转移原因",
    }

    transfer = await TransferService.create_transfer(
        session=test_session,
        data=transfer_data,
        from_sales_rep_id=from_sales_rep.id,
        created_by=from_sales_rep.id,
    )

    assert transfer.id is not None
    assert transfer.customer_id == customer.id
    assert transfer.from_sales_rep_id == from_sales_rep.id
    assert transfer.to_sales_rep_id == to_sales_rep.id
    assert transfer.reason == "测试转移原因"
    assert transfer.status == "pending"
    assert transfer.created_by == from_sales_rep.id


@pytest.mark.asyncio
async def test_get_transfer(test_session):
    """测试获取转移详情"""
    # 创建测试数据
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试原因",
        status="pending",
        created_by=from_sales_rep.id,
    )
    test_session.add(transfer)
    await test_session.flush()

    # 获取转移
    result = await TransferService.get_transfer(
        session=test_session,
        transfer_id=transfer.id,
        user_id=from_sales_rep.id,
        user_role="sales",
    )

    assert result is not None
    assert result.id == transfer.id
    assert result.customer_id == customer.id


@pytest.mark.asyncio
async def test_approve_transfer(test_session):
    """测试审批通过转移"""
    # 创建测试数据
    approver = User(
        username=f"approver_{uuid.uuid4().hex[:8]}",
        email=f"approver{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Manager",
    )
    test_session.add(approver)
    await test_session.flush()

    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试原因",
        status="pending",
        created_by=from_sales_rep.id,
    )
    test_session.add(transfer)
    await test_session.flush()

    # 审批通过
    result = await TransferService.approve_transfer(
        session=test_session,
        transfer_id=transfer.id,
        approved_by=approver.id,
    )

    assert result is not None
    assert result.status == "approved"
    assert result.approved_by == approver.id
    assert result.approved_at is not None


@pytest.mark.asyncio
async def test_reject_transfer(test_session):
    """测试拒绝转移"""
    # 创建测试数据
    approver = User(
        username=f"approver_{uuid.uuid4().hex[:8]}",
        email=f"approver{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Manager",
    )
    test_session.add(approver)
    await test_session.flush()

    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试原因",
        status="pending",
        created_by=from_sales_rep.id,
    )
    test_session.add(transfer)
    await test_session.flush()

    # 拒绝转移
    result = await TransferService.reject_transfer(
        session=test_session,
        transfer_id=transfer.id,
        approved_by=approver.id,
    )

    assert result is not None
    assert result.status == "rejected"
    assert result.approved_by == approver.id


@pytest.mark.asyncio
async def test_complete_transfer(test_session):
    """测试完成转移"""
    # 创建测试数据
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试原因",
        status="approved",  # 必须是 approved 状态
        created_by=from_sales_rep.id,
    )
    test_session.add(transfer)
    await test_session.flush()

    # 完成转移
    result = await TransferService.complete_transfer(
        session=test_session,
        transfer_id=transfer.id,
    )

    assert result is not None
    assert result.status == "completed"

    # 验证客户的销售已更新
    await test_session.refresh(customer)
    assert customer.sales_rep_id == to_sales_rep.id


@pytest.mark.asyncio
async def test_complete_transfer_invalid_state(test_session):
    """测试完成非 approved 状态的转移"""
    # 创建测试数据
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试原因",
        status="pending",  # pending 状态，不能完成
        created_by=from_sales_rep.id,
    )
    test_session.add(transfer)
    await test_session.flush()

    # 尝试完成转移，应该抛出 ValueError
    with pytest.raises(ValueError, match="只有已审批的转移才能完成"):
        await TransferService.complete_transfer(
            session=test_session,
            transfer_id=transfer.id,
        )


@pytest.mark.asyncio
async def test_list_transfers(test_session):
    """测试分页查询转移列表"""
    # 创建测试数据
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    # 创建多条转移记录
    for i in range(5):
        transfer = CustomerTransfer(
            customer_id=customer.id,
            from_sales_rep_id=from_sales_rep.id,
            to_sales_rep_id=to_sales_rep.id,
            reason=f"测试原因_{i}",
            status="pending" if i % 2 == 0 else "approved",
            created_by=from_sales_rep.id,
        )
        test_session.add(transfer)
    await test_session.flush()

    # 查询所有记录
    result = await TransferService.list_transfers(
        session=test_session,
        filters={},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert result["total"] == 5
    assert len(result["items"]) == 5
    assert result["page"] == 1
    assert result["size"] == 10


@pytest.mark.asyncio
async def test_list_transfers_filter_by_status(test_session):
    """测试按状态过滤转移列表"""
    # 创建测试数据
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    # 创建不同状态的转移记录
    for status in ["pending", "pending", "approved", "rejected", "completed"]:
        transfer = CustomerTransfer(
            customer_id=customer.id,
            from_sales_rep_id=from_sales_rep.id,
            to_sales_rep_id=to_sales_rep.id,
            reason=f"测试原因_{status}",
            status=status,
            created_by=from_sales_rep.id,
        )
        test_session.add(transfer)
    await test_session.flush()

    # 过滤 pending 状态
    result = await TransferService.list_transfers(
        session=test_session,
        filters={"status": "pending"},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert result["total"] == 2
    for item in result["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_transfer_to_dict(test_session):
    """测试转移记录的 to_dict 方法"""
    # 创建测试数据
    from_sales_rep = User(
        username=f"from_sales_{uuid.uuid4().hex[:8]}",
        email=f"from{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    to_sales_rep = User(
        username=f"to_sales_{uuid.uuid4().hex[:8]}",
        email=f"to{uuid.uuid4().hex[:8]}@test.com",
        password_hash="hashed_password",
        real_name="Sales Rep",
    )
    test_session.add(from_sales_rep)
    test_session.add(to_sales_rep)
    await test_session.flush()

    customer = Customer(
        name=f"测试客户_{uuid.uuid4().hex[:8]}",
        sales_rep_id=from_sales_rep.id,
    )
    test_session.add(customer)
    await test_session.flush()

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试原因",
        status="pending",
        created_by=from_sales_rep.id,
    )
    test_session.add(transfer)
    await test_session.flush()

    # 测试 to_dict
    transfer_dict = transfer.to_dict()

    assert "id" in transfer_dict
    assert transfer_dict["customer_id"] == customer.id
    assert transfer_dict["from_sales_rep_id"] == from_sales_rep.id
    assert transfer_dict["to_sales_rep_id"] == to_sales_rep.id
    assert transfer_dict["reason"] == "测试原因"
    assert transfer_dict["status"] == "pending"
    assert "created_at" in transfer_dict
    assert "updated_at" in transfer_dict
