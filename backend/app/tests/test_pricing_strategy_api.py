"""
定价策略管理 API 测试
"""

import pytest
import uuid
from app.utils.jwt import create_access_token


# 使用数据库中存在的用户 ID
TEST_USER_ID = 122


@pytest.fixture
def app(test_session):
    """创建测试应用"""
    from sanic import Sanic
    from app.blueprints.pricing_strategy import pricing_strategy_bp
    from app.middlewares.auth import attach_auth_middleware
    from app.decorators.rbac import require_permissions

    app = Sanic(f"test_app_{uuid.uuid4().hex[:8]}")
    attach_auth_middleware(app)
    app.blueprint(pricing_strategy_bp)

    @app.get("/protected")
    @require_permissions("pricing.view")
    async def protected(request):
        return {"user": request.ctx.user}

    return app


def test_list_strategies_without_token(app):
    """测试列表 API 无 Token"""
    request, response = app.test_client.get("/api/v1/pricing-strategies")
    assert response.status == 401


def test_list_strategies_with_token(app):
    """测试列表 API 有效 Token"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["*"])

    request, response = app.test_client.get(
        "/api/v1/pricing-strategies", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status == 200
    assert "data" in response.json


def test_create_strategy_without_permission(app):
    """测试创建策略没有权限"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "user", ["pricing.view"])

    request, response = app.test_client.post(
        "/api/v1/pricing-strategies",
        json={
            "name": "测试策略",
            "code": "TEST_STRATEGY",
            "discount_type": "percentage",
            "discount_value": 10,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 403


def test_create_strategy_with_permission(app):
    """测试创建策略有权限"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["pricing.create"])

    request, response = app.test_client.post(
        "/api/v1/pricing-strategies",
        json={
            "name": "测试策略",
            "code": "TEST_STRATEGY",
            "discount_type": "percentage",
            "discount_value": 10,
            "status": "active",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert response.json["data"]["name"] == "测试策略"
    assert response.json["data"]["code"] == "TEST_STRATEGY"


def test_get_strategy_not_found(app):
    """测试获取不存在的策略"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["pricing.view"])

    request, response = app.test_client.get(
        "/api/v1/pricing-strategies/999", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status == 404


@pytest.mark.asyncio
async def test_update_strategy(app, test_session):
    """测试更新策略"""
    from app.utils.jwt import create_access_token
    from app.models.pricing_strategy import PricingStrategy
    from datetime import datetime

    # 先创建测试数据
    strategy = PricingStrategy(
        name="原名称",
        code=f"UPDATE_{uuid.uuid4().hex[:8]}",
        discount_type="percentage",
        discount_value=10,
        status="active",
        created_by=TEST_USER_ID,
    )
    test_session.add(strategy)
    await test_session.flush()

    token = create_access_token(TEST_USER_ID, "admin", ["pricing.update"])

    request, response = app.test_client.put(
        f"/api/v1/pricing-strategies/{strategy.id}",
        json={"name": "新名称", "discount_value": 20},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert response.json["data"]["name"] == "新名称"
    assert response.json["data"]["discount_value"] == 20


@pytest.mark.asyncio
async def test_delete_strategy(app, test_session):
    """测试删除策略"""
    from app.utils.jwt import create_access_token
    from app.models.pricing_strategy import PricingStrategy

    # 先创建测试数据
    strategy = PricingStrategy(
        name="删除测试",
        code=f"DELETE_{uuid.uuid4().hex[:8]}",
        discount_type="percentage",
        discount_value=10,
        status="active",
        created_by=TEST_USER_ID,
    )
    test_session.add(strategy)
    await test_session.flush()

    token = create_access_token(TEST_USER_ID, "admin", ["pricing.delete"])

    request, response = app.test_client.delete(
        f"/api/v1/pricing-strategies/{strategy.id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200

    # 验证删除
    request, response = app.test_client.get(
        f"/api/v1/pricing-strategies/{strategy.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status == 404


def test_list_strategies_filter_by_status(app, test_session):
    """测试按状态筛选策略"""
    from app.utils.jwt import create_access_token
    from app.models.pricing_strategy import PricingStrategy

    # 创建测试数据
    strategies = [
        PricingStrategy(
            name="策略 1",
            code="TEST_1",
            discount_type="percentage",
            discount_value=10,
            status="active",
            created_by=1,
        ),
        PricingStrategy(
            name="策略 2",
            code="TEST_2",
            discount_type="percentage",
            discount_value=20,
            status="inactive",
            created_by=1,
        ),
        PricingStrategy(
            name="策略 3",
            code="TEST_3",
            discount_type="fixed",
            discount_value=100,
            status="active",
            created_by=1,
        ),
    ]
    test_session.add_all(strategies)
    test_session.flush()

    token = create_access_token(1, "admin", ["pricing.view"])

    # 筛选启用状态
    request, response = app.test_client.get(
        "/api/v1/pricing-strategies?status=active",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert response.json["data"]["total"] >= 2


def test_list_strategies_filter_by_discount_type(app, test_session):
    """测试按折扣类型筛选策略"""
    from app.utils.jwt import create_access_token
    from app.models.pricing_strategy import PricingStrategy

    # 创建测试数据
    strategies = [
        PricingStrategy(
            name="策略 1",
            code="TEST_1",
            discount_type="percentage",
            discount_value=10,
            status="active",
            created_by=1,
        ),
        PricingStrategy(
            name="策略 2",
            code="TEST_2",
            discount_type="fixed",
            discount_value=100,
            status="active",
            created_by=1,
        ),
    ]
    test_session.add_all(strategies)
    test_session.flush()

    token = create_access_token(1, "admin", ["pricing.view"])

    # 筛选百分比类型
    request, response = app.test_client.get(
        "/api/v1/pricing-strategies?discount_type=percentage",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert response.json["data"]["total"] >= 1
