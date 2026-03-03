import pytest
from sanic import Sanic
from app.blueprints.customer import customer_bp
from app.middlewares.auth import attach_auth_middleware
from app.decorators.rbac import require_permissions


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    app.blueprint(customer_bp)

    @app.get("/protected")
    @require_permissions("customer.view")
    async def protected(request):
        from app.utils.jwt import create_access_token

        return {"user": request.ctx.user}

    return app


def test_list_customers_without_token(app):
    """测试列表 API 无 Token"""
    request, response = app.test_client.get("/api/v1/customers")
    assert response.status == 401


def test_list_customers_with_token(app):
    """测试列表 API 有效 Token"""
    from app.utils.jwt import create_access_token

    token = create_access_token(1, "admin", ["*"])

    request, response = app.test_client.get(
        "/api/v1/customers", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status == 200
    assert "data" in response.json
