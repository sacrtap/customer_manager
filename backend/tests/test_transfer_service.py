"""
Transfer Service 测试 - 直接测试服务层
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import pytest_asyncio
import uuid

from app.models.transfer import CustomerTransfer
from app.models.customer import Customer
from app.models.user import User
from app.services.transfer_service import TransferService


@pytest_asyncio.fixture(scope="function")
async def setup_test_users(session: AsyncSession):
    """创建测试用户（两个销售代表）"""
    users = []
    for i in range(2):
        user = User(
            username=f"sales_{uuid.uuid4()}",
            password_hash="hashed_password",
            real_name=f"销售代表{i + 1}",
        )
        session.add(user)
    await session.flush()

    # 重新查询确保获取完整对象
    result = await session.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    yield users


@pytest_asyncio.fixture(scope="function")
async def setup_test_customer(session: AsyncSession, setup_test_users):
    """创建测试客户"""
    from_sales_rep = setup_test_users[0]

    customer = Customer(
        name=f"测试客户_{uuid.uuid4()}",
        code=f"TRANSFER_{uuid.uuid4()}",
        sales_rep_id=from_sales_rep.id,
        tier_level="A",
        health_score=80,
    )
    session.add(customer)
    await session.flush()

    yield customer


@pytest_asyncio.fixture(scope="function")
async def setup_test_transfers(
    session: AsyncSession, setup_test_users, setup_test_customer
):
    """创建测试转移记录"""
    from_sales_rep = setup_test_users[0]
    to_sales_rep = setup_test_users[1]
    customer = setup_test_customer

    transfers = []
    statuses = ["pending", "pending", "approved", "rejected", "completed"]

    for i, status in enumerate(statuses):
        transfer = CustomerTransfer(
            customer_id=customer.id,
            from_sales_rep_id=from_sales_rep.id,
            to_sales_rep_id=to_sales_rep.id,
            reason=f"转移原因_{i}",
            status=status,
            created_by=from_sales_rep.id,
        )
        if status != "pending":
            transfer.approved_by = to_sales_rep.id
            transfer.approved_at = datetime.utcnow()
        session.add(transfer)

    await session.flush()

    # 重新查询确保获取完整对象
    result = await session.execute(
        select(CustomerTransfer).order_by(CustomerTransfer.id)
    )
    transfers = result.scalars().all()
    yield transfers


@pytest.mark.asyncio
async def test_create_transfer(session, setup_test_users, setup_test_customer):
    """测试创建转移申请"""
    from_sales_rep = setup_test_users[0]
    to_sales_rep = setup_test_users[1]
    customer = setup_test_customer

    data = {
        "customer_id": customer.id,
        "to_sales_rep_id": to_sales_rep.id,
        "reason": "客户管理需求调整",
    }

    transfer = await TransferService.create_transfer(
        session=session,
        data=data,
        from_sales_rep_id=from_sales_rep.id,
        created_by=from_sales_rep.id,
    )

    assert transfer.customer_id == customer.id
    assert transfer.from_sales_rep_id == from_sales_rep.id
    assert transfer.to_sales_rep_id == to_sales_rep.id
    assert transfer.reason == "客户管理需求调整"
    assert transfer.status == "pending"
    assert transfer.created_by == from_sales_rep.id
    assert transfer.id is not None


@pytest.mark.asyncio
async def test_get_transfer(session, setup_test_transfers, setup_test_users):
    """测试获取转移详情"""
    transfer = setup_test_transfers[0]
    from_sales_rep = setup_test_users[0]

    # 管理员获取
    result = await TransferService.get_transfer(
        session=session,
        transfer_id=transfer.id,
        user_id=999,
        user_role="admin",
    )

    assert result is not None
    assert result.id == transfer.id
    assert result.customer_id == transfer.customer_id

    # 销售获取自己的转移
    result = await TransferService.get_transfer(
        session=session,
        transfer_id=transfer.id,
        user_id=from_sales_rep.id,
        user_role="sales",
    )

    assert result is not None
    assert result.id == transfer.id

    # 销售获取无关的转移
    result = await TransferService.get_transfer(
        session=session,
        transfer_id=transfer.id,
        user_id=9999,
        user_role="sales",
    )

    assert result is None


@pytest.mark.asyncio
async def test_list_transfers(session, setup_test_transfers):
    """测试获取转移列表"""
    result = await TransferService.list_transfers(
        session=session,
        filters={},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert "items" in result
    assert "total" in result
    assert result["total"] >= 5
    assert len(result["items"]) >= 5


@pytest.mark.asyncio
async def test_list_transfers_filter_by_status(
    session, setup_test_users, setup_test_customer
):
    """测试按状态筛选转移记录"""
    from_sales_rep = setup_test_users[0]
    to_sales_rep = setup_test_users[1]
    customer = setup_test_customer

    # 创建 2 个 pending 和 1 个 approved 的转移
    for i in range(2):
        transfer = CustomerTransfer(
            customer_id=customer.id,
            from_sales_rep_id=from_sales_rep.id,
            to_sales_rep_id=to_sales_rep.id,
            reason=f"待处理转移_{i}",
            status="pending",
            created_by=from_sales_rep.id,
        )
        session.add(transfer)

    # 创建一个 approved 的转移
    approved_transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="已审批转移",
        status="approved",
        created_by=from_sales_rep.id,
        approved_by=to_sales_rep.id,
        approved_at=datetime.utcnow(),
    )
    session.add(approved_transfer)
    await session.flush()

    result = await TransferService.list_transfers(
        session=session,
        filters={"status": "pending"},
        page=1,
        size=10,
        order_by=["created_at desc"],
    )

    assert result["total"] >= 2
    for item in result["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_list_transfers_pagination(session, setup_test_transfers):
    """测试分页获取转移记录"""
    result = await TransferService.list_transfers(
        session=session,
        filters={},
        page=1,
        size=2,
        order_by=["created_at desc"],
    )

    assert result["total"] >= 5
    assert len(result["items"]) == 2
    assert result["page"] == 1
    assert result["size"] == 2


@pytest.mark.asyncio
async def test_approve_transfer(session, setup_test_transfers, setup_test_users):
    """测试审批通过转移"""
    transfer = setup_test_transfers[0]  # pending状态
    approver = setup_test_users[1]

    result = await TransferService.approve_transfer(
        session=session,
        transfer_id=transfer.id,
        approved_by=approver.id,
    )

    assert result is not None
    assert result.status == "approved"
    assert result.approved_by == approver.id
    assert result.approved_at is not None


@pytest.mark.asyncio
async def test_reject_transfer(session, setup_test_transfers, setup_test_users):
    """测试拒绝转移"""
    transfer = setup_test_transfers[1]  # pending状态
    approver = setup_test_users[1]

    result = await TransferService.reject_transfer(
        session=session,
        transfer_id=transfer.id,
        approved_by=approver.id,
    )

    assert result is not None
    assert result.status == "rejected"
    assert result.approved_by == approver.id
    assert result.approved_at is not None


@pytest.mark.asyncio
async def test_complete_transfer(
    session, setup_test_transfers, setup_test_users, setup_test_customer
):
    """测试完成转移（更新客户销售）"""
    # 创建一个 approved 状态的转移
    from_sales_rep = setup_test_users[0]
    to_sales_rep = setup_test_users[1]
    customer = setup_test_customer

    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试完成转移",
        status="approved",
        created_by=from_sales_rep.id,
        approved_by=to_sales_rep.id,
        approved_at=datetime.utcnow(),
    )
    session.add(transfer)
    await session.flush()
    await session.refresh(transfer)

    # 确认当前客户的销售是原销售
    await session.refresh(customer)
    assert customer.sales_rep_id == from_sales_rep.id

    # 完成转移
    result = await TransferService.complete_transfer(
        session=session,
        transfer_id=transfer.id,
    )

    assert result is not None
    assert result.status == "completed"

    # 确认客户的销售已更新
    await session.refresh(customer)
    assert customer.sales_rep_id == to_sales_rep.id


@pytest.mark.asyncio
async def test_complete_transfer_not_approved(
    session, setup_test_users, setup_test_customer
):
    """测试完成非approved状态的转移（应该失败）"""
    from_sales_rep = setup_test_users[0]
    to_sales_rep = setup_test_users[1]
    customer = setup_test_customer

    # 创建一个 rejected 状态的转移
    transfer = CustomerTransfer(
        customer_id=customer.id,
        from_sales_rep_id=from_sales_rep.id,
        to_sales_rep_id=to_sales_rep.id,
        reason="测试拒绝的转移",
        status="rejected",
        created_by=from_sales_rep.id,
        approved_by=to_sales_rep.id,
        approved_at=datetime.utcnow(),
    )
    session.add(transfer)
    await session.flush()
    await session.refresh(transfer)

    with pytest.raises(ValueError, match="只有已审批的转移才能完成"):
        await TransferService.complete_transfer(
            session=session,
            transfer_id=transfer.id,
        )
