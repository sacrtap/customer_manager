"""
Price Config Service 测试 - 测试价格配置服务层
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
import uuid

from app.models.price_config import PriceConfig
from app.services.price_config_service import PriceConfigService


@pytest_asyncio.fixture(scope="function")
async def test_user(session: AsyncSession):
    """创建测试用户"""
    from app.models.user import User

    user = User(
        username=f"price_test_{uuid.uuid4().hex[:8]}",
        password_hash="hashed_password",
        real_name="价格测试用户",
    )
    session.add(user)
    await session.flush()
    yield user


@pytest_asyncio.fixture(scope="function")
async def setup_test_price_configs(session: AsyncSession, test_user):
    """创建测试价格配置"""
    configs = [
        PriceConfig(
            code=f"CFG_{uuid.uuid4().hex[:8]}",
            name=f"价格配置{i + 1}_{uuid.uuid4().hex[:4]}",
            description=f"测试价格配置{i + 1}",
            base_price=100.0 * (i + 1),
            status="active" if i % 2 == 0 else "inactive",
            created_by=test_user.id,
        )
        for i in range(4)
    ]

    for config in configs:
        session.add(config)
    await session.flush()

    yield {"configs": configs, "user": test_user}


@pytest.mark.asyncio
async def test_create_price_config(session, test_user):
    """测试创建价格配置"""
    config_data = {
        "code": f"NEW_{uuid.uuid4().hex[:8]}",
        "name": f"新价格配置_{uuid.uuid4().hex[:4]}",
        "description": "测试新价格配置",
        "base_price": 500.0,
        "status": "active",
    }

    config = await PriceConfigService.create_price_config(
        session=session,
        data=config_data,
        created_by=test_user.id,
    )

    assert config is not None
    assert "新价格配置" in config.name
    assert config.base_price == 500.0


@pytest.mark.asyncio
async def test_get_price_config(session, setup_test_price_configs):
    """测试获取价格配置详情"""
    config_id = setup_test_price_configs["configs"][0].id

    config = await PriceConfigService.get_price_config(
        session=session,
        price_config_id=config_id,
    )

    assert config is not None
    assert config.id == config_id
    assert "价格配置" in config.name


@pytest.mark.asyncio
async def test_get_price_config_not_found(session):
    """测试获取不存在的价格配置"""
    config = await PriceConfigService.get_price_config(
        session=session,
        price_config_id=99999,
    )

    assert config is None


@pytest.mark.asyncio
async def test_update_price_config(session, setup_test_price_configs, test_user):
    """测试更新价格配置"""
    config_id = setup_test_price_configs["configs"][0].id

    update_data = {
        "name": f"更新后的配置名_{uuid.uuid4().hex[:4]}",
        "description": "更新后的描述",
        "base_price": 999.0,
    }

    config = await PriceConfigService.update_price_config(
        session=session,
        price_config_id=config_id,
        data=update_data,
        updated_by=test_user.id,
    )

    assert config is not None
    assert "更新后的配置名" in config.name
    assert config.base_price == 999.0


@pytest.mark.asyncio
async def test_update_price_config_not_found(session, test_user):
    """测试更新不存在的价格配置"""
    update_data = {"name": "更新名字", "base_price": 888.0}

    config = await PriceConfigService.update_price_config(
        session=session,
        price_config_id=99999,
        data=update_data,
        updated_by=test_user.id,
    )

    assert config is None


@pytest.mark.asyncio
async def test_delete_price_config(session, setup_test_price_configs):
    """测试删除价格配置"""
    config_id = setup_test_price_configs["configs"][-1].id

    # 先获取配置
    config = await PriceConfigService.get_price_config(
        session=session,
        price_config_id=config_id,
    )
    assert config is not None

    # 删除配置
    deleted = await PriceConfigService.delete_price_config(
        session=session,
        price_config_id=config_id,
    )

    assert deleted is True

    # 验证配置已被删除
    config = await PriceConfigService.get_price_config(
        session=session,
        price_config_id=config_id,
    )

    assert config is None


@pytest.mark.asyncio
async def test_delete_price_config_not_found(session):
    """测试删除不存在的价格配置"""
    result = await PriceConfigService.delete_price_config(
        session=session,
        price_config_id=99999,
    )

    assert result is False
