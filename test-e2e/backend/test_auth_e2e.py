"""
后端E2E测试 - 认证系统
"""

import pytest
import requests
import json
import uuid


@pytest.fixture(scope="session")
def base_url():
    """基础URL"""
    return "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def test_users():
    """测试用户数据"""
    return [
        {
            "username": "admin",
            "password": "admin123",
            "real_name": "系统管理员",
            "email": "admin@example.com",
            "phone": "13800000001",
            "role": "admin",
            "status": "active",
        },
        {
            "username": "manager",
            "password": "manager123",
            "real_name": "运营经理",
            "email": "manager@example.com",
            "phone": "13800000002",
            "role": "manager",
            "status": "active",
        },
        {
            "username": "specialist",
            "password": "specialist123",
            "real_name": "运营专员",
            "email": "specialist@example.com",
            "phone": "13800000003",
            "role": "specialist",
            "status": "active",
        },
        {
            "username": "sales",
            "password": "sales123",
            "real_name": "销售人员",
            "email": "sales@example.com",
            "phone": "13800000004",
            "role": "sales",
            "status": "active",
        },
    ]


@pytest.fixture(scope="session")
def test_tokens(base_url):
    """预创建测试用户的Token"""
    tokens = {}

    for user in test_users():
        response = requests.post(
            f"{base_url}/auth/login",
            json={"username": user["username"], "password": user["password"]},
        )

        if response.status_code == 200:
            data = response.json()
            tokens[user["username"]] = data["data"]["token"]
        else:
            print(f"Failed to create token for {user['username']}: {response.text}")

    return tokens


class TestAuthentication:
    """认证系统E2E测试"""

    def test_login_with_valid_credentials(self, base_url, test_users):
        """使用有效用户名和密码登录"""
        admin_user = test_users[0]

        response = requests.post(
            f"{base_url}/auth/login",
            json={
                "username": admin_user["username"],
                "password": admin_user["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()["data"]
        assert "token" in data
        assert "user" in data
        assert "permissions" in data
        assert data["user"]["username"] == admin_user["username"]
        assert data["user"]["role"] == admin_user["role"]

    def test_login_with_invalid_username(self, base_url):
        """使用无效用户名登录"""
        response = requests.post(
            f"{base_url}/auth/login",
            json={"username": "nonexistent_user", "password": "wrongpass"},
        )

        assert response.status_code == 401
        error_data = response.json()["error"]
        assert error_data["code"] == "UNAUTHORIZED"

    def test_login_with_invalid_password(self, base_url, test_users):
        """使用无效密码登录"""
        admin_user = test_users[0]

        response = requests.post(
            f"{base_url}/auth/login",
            json={"username": admin_user["username"], "password": "wrongpassword"},
        )

        assert response.status_code == 401
        error_data = response.json()["error"]
        assert error_data["code"] == "UNAUTHORIZED"

    def test_token_generation_and_validation(self, base_url, test_tokens):
        """Token生成和验证"""
        token = test_tokens["admin"]

        assert isinstance(token, str)
        assert len(token) > 0

        # 验证Token可以访问受保护端点
        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

    def test_logout(self, base_url, test_tokens):
        """登出功能"""
        token = test_tokens["admin"]

        response = requests.post(
            f"{base_url}/auth/logout", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

        # 验证Token失效
        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 401

    def test_protected_endpoint_without_token(self, base_url):
        """访问受保护端点但没有Token"""
        response = requests.get(f"{base_url}/customers")

        assert response.status_code == 401
        error_data = response.json()["error"]
        assert error_data["code"] == "UNAUTHORIZED"

    def test_expired_token_handling(self, base_url):
        """Token过期处理（使用无效Token）"""
        invalid_token = "invalid.token.string"

        response = requests.get(
            f"{base_url}/customers",
            headers={"Authorization": f"Bearer {invalid_token}"},
        )

        assert response.status_code == 401
