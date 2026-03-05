import pytest
from sanic import Sanic
from sanic.response import json

from app.decorators.rbac import require_permissions


def test_require_permissions_with_valid_permission():
    """测试有效权限"""
    app = Sanic("test_app")

    @app.get("/customer/list")
    @require_permissions("customer.view")
    async def list_customers(request):
        return json({"data": []})

    @app.middleware("request")
    async def mock_auth(request):
        request.ctx.user = {
            "user_id": 1,
            "role": "user",
            "permissions": ["customer.view"],
        }

    request, response = app.test_client.get("/customer/list")
    assert response.status == 200


def test_require_permissions_without_permission():
    """测试无权限"""
    app = Sanic("test_app")

    @app.get("/customer/list")
    @require_permissions("customer.view")
    async def list_customers(request):
        return json({"data": []})

    @app.middleware("request")
    async def mock_auth(request):
        request.ctx.user = {"user_id": 1, "role": "user", "permissions": []}

    request, response = app.test_client.get("/customer/list")
    assert response.status == 403
