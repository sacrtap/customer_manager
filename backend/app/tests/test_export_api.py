# backend/app/tests/test_export_api.py
import pytest
from sanic import Sanic
from app.blueprints.customer import customer_bp
from app.middlewares.auth import attach_auth_middleware


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    app.blueprint(customer_bp)
    return app


def test_export_without_token(app):
    """测试导出无 Token"""
    request, response = app.test_client.get("/api/v1/customers/export")
    assert response.status == 401


def test_export_with_token(app):
    """测试导出有效 Token"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["*"])

    request, response = app.test_client.get(
        "/api/v1/customers/export",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert response.headers.get("Content-Type").startswith(
        "application/vnd.openxmlformats"
    )
