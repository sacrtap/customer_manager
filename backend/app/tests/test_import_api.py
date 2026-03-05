# backend/app/tests/test_import_api.py
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


def test_download_template_without_token(app):
    """测试下载模板无 Token"""
    request, response = app.test_client.get("/api/v1/customers/import-template")
    assert response.status == 401


def test_download_template_with_token(app):
    """测试下载模板有效 Token"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["*"])

    request, response = app.test_client.get(
        "/api/v1/customers/import-template",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 200
    assert response.headers.get("Content-Type").startswith(
        "application/vnd.openxmlformats"
    )


def test_import_customers_no_file(app):
    """测试导入无文件"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["*"])

    request, response = app.test_client.post(
        "/api/v1/customers/import",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status == 400
    assert response.json.get("error").get("code") == "NO_FILE"
