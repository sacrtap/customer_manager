"""
Billing API 测试
"""

import pytest
import uuid
from datetime import datetime

from app.utils.jwt import create_access_token


pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_billing_list_requires_auth(test_app):
    """测试结算记录列表需要认证"""
    request, response = await test_app.test_client.get("/api/v1/billing")

    assert response.status == 401
    assert "error" in response.json


@pytest.mark.asyncio
async def test_billing_list_returns_empty_data(test_app):
    """测试结算记录列表返回空数据"""
    token = create_access_token(
        user_id=999999,
        role="admin",
        permissions=["billing.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/billing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert "data" in response.json

    data = response.json["data"]
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data

    assert isinstance(data["items"], list)
    assert data["total"] == 0
    assert data["page"] == 1
    assert data["page_size"] == 10


@pytest.mark.asyncio
async def test_billing_create_requires_auth(test_app):
    """测试创建结算记录需要认证"""
    request, response = await test_app.test_client.post(
        "/api/v1/billing",
        json={
            "customer_id": 1,
            "customer_name": "测试客户",
            "amount": 1000.00,
        },
    )

    assert response.status == 401


@pytest.mark.asyncio
async def test_billing_create_and_list(test_app):
    """测试创建和列出结算记录"""
    token = create_access_token(
        user_id=999998,
        role="admin",
        permissions=["billing.view", "billing.create"],
    )

    # 创建结算记录
    unique_id = str(uuid.uuid4())[:8]
    create_data = {
        "customer_id": 1,
        "customer_name": f"测试客户_{unique_id}",
        "amount": 15000.00,
        "billing_date": datetime.now().isoformat(),
    }

    create_request, create_response = await test_app.test_client.post(
        "/api/v1/billing",
        json=create_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert create_response.status == 200
    assert "data" in create_response.json

    created_billing = create_response.json["data"]
    assert created_billing["customer_name"] == create_data["customer_name"]
    assert created_billing["amount"] == create_data["amount"]
    assert created_billing["status"] == "pending"
    assert "id" in created_billing
    assert "created_at" in created_billing

    # 列出结算记录
    list_request, list_response = await test_app.test_client.get(
        "/api/v1/billing",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert list_response.status == 200
    data = list_response.json["data"]

    assert data["total"] >= 1
    assert len(data["items"]) >= 1

    # 验证创建的记录在列表中
    found = False
    for item in data["items"]:
        if item["customer_name"] == create_data["customer_name"]:
            found = True
            assert item["amount"] == create_data["amount"]
            assert item["status"] == "pending"
            break

    assert found, "创建的结算记录应该在列表中"


@pytest.mark.asyncio
async def test_billing_list_pagination(test_app):
    """测试结算记录列表分页"""
    token = create_access_token(
        user_id=999997,
        role="admin",
        permissions=["billing.view", "billing.create"],
    )

    # 创建多条记录
    for i in range(5):
        unique_id = str(uuid.uuid4())[:8]
        await test_app.test_client.post(
            "/api/v1/billing",
            json={
                "customer_id": 1,
                "customer_name": f"分页测试客户_{i}_{unique_id}",
                "amount": 1000.00 * (i + 1),
                "billing_date": datetime.now().isoformat(),
            },
            headers={"Authorization": f"Bearer {token}"},
        )

    # 测试第一页
    request1, response1 = await test_app.test_client.get(
        "/api/v1/billing?page=1&size=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response1.status == 200
    data1 = response1.json["data"]
    assert data1["page"] == 1
    assert data1["page_size"] == 2
    assert len(data1["items"]) <= 2

    # 测试第二页
    request2, response2 = await test_app.test_client.get(
        "/api/v1/billing?page=2&size=2",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response2.status == 200
    data2 = response2.json["data"]
    assert data2["page"] == 2
    assert data2["page_size"] == 2


@pytest.mark.asyncio
async def test_billing_list_filter_by_status(test_app):
    """测试按状态过滤结算记录"""
    token = create_access_token(
        user_id=999996,
        role="admin",
        permissions=["billing.view", "billing.create"],
    )

    # 创建一个 pending 状态的记录
    unique_id = str(uuid.uuid4())[:8]
    await test_app.test_client.post(
        "/api/v1/billing",
        json={
            "customer_id": 1,
            "customer_name": f"Pending 客户_{unique_id}",
            "amount": 5000.00,
            "billing_date": datetime.now().isoformat(),
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # 过滤 pending 状态
    request, response = await test_app.test_client.get(
        "/api/v1/billing?status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    data = response.json["data"]

    # 所有返回的记录都应该是 pending 状态
    for item in data["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_billing_create_validation(test_app):
    """测试创建结算记录的验证"""
    token = create_access_token(
        user_id=999995,
        role="admin",
        permissions=["billing.view", "billing.create"],
    )

    # 缺少 customer_name
    request1, response1 = await test_app.test_client.post(
        "/api/v1/billing",
        json={
            "customer_id": 1,
            "amount": 1000.00,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response1.status == 400
    assert "error" in response1.json

    # 缺少 customer_id
    request2, response2 = await test_app.test_client.post(
        "/api/v1/billing",
        json={
            "customer_name": "测试客户",
            "amount": 1000.00,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response2.status == 400
    assert "error" in response2.json


@pytest.mark.asyncio
async def test_billing_permissions(test_app):
    """测试结算记录权限检查"""
    # 测试没有权限的情况
    token_no_perm = create_access_token(
        user_id=999994,
        role="user",
        permissions=["other.permission"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/billing",
        headers={"Authorization": f"Bearer {token_no_perm}"},
    )

    assert response.status == 403

    # 测试有 billing.view 权限的情况
    token_view_perm = create_access_token(
        user_id=999993,
        role="user",
        permissions=["billing.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/billing",
        headers={"Authorization": f"Bearer {token_view_perm}"},
    )

    assert response.status == 200
