import pytest
from sanic import Request, Sanic
from sanic.response import json

from app.middlewares.auth import attach_auth_middleware, require_auth_middleware
from app.utils.jwt import create_access_token


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    require_auth_middleware(app)

    @app.get("/protected")
    async def protected(request):
        return json({"user": request.ctx.user})

    @app.get("/public")
    async def public(request):
        return json({"message": "public"})

    return app


def test_public_endpoint_without_token(app):
    """测试公开端点不需要 Token"""
    request, response = app.test_client.get("/public")
    assert response.status == 200
    assert response.json["message"] == "public"


def test_protected_endpoint_without_token(app):
    """测试受保护端点需要 Token"""
    request, response = app.test_client.get("/protected")
    assert response.status == 401


def test_protected_endpoint_with_valid_token(app):
    """测试受保护端点有效 Token"""
    token = create_access_token(123, "admin", ["*"])

    request, response = app.test_client.get(
        "/protected", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status == 200
    assert response.json["user"]["user_id"] == 123
