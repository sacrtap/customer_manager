"""
测试辅助工具模块
"""

import json
import uuid
import pytest
from typing import Dict, Any
from pathlib import Path


def load_fixture(fixture_name: str) -> Dict[str, Any]:
    """加载测试fixture数据"""
    fixture_path = Path(__file__).parent.parent / "fixtures" / fixture_name

    if not fixture_path.exists():
        raise FileNotFoundError(f"Fixture file not found: {fixture_path}")

    with open(fixture_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_test_users() -> list:
    """获取测试用户列表"""
    data = load_fixture("users.json")
    return data["test_users"]


def get_test_customers() -> list:
    """获取测试客户列表"""
    data = load_fixture("customers.json")
    return data["test_customers"]


def generate_unique_customer_name(base_name: str = "测试客户") -> str:
    """生成唯一的客户名称"""
    suffix = uuid.uuid4().hex[:6]
    return f"{base_name}_{suffix}"


def generate_unique_customer_code(base_code: str = "CUST") -> str:
    """生成唯一的客户编码"""
    suffix = uuid.uuid4().hex[:6].upper()
    return f"{base_code}{suffix}"


def assert_api_response(response, expected_status: int = 200, check_data: bool = True):
    """断言API响应"""
    assert response.status == expected_status, (
        f"Expected status {expected_status}, got {response.status}"
    )

    if check_data:
        assert "data" in response.json or "error" not in response.json, (
            f"Response should contain 'data' or 'error'"
        )


def assert_error_response(response, expected_code: str, expected_message: str = None):
    """断言错误响应"""
    assert response.status >= 400, (
        f"Expected error status >= 400, got {response.status}"
    )

    response_json = response.json if hasattr(response, "json") else response.body
    assert "error" in response_json, "Response should contain 'error'"

    if expected_code:
        assert response_json["error"]["code"] == expected_code, (
            f"Expected error code {expected_code}, got {response_json['error']['code']}"
        )

    if expected_message:
        assert expected_message in response_json["error"]["message"], (
            f"Expected message to contain '{expected_message}'"
        )


def get_auth_headers(token: str) -> Dict[str, str]:
    """获取认证头"""
    return {"Authorization": f"Bearer {token}"}


def parse_pagination_info(response_data: dict) -> dict:
    """解析分页信息"""
    return {
        "items": response_data.get("items", []),
        "total": response_data.get("total", 0),
        "page": response_data.get("page", 1),
        "size": response_data.get("size", 10),
        "pages": response_data.get("pages", 0),
    }


class APIClient:
    """API客户端包装类"""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1"):
        self.base_url = base_url
        self.token = None

    def set_token(self, token: str):
        """设置认证Token"""
        self.token = token

    def get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        return headers

    def login(self, username: str, password: str) -> dict:
        """登录"""
        import requests

        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"username": username, "password": password},
            headers={"Content-Type": "application/json"},
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("data", {}).get("token")
            return {"success": True, "data": data}
        else:
            return {"success": False, "error": response.json()}

    def logout(self) -> dict:
        """登出"""
        import requests

        response = requests.post(
            f"{self.base_url}/auth/logout", headers=self.get_headers()
        )

        self.token = None
        return {"success": response.status_code == 200}

    def get_customers(self, params: dict = None) -> dict:
        """获取客户列表"""
        import requests

        response = requests.get(
            f"{self.base_url}/customers",
            params=params or {},
            headers=self.get_headers(),
        )

        return {
            "success": response.status_code == 200,
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
        }

    def create_customer(self, customer_data: dict) -> dict:
        """创建客户"""
        import requests

        response = requests.post(
            f"{self.base_url}/customers", json=customer_data, headers=self.get_headers()
        )

        return {
            "success": response.status_code == 200,
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
        }

    def get_customer(self, customer_id: int) -> dict:
        """获取客户详情"""
        import requests

        response = requests.get(
            f"{self.base_url}/customers/{customer_id}", headers=self.get_headers()
        )

        return {
            "success": response.status_code == 200,
            "status": response.status_code,
            "data": response.json.json() if response.status_code == 200 else None,
        }

    def update_customer(self, customer_id: int, customer_data: dict) -> dict:
        """更新客户"""
        import requests

        response = requests.put(
            f"{self.base_url}/customers/{customer_id}",
            json=customer_data,
            headers=self.get_headers(),
        )

        return {
            "success": response.status_code == 200,
            "status": response.status_code,
            "data": response.json() if response.status_code == 200 else None,
        }

    def delete_customer(self, customer_id: int) -> dict:
        """删除客户"""
        import requests

        response = requests.delete(
            f"{self.base_url}/customers/{customer_id}", headers=self.get_headers()
        )

        return {"success": response.status_code == 200, "status": response.status_code}

    def download_import_template(self) -> dict:
        """下载导入模板"""
        import requests

        response = requests.get(
            f"{self.base_url}/customers/import-template", headers=self.get_headers()
        )

        return {
            "success": response.status_code == 200,
            "status": response.status_code,
            "content": response.content if response.status_code == 200 else None,
        }

    def export_customers(self, params: dict = None) -> dict:
        """导出客户数据"""
        import requests

        response = requests.get(
            f"{self.base_url}/customers/export",
            params=params or {},
            headers=self.get_headers(),
        )

        return {
            "success": response.status_code == 200,
            "status": response.status_code,
            "content": response.content if response.status_code == 200 else None,
        }


@pytest.fixture
def api_client():
    """创建API客户端fixture"""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client):
    """创建已认证的客户端fixture"""
    users = get_test_users()
    admin_user = users[0]  # admin

    result = api_client.login(admin_user["username"], admin_user["password"])

    if not result["success"]:
        pytest.fail(f"Failed to login as admin: {result.get('error')}")

    return api_client
