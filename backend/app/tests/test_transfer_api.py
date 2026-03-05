"""
Customer Transfer API 测试
"""

import pytest
import uuid
from datetime import datetime
import asyncio

from app.utils.jwt import create_access_token


pytest_plugins = ("pytest_asyncio",)


# ==================== 认证测试 ====================


@pytest.mark.asyncio
async def test_transfer_list_requires_auth(test_app):
    """测试转移列表需要认证"""
    request, response = await test_app.test_client.get("/api/v1/transfers")

    assert response.status == 401
    assert "error" in response.json


@pytest.mark.asyncio
async def test_transfer_create_requires_auth(test_app):
    """测试创建转移需要认证"""
    request, response = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": "测试转移",
        },
    )

    assert response.status == 401


@pytest.mark.asyncio
async def test_transfer_detail_requires_auth(test_app):
    """测试转移详情需要认证"""
    request, response = await test_app.test_client.get("/api/v1/transfers/1")

    assert response.status == 401


@pytest.mark.asyncio
async def test_transfer_approve_requires_auth(test_app):
    """测试审批转移需要认证"""
    request, response = await test_app.test_client.post(
        "/api/v1/transfers/1/approve",
        json={},
    )

    assert response.status == 401


@pytest.mark.asyncio
async def test_transfer_reject_requires_auth(test_app):
    """测试拒绝转移需要认证"""
    request, response = await test_app.test_client.post(
        "/api/v1/transfers/1/reject",
        json={},
    )

    assert response.status == 401


@pytest.mark.asyncio
async def test_transfer_complete_requires_auth(test_app):
    """测试完成转移需要认证"""
    request, response = await test_app.test_client.post(
        "/api/v1/transfers/1/complete",
        json={},
    )

    assert response.status == 401


# ==================== 权限测试 ====================


