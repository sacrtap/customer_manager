"""
Pricing Strategy Service 测试 - 测试定价策略服务层
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

from app.models.pricing_strategy import PricingStrategy
from app.services.pricing_strategy_service import PricingStrategyService


@pytest_asyncio.fixture(scope="function")
async def test_user(session: AsyncSession):
    """创建测试用户"""
    from app.models.user import User

    user = User(
        username=f"pricing_test_{uuid.uuid4().hex[:8]}",
        password_hash="hashed_password",
        real_name="定价测试用户",
    )
    session.add(user)
    await session.flush()
    yield user


@pytest_asyncio.fixture(scope="function")
async def setup_test_strategies(session: AsyncSession, test_user):
    """创建测试定价策略"""
    strategies = [
        PricingStrategy(
            name=f"策略{i + 1}_{uuid.uuid4().hex[:4]}",
            code=f"STRAT_{uuid.uuid4().hex[:8]}",
            description=f"测试策略{i + 1}",
            applicable_customer_type="enterprise" if i % 2 == 0 else "smb",
            applicable_tier_levels='["A", "B"]' if i % 2 == 0 else '["C", "D"]',
            discount_type="percentage" if i % 2 == 0 else "fixed",
            discount_value=10.0 * (i + 1),
            priority=i + 1,
            status="active" if i % 2 == 0 else "inactive",
            valid_from=datetime.now() - timedelta(days=30),
            valid_to=datetime.now() + timedelta(days=30),
            created_by=test_user.id,
            created_at=datetime.now(),
        )
        for i in range(4)
    ]

    for strategy in strategies:
        session.add(strategy)
    await session.flush()

    yield {"strategies": strategies, "user": test_user}


@pytest.mark.asyncio
async def test_create_strategy(session, test_user):
    """测试创建定价策略"""
    strategy_data = {
        "name": f"新策略_{uuid.uuid4().hex[:4]}",
        "code": f"NEW_{uuid.uuid4().hex[:8]}",
        "description": "测试新策略",
        "applicable_customer_type": "enterprise",
        "applicable_tier_levels": '["A", "B"]',
        "discount_type": "percentage",
        "discount_value": 15.0,
        "priority": 1,
        "status": "active",
    }

    strategy = await PricingStrategyService.create_strategy(
        session=session,
        data=strategy_data,
        created_by=test_user.id,
    )

    assert strategy is not None
    assert "新策略" in strategy.name
    assert strategy.discount_value == 15.0


@pytest.mark.asyncio
async def test_get_strategy(session, setup_test_strategies):
    """测试获取定价策略详情"""
    strategy_id = setup_test_strategies["strategies"][0].id

    strategy = await PricingStrategyService.get_strategy(
        session=session,
        strategy_id=strategy_id,
    )

    assert strategy is not None
    assert strategy.id == strategy_id
    assert "策略" in strategy.name


@pytest.mark.asyncio
async def test_get_strategy_not_found(session):
    """测试获取不存在的定价策略"""
    strategy = await PricingStrategyService.get_strategy(
        session=session,
        strategy_id=99999,
    )

    assert strategy is None


@pytest.mark.asyncio
async def test_update_strategy(session, setup_test_strategies, test_user):
    """测试更新定价策略"""
    strategy_id = setup_test_strategies["strategies"][0].id

    update_data = {
        "name": f"更新后的策略名_{uuid.uuid4().hex[:4]}",
        "description": "更新后的描述",
        "discount_value": 25.0,
        "priority": 10,
    }

    strategy = await PricingStrategyService.update_strategy(
        session=session,
        strategy_id=strategy_id,
        data=update_data,
        updated_by=test_user.id,
    )

    assert strategy is not None
    assert "更新后的策略名" in strategy.name
    assert strategy.discount_value == 25.0
    assert strategy.priority == 10


@pytest.mark.asyncio
async def test_update_strategy_not_found(session, test_user):
    """测试更新不存在的定价策略"""
    update_data = {"name": "更新名字", "discount_value": 20.0}

    strategy = await PricingStrategyService.update_strategy(
        session=session,
        strategy_id=99999,
        data=update_data,
        updated_by=test_user.id,
    )

    assert strategy is None


@pytest.mark.asyncio
async def test_delete_strategy(session, setup_test_strategies):
    """测试删除定价策略"""
    strategy_id = setup_test_strategies["strategies"][-1].id

    # 先获取策略
    strategy = await PricingStrategyService.get_strategy(
        session=session,
        strategy_id=strategy_id,
    )
    assert strategy is not None

    # 删除策略
    deleted = await PricingStrategyService.delete_strategy(
        session=session,
        strategy_id=strategy_id,
    )

    assert deleted is True

    # 验证策略已被删除
    strategy = await PricingStrategyService.get_strategy(
        session=session,
        strategy_id=strategy_id,
    )

    assert strategy is None


@pytest.mark.asyncio
async def test_delete_strategy_not_found(session):
    """测试删除不存在的定价策略"""
    result = await PricingStrategyService.delete_strategy(
        session=session,
        strategy_id=99999,
    )

    assert result is False
