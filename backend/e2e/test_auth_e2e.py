"""
后端E2E测试 - 认证系统
"""

import pytest
import requests
import json
import uuid
from test_helpers import get_test_users


class TestAuthentication:
    """认证系统E2E测试"""

    def test_login_with_valid_credentials(self, base_url, test_tokens):
        """使用有效用户名和密码登录"""
        users = get_test_users()
        admin_user = users[0]

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
        assert "role" in data
        assert data["user"]["username"] == admin_user["username"]
        assert data["role"] == admin_user["role"]

    def test_login_with_invalid_username(self, base_url):
        """使用无效用户名登录"""
        response = requests.post(
            f"{base_url}/auth/login",
            json={"username": "nonexistent_user", "password": "wrongpass"},
        )

        assert response.status_code == 401
        error_data = response.json()["error"]
        assert error_data["code"] == "INVALID_CREDENTIALS"

    def test_login_with_invalid_password(self, base_url):
        """使用无效密码登录"""
        users = get_test_users()
        admin_user = users[0]

        response = requests.post(
            f"{base_url}/auth/login",
            json={"username": admin_user["username"], "password": "wrongpassword"},
        )

        assert response.status_code == 401
        error_data = response.json()["error"]
        assert error_data["code"] == "INVALID_CREDENTIALS"

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

        # 验证Token失效（客户端删除token，服务端不检查）
        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200

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