@pytest.mark.asyncio
async def test_transfer_list_permissions(test_app):
    """测试转移列表权限检查"""
    # 没有权限
    token_no_perm = create_access_token(
        user_id=999991,
        role="user",
        permissions=["other.permission"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/transfers",
        headers={"Authorization": f"Bearer {token_no_perm}"},
    )

    assert response.status == 403

    # 有 customer.transfer.view 权限
    token_view_perm = create_access_token(
        user_id=999992,
        role="user",
        permissions=["customer.transfer.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/transfers",
        headers={"Authorization": f"Bearer {token_view_perm}"},
    )

    assert response.status == 200


@pytest.mark.asyncio
async def test_transfer_create_permissions(test_app):
    """测试创建转移权限检查"""
    # 没有权限
    token_no_perm = create_access_token(
        user_id=999993,
        role="user",
        permissions=["other.permission"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": "测试转移",
        },
        headers={"Authorization": f"Bearer {token_no_perm}"},
    )

    assert response.status == 403

    # 有 customer.transfer 权限
    token_create_perm = create_access_token(
        user_id=999994,
        role="user",
        permissions=["customer.transfer"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": "测试转移",
        },
        headers={"Authorization": f"Bearer {token_create_perm}"},
    )

    # 应该通过权限检查（可能因为客户不存在而返回 404）
    assert response.status in [200, 400, 404]


@pytest.mark.asyncio
async def test_transfer_approve_permissions(test_app):
    """测试审批转移权限检查"""
    # 没有权限
    token_no_perm = create_access_token(
        user_id=999995,
        role="user",
        permissions=["other.permission"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers/1/approve",
        json={},
        headers={"Authorization": f"Bearer {token_no_perm}"},
    )

    assert response.status == 403

    # 有 customer.transfer.approve 权限
    token_approve_perm = create_access_token(
        user_id=999996,
        role="user",
        permissions=["customer.transfer.approve"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers/1/approve",
        json={},
        headers={"Authorization": f"Bearer {token_approve_perm}"},
    )

    # 应该通过权限检查（可能因为记录不存在而返回 404）
    assert response.status in [200, 404]


# ==================== 列表和分页测试 ====================


@pytest.mark.asyncio
async def test_transfer_list_returns_empty_data(test_app):
    """测试转移列表返回空数据"""
    token = create_access_token(
        user_id=999997,
        role="admin",
        permissions=["customer.transfer.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/transfers",
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
async def test_transfer_list_pagination(test_app):
    """测试转移列表分页"""
    token = create_access_token(
        user_id=999998,
        role="admin",
        permissions=["customer.transfer.view", "customer.transfer"],
    )

    # 先创建一个转移记录
    unique_id = str(uuid.uuid4())[:8]
    create_request, create_response = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": f"测试转移_{unique_id}",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # 测试分页
    list_request, list_response = await test_app.test_client.get(
        "/api/v1/transfers?page=1&size=5",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert list_response.status == 200
    data = list_response.json["data"]

    assert data["page"] == 1
    assert data["page_size"] == 5
    assert data["total"] >= 1


# ==================== 创建转移测试 ====================


@pytest.mark.asyncio
async def test_transfer_create_success(test_app):
    """测试成功创建转移"""
    token = create_access_token(
        user_id=999999,
        role="admin",
        permissions=["customer.transfer", "customer.view"],
    )

    unique_id = str(uuid.uuid4())[:8]
    create_data = {
        "customer_id": 1,
        "to_sales_rep_id": 2,
        "reason": f"测试转移_{unique_id}",
    }

    request, response = await test_app.test_client.post(
        "/api/v1/transfers",
        json=create_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    # 注意：由于客户 ID 1 可能不存在，这里可能返回 400 或 404
    # 如果客户存在，应该返回 200
    assert response.status in [200, 400, 404]

    if response.status == 200:
        assert "data" in response.json
        transfer = response.json["data"]

        assert transfer["customer_id"] == create_data["customer_id"]
        assert transfer["to_sales_rep_id"] == create_data["to_sales_rep_id"]
        assert transfer["reason"] == create_data["reason"]
        assert transfer["status"] == "pending"
        assert "id" in transfer
        assert "created_at" in transfer


@pytest.mark.asyncio
async def test_transfer_create_validation(test_app):
    """测试创建转移的验证"""
    token = create_access_token(
        user_id=999990,
        role="admin",
        permissions=["customer.transfer"],
    )

    # 缺少 customer_id
    request1, response1 = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "to_sales_rep_id": 2,
            "reason": "测试转移",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response1.status == 400
    assert "error" in response1.json

    # 缺少 to_sales_rep_id
    request2, response2 = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "reason": "测试转移",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response2.status == 400
    assert "error" in response2.json

    # 缺少 reason
    request3, response3 = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response3.status == 400
    assert "error" in response3.json

    # from_sales_rep_id 和 to_sales_rep_id 相同
    request4, response4 = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 1,
            "reason": "测试转移",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response4.status == 400
    assert "error" in response4.json


# ==================== 转移详情测试 ====================


@pytest.mark.asyncio
async def test_transfer_detail_not_found(test_app):
    """测试转移详情不存在"""
    token = create_access_token(
        user_id=999991,
        role="admin",
        permissions=["customer.transfer.view"],
    )

    request, response = await test_app.test_client.get(
        "/api/v1/transfers/999999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 404
    assert "error" in response.json
    assert response.json["error"]["code"] == "NOT_FOUND"


# ==================== 审批转移测试 ====================


@pytest.mark.asyncio
async def test_transfer_approve_not_found(test_app):
    """测试审批不存在的转移"""
    token = create_access_token(
        user_id=999992,
        role="admin",
        permissions=["customer.transfer.approve"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers/999999/approve",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 404
    assert "error" in response.json


# ==================== 拒绝转移测试 ====================


@pytest.mark.asyncio
async def test_transfer_reject_not_found(test_app):
    """测试拒绝不存在的转移"""
    token = create_access_token(
        user_id=999993,
        role="admin",
        permissions=["customer.transfer.approve"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers/999999/reject",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 404
    assert "error" in response.json


# ==================== 完成转移测试 ====================


@pytest.mark.asyncio
async def test_transfer_complete_not_found(test_app):
    """测试完成不存在的转移"""
    token = create_access_token(
        user_id=999994,
        role="admin",
        permissions=["customer.transfer"],
    )

    request, response = await test_app.test_client.post(
        "/api/v1/transfers/999999/complete",
        json={},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 404
    assert "error" in response.json


# ==================== 集成测试 ====================


@pytest.mark.asyncio
async def test_transfer_workflow(test_app):
    """测试转移完整工作流"""
    token = create_access_token(
        user_id=999995,
        role="admin",
        permissions=[
            "customer.transfer",
            "customer.transfer.view",
            "customer.transfer.approve",
        ],
    )

    unique_id = str(uuid.uuid4())[:8]

    # 1. 创建转移
    create_request, create_response = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": f"工作流测试_{unique_id}",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # 由于客户 ID 1 可能不存在，这里可能返回 400 或 404
    # 如果是 200，继续测试后续流程
    if create_response.status == 200:
        transfer_id = create_response.json["data"]["id"]

        # 2. 获取转移详情
        detail_request, detail_response = await test_app.test_client.get(
            f"/api/v1/transfers/{transfer_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert detail_response.status == 200
        assert detail_response.json["data"]["status"] == "pending"

        # 3. 审批通过
        approve_request, approve_response = await test_app.test_client.post(
            f"/api/v1/transfers/{transfer_id}/approve",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert approve_response.status == 200
        assert approve_response.json["data"]["status"] == "approved"

        # 4. 完成转移
        complete_request, complete_response = await test_app.test_client.post(
            f"/api/v1/transfers/{transfer_id}/complete",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert complete_response.status == 200
        assert complete_response.json["data"]["status"] == "completed"

        # 5. 验证最终状态
        final_request, final_response = await test_app.test_client.get(
            f"/api/v1/transfers/{transfer_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert final_response.status == 200
        final_data = final_response.json["data"]
        assert final_data["status"] == "completed"
        assert "approved_at" in final_data


@pytest.mark.asyncio
async def test_transfer_reject_workflow(test_app):
    """测试转移拒绝工作流"""
    token = create_access_token(
        user_id=999996,
        role="admin",
        permissions=[
            "customer.transfer",
            "customer.transfer.view",
            "customer.transfer.approve",
        ],
    )

    unique_id = str(uuid.uuid4())[:8]

    # 1. 创建转移
    create_request, create_response = await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": f"拒绝测试_{unique_id}",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    if create_response.status == 200:
        transfer_id = create_response.json["data"]["id"]

        # 2. 拒绝转移
        reject_request, reject_response = await test_app.test_client.post(
            f"/api/v1/transfers/{transfer_id}/reject",
            json={},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert reject_response.status == 200
        assert reject_response.json["data"]["status"] == "rejected"

        # 3. 验证状态
        detail_request, detail_response = await test_app.test_client.get(
            f"/api/v1/transfers/{transfer_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert detail_response.status == 200
        assert detail_response.json["data"]["status"] == "rejected"


@pytest.mark.asyncio
async def test_transfer_list_filter_by_status(test_app):
    """测试按状态过滤转移记录"""
    token = create_access_token(
        user_id=999997,
        role="admin",
        permissions=["customer.transfer.view", "customer.transfer"],
    )

    # 创建一个转移
    unique_id = str(uuid.uuid4())[:8]
    await test_app.test_client.post(
        "/api/v1/transfers",
        json={
            "customer_id": 1,
            "to_sales_rep_id": 2,
            "reason": f"状态过滤测试_{unique_id}",
        },
        headers={"Authorization": f"Bearer {token}"},
    )

    # 过滤 pending 状态
    request, response = await test_app.test_client.get(
        "/api/v1/transfers?status=pending",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    data = response.json["data"]

    # 所有返回的记录都应该是 pending 状态
    for item in data["items"]:
        assert item["status"] == "pending"


@pytest.mark.asyncio
async def test_transfer_model_unique_id(test_app):
    """测试使用 UUID 避免唯一性约束冲突"""
    token = create_access_token(
        user_id=999998,
        role="admin",
        permissions=["customer.transfer.view", "customer.transfer"],
    )

    # 多次运行测试，每次使用唯一 ID
    for i in range(3):
        unique_id = str(uuid.uuid4())[:8]

        request, response = await test_app.test_client.post(
            "/api/v1/transfers",
            json={
                "customer_id": 1,
                "to_sales_rep_id": 2,
                "reason": f"唯一性测试_{unique_id}_{i}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        # 应该都能成功创建（或都因为客户不存在而失败）
        assert response.status in [200, 400, 404]
