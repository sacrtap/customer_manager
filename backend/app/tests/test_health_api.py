"""
Health API 测试
"""

import pytest
import uuid
from app.utils.jwt import create_access_token


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_health_dashboard_requires_auth(test_app):
    """测试健康度仪表盘需要认证"""
    request, response = await test_app.test_client.get("/api/v1/health/dashboard")

    assert response.status == 401
    assert "error" in response.json


@pytest.mark.asyncio
async def test_health_dashboard_returns_data(test_app):
    """测试健康度仪表盘返回数据"""
    # 创建测试用户 token
    token = create_access_token(
        user_id=999999,
        role="admin",
        permissions=["dashboard.view", "customer.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/health/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert "data" in response.json

    data = response.json["data"]
    assert "total_customers" in data
    assert "healthy_customers" in data
    assert "at_risk_customers" in data
    assert "zombie_customers" in data
    assert "health_trend" in data
    assert "value_distribution" in data

    # 验证数据类型
    assert isinstance(data["total_customers"], int)
    assert isinstance(data["healthy_customers"], int)
    assert isinstance(data["at_risk_customers"], int)
    assert isinstance(data["zombie_customers"], int)
    assert isinstance(data["health_trend"], list)
    assert isinstance(data["value_distribution"], list)

    # 验证趋势数据有 7 个点
    assert len(data["health_trend"]) == 7

    # 验证响应有时间戳
    assert "timestamp" in response.json


@pytest.mark.asyncio
async def test_health_dashboard_value_distribution_structure(test_app):
    """测试价值分布数据结构"""
    token = create_access_token(
        user_id=999998,
        role="admin",
        permissions=["dashboard.view", "customer.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/health/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200

    distribution = response.json["data"]["value_distribution"]

    # 验证每个层级的结构
    for item in distribution:
        assert "tier" in item
        assert "count" in item
        assert "value" in item
        assert item["tier"] in ["A", "B", "C", "D"]
        assert isinstance(item["count"], int)
        assert isinstance(item["value"], (int, float))


@pytest.mark.asyncio
async def test_health_dashboard_permissions(test_app):
    """测试健康度仪表盘权限检查"""
    # 测试没有权限的情况
    token_no_perm = create_access_token(
        user_id=999997,
        role="user",
        permissions=["other.permission"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/health/dashboard",
        headers={"Authorization": f"Bearer {token_no_perm}"},
    )

    assert response.status == 403

    # 测试有 dashboard.view 权限的情况
    token_dash_perm = create_access_token(
        user_id=999996,
        role="user",
        permissions=["dashboard.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/health/dashboard",
        headers={"Authorization": f"Bearer {token_dash_perm}"},
    )

    assert response.status == 200
