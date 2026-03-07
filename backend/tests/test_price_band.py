"""
Price Band Service 测试 - 测试价格区间服务层
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import uuid

from app.models.price_band import PriceBand
from app.services.price_band_service import PriceBandService


@pytest_asyncio.fixture(scope="function")
async def test_user(session: AsyncSession):
    """创建测试用户"""
    from app.models.user import User

    user = User(
        username=f"band_test_{uuid.uuid4().hex[:8]}",
        password_hash="hashed_password",
        real_name="价格区间测试用户",
    )
    session.add(user)
    await session.flush()
    yield user


@pytest_asyncio.fixture(scope="function")
async def test_price_config(session: AsyncSession, test_user):
    """创建测试价格配置"""
    from app.models.price_config import PriceConfig

    config = PriceConfig(
        code=f"TEST_CFG_{uuid.uuid4().hex[:8]}",
        name="测试价格配置",
        description="用于价格区间测试",
        base_price=100.0,
        status="active",
        created_by=test_user.id,
    )
    session.add(config)
    await session.flush()
    yield config


@pytest_asyncio.fixture(scope="function")
async def setup_test_price_bands(session: AsyncSession, test_price_config, test_user):
    """创建测试价格区间"""
    bands = [
        PriceBand(
            code=f"BAND_{uuid.uuid4().hex[:8]}",
            name=f"价格区间{i + 1}_{uuid.uuid4().hex[:4]}",
            description=f"测试价格区间{i + 1}",
            price_config_id=test_price_config.id,
            min_quantity=1 if i == 0 else (i * 10 + 1),
            max_quantity=10 if i == 0 else (i + 1) * 10,
            min_amount=100.0 * (i + 1),
            max_amount=1000.0 * (i + 1),
            unit_price=50.0 + i * 10,
            discount_rate=5.0 * (i + 1),
            final_price=45.0 + i * 10,
            priority=i + 1,
            is_active=i % 2 == 0,
            valid_from=datetime.now() - timedelta(days=30),
            valid_until=datetime.now() + timedelta(days=30),
            created_by=test_user.id,
            created_at=datetime.now(),
        )
        for i in range(3)
    ]

    for band in bands:
        session.add(band)
    await session.flush()

    yield {"bands": bands, "config": test_price_config, "user": test_user}


@pytest.mark.asyncio
async def test_create_price_band(session, test_price_config, test_user):
    """测试创建价格区间"""
    band_data = {
        "code": f"NEW_{uuid.uuid4().hex[:8]}",
        "name": f"新价格区间_{uuid.uuid4().hex[:4]}",
        "description": "测试新价格区间",
        "price_config_id": test_price_config.id,
        "min_quantity": 1,
        "max_quantity": 100,
        "min_amount": 100.0,
        "max_amount": 10000.0,
        "unit_price": 80.0,
        "discount_rate": 10.0,
        "final_price": 72.0,
        "priority": 1,
        "status": "active",
    }

    band = await PriceBandService.create_price_band(
        session=session,
        data=band_data,
        created_by=test_user.id,
    )

    assert band is not None
    assert "新价格区间" in band.name
    assert band.price_config_id == test_price_config.id


@pytest.mark.asyncio
async def test_get_price_band(session, setup_test_price_bands):
    """测试获取价格区间详情"""
    band_id = setup_test_price_bands["bands"][0].id

    band = await PriceBandService.get_price_band(
        session=session,
        price_band_id=band_id,
    )

    assert band is not None
    assert band.id == band_id
    assert "价格区间" in band.name


@pytest.mark.asyncio
async def test_get_price_band_not_found(session):
    """测试获取不存在的价格区间"""
    band = await PriceBandService.get_price_band(
        session=session,
        price_band_id=99999,
    )

    assert band is None


@pytest.mark.asyncio
async def test_update_price_band(session, setup_test_price_bands, test_user):
    """测试更新价格区间"""
    band_id = setup_test_price_bands["bands"][0].id

    update_data = {
        "name": f"更新后的区间名_{uuid.uuid4().hex[:4]}",
        "description": "更新后的描述",
        "unit_price": 99.0,
        "discount_rate": 15.0,
        "priority": 10,
    }

    band = await PriceBandService.update_price_band(
        session=session,
        price_band_id=band_id,
        data=update_data,
        updated_by=test_user.id,
    )

    assert band is not None
    assert "更新后的区间名" in band.name
    assert band.unit_price == 99.0
    assert band.discount_rate == 15.0


@pytest.mark.asyncio
async def test_update_price_band_not_found(session, test_user):
    """测试更新不存在的价格区间"""
    update_data = {"name": "更新名字", "unit_price": 88.0}

    band = await PriceBandService.update_price_band(
        session=session,
        price_band_id=99999,
        data=update_data,
        updated_by=test_user.id,
    )

    assert band is None


@pytest.mark.asyncio
async def test_delete_price_band(session, setup_test_price_bands):
    """测试删除价格区间"""
    band_id = setup_test_price_bands["bands"][-1].id

    # 先获取区间
    band = await PriceBandService.get_price_band(
        session=session,
        price_band_id=band_id,
    )
    assert band is not None

    # 删除区间
    deleted = await PriceBandService.delete_price_band(
        session=session,
        price_band_id=band_id,
    )

    assert deleted is True

    # 验证区间已被删除
    band = await PriceBandService.get_price_band(
        session=session,
        price_band_id=band_id,
    )

    assert band is None


@pytest.mark.asyncio
async def test_delete_price_band_not_found(session):
    """测试删除不存在的价格区间"""
    result = await PriceBandService.delete_price_band(
        session=session,
        price_band_id=99999,
    )

    assert result is False
