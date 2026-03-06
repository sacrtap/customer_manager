"""
Health Service 测试 - 直接测试服务层

注意：根据 AGENTS.md 规则 8，Sanic 测试客户端与异步 SQLAlchemy 存在兼容性问题。
因此只测试 Service 层，不测试 API 层。
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import pytest_asyncio
import uuid

from app.models.customer import Customer
from app.services.health_service import HealthService


@pytest_asyncio.fixture(scope="function")
async def setup_test_customers(session: AsyncSession):
    """创建测试客户数据"""
    customers = [
        Customer(
            name=f"健康客户_{i}",
            code=f"HEALTHY_{uuid.uuid4()}",
            sales_rep_id=1,
            tier_level="A",
            health_score=80 + i,
            annual_consumption=10000 + i * 1000,
        )
        for i in range(3)
    ]
    customers += [
        Customer(
            name=f"风险客户_{i}",
            code=f"ATRISK_{uuid.uuid4()}",
            sales_rep_id=1,
            tier_level="B",
            health_score=50 + i,
            annual_consumption=5000 + i * 500,
        )
        for i in range(2)
    ]
    customers += [
        Customer(
            name=f"僵尸客户_{i}",
            code=f"ZOMBIE_{uuid.uuid4()}",
            sales_rep_id=1,
            tier_level="C",
            health_score=20 + i,
            annual_consumption=1000 + i * 100,
        )
        for i in range(2)
    ]

    for customer in customers:
        session.add(customer)
    await session.flush()

    yield customers


@pytest.mark.asyncio
async def test_get_health_dashboard_stats(session, setup_test_customers):
    """测试获取健康度仪表盘统计数据"""
    stats = await HealthService.get_dashboard_stats(session)

    # 验证返回格式
    assert "total_customers" in stats
    assert "healthy_customers" in stats
    assert "at_risk_customers" in stats
    assert "zombie_customers" in stats
    assert "health_trend" in stats
    assert "value_distribution" in stats

    # 验证趋势数据格式（7 天，每天包含 date 和 score）
    assert len(stats["health_trend"]) == 7
    for trend_item in stats["health_trend"]:
        assert "date" in trend_item
        assert "score" in trend_item
        # 验证分数在合理范围内（0-100）
        assert 0 <= trend_item["score"] <= 100

    # 验证分布数据格式（4 个层级）
    tier_levels = [item["tier"] for item in stats["value_distribution"]]
    assert tier_levels == ["A", "B", "C", "D"]

    # 验证每个层级都有 count 和 value 字段
    for tier_item in stats["value_distribution"]:
        assert "count" in tier_item
        assert "value" in tier_item

    # 验证至少有一些客户数据（来自 fixture）
    assert stats["total_customers"] > 0


@pytest.mark.asyncio
async def test_get_health_dashboard_with_mixed_data(session):
    """测试混合数据的健康度仪表盘（验证趋势和分布格式）"""
    stats = await HealthService.get_dashboard_stats(session)

    # 验证返回格式
    assert "total_customers" in stats
    assert "health_trend" in stats
    assert "value_distribution" in stats

    # 验证趋势数据格式（7 天，每天包含 date 和 score）
    assert len(stats["health_trend"]) == 7
    for trend_item in stats["health_trend"]:
        assert "date" in trend_item
        assert "score" in trend_item

    # 验证分布数据格式（4 个层级）
    assert len(stats["value_distribution"]) == 4
    tier_levels = [item["tier"] for item in stats["value_distribution"]]
    assert tier_levels == ["A", "B", "C", "D"]
