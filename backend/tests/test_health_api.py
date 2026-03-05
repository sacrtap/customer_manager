"""
Health Service 测试 - 直接测试服务层
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta
import pytest_asyncio
import uuid

from app.models.customer import Customer
from app.config import settings
from app.database import Base
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
async def test_get_health_dashboard(app, setup_test_customers):
    """测试获取健康度仪表盘数据"""
    token = create_access_token("test_user", "testuser", ["dashboard.view"])

    request, response = await app.test_client.get(
        "/api/v1/health/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert "data" in response.json
    assert "timestamp" in response.json

    data = response.json["data"]
    assert "total_customers" in data
    assert "healthy_customers" in data
    assert "at_risk_customers" in data
    assert "zombie_customers" in data
    assert "health_trend" in data
    assert "value_distribution" in data

    # 验证统计数据
    assert data["total_customers"] == 7
    assert data["healthy_customers"] == 3
    assert data["at_risk_customers"] == 2
    assert data["zombie_customers"] == 2


@pytest.mark.asyncio
async def test_get_health_dashboard_empty(app):
    """测试空数据的健康度仪表盘"""
    token = create_access_token("test_user", "testuser", ["dashboard.view"])

    request, response = await app.test_client.get(
        "/api/v1/health/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    data = response.json["data"]

    assert data["total_customers"] == 0
    assert data["healthy_customers"] == 0
    assert data["at_risk_customers"] == 0
    assert data["zombie_customers"] == 0
    assert data["health_trend"] == []
    assert data["value_distribution"] == [
        {"tier": "A", "count": 0, "value": 0},
        {"tier": "B", "count": 0, "value": 0},
        {"tier": "C", "count": 0, "value": 0},
        {"tier": "D", "count": 0, "value": 0},
    ]


@pytest.mark.asyncio
async def test_get_health_dashboard_stats(session, setup_test_customers):
    """测试获取健康度仪表盘统计数据"""
    stats = await HealthService.get_dashboard_stats(session)

    assert "total_customers" in stats
    assert "healthy_customers" in stats
    assert "at_risk_customers" in stats
    assert "zombie_customers" in stats
    assert "health_trend" in stats
    assert "value_distribution" in stats

    # 验证统计数据
    assert stats["total_customers"] == 7
    assert stats["healthy_customers"] == 3
    assert stats["at_risk_customers"] == 2
    assert stats["zombie_customers"] == 2


@pytest.mark.asyncio
async def test_get_health_dashboard_empty(session):
    """测试空数据的健康度仪表盘"""
    stats = await HealthService.get_dashboard_stats(session)

    assert stats["total_customers"] == 0
    assert stats["healthy_customers"] == 0
    assert stats["at_risk_customers"] == 0
    assert stats["zombie_customers"] == 0
    assert len(stats["health_trend"]) == 7
    assert stats["value_distribution"] == [
        {"tier": "A", "count": 0, "value": 0},
        {"tier": "B", "count": 0, "value": 0},
        {"tier": "C", "count": 0, "value": 0},
        {"tier": "D", "count": 0, "value": 0},
    ]


@pytest.mark.asyncio
async def test_get_health_dashboard_stats(session, setup_test_customers):
    """测试获取健康度仪表盘统计数据"""
    stats = await HealthService.get_dashboard_stats(session)

    assert "total_customers" in stats
    assert "healthy_customers" in stats
    assert "at_risk_customers" in stats
    assert "zombie_customers" in stats
    assert "health_trend" in stats
    assert "value_distribution" in stats

    # 验证统计数据
    assert stats["total_customers"] == 7
    assert stats["healthy_customers"] == 3
    assert stats["at_risk_customers"] == 2
    assert stats["zombie_customers"] == 2


@pytest.mark.asyncio
async def test_get_health_dashboard_empty(session):
    """测试空数据的健康度仪表盘"""
    stats = await HealthService.get_dashboard_stats(session)

    assert stats["total_customers"] == 0
    assert stats["healthy_customers"] == 0
    assert stats["at_risk_customers"] == 0
    assert stats["zombie_customers"] == 0
    assert len(stats["health_trend"]) == 7
    assert stats["value_distribution"] == [
        {"tier": "A", "count": 0, "value": 0},
        {"tier": "B", "count": 0, "value": 0},
        {"tier": "C", "count": 0, "value": 0},
        {"tier": "D", "count": 0, "value": 0},
    ]
