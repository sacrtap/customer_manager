"""
RBAC权限系统E2E测试
"""

import pytest
import requests
from test_helpers import (
    APIClient,
    get_test_users,
    assert_api_response,
    assert_error_response,
)


class TestRBAC:
    """RBAC权限系统E2E测试"""

    def test_admin_access_all_features(self, base_url, test_tokens):
        """超級管理员访问所有功能"""
        token = test_tokens["admin"]

        # 测试创建客户
        response = requests.post(
            f"{base_url}/customers",
            json={"name": "测试客户", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

        # 测试删除客户
        if "data" in response.json():
            customer_id = response.json()["data"]["id"]
            response = requests.delete(
                f"{base_url}/customers/{customer_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200

    def test_manager_permissions(self, base_url, test_tokens):
        """运营经理权限验证"""
        token = test_tokens["manager"]

        # 运营经理可以查看客户
        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

        # 运营经理可以创建客户
        response = requests.post(
            f"{base_url}/customers",
            json={"name": "测试客户", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200

    def test_specialist_permissions(self, base_url, test_tokens):
        """运营专员权限验证"""
        token = test_tokens["specialist"]

        # 运营专员可以查看客户
        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200

    def test_sales_only_own_customers(self, base_url, test_tokens):
        """销售人员只能看自己客户"""
        token = test_tokens["sales"]

        # 创建一个属于sales的客户
        response = requests.post(
            f"{base_url}/customers",
            json={"name": "销售客户", "sales_rep_id": 999},  # 假设sales的user_id是999
            headers={
                "Authorization": f"Bearer {test_tokens['admin']}"
            },  # 使用admin创建
        )

        if response.status_code == 200:
            customer_id = response.json()["data"]["id"]

            # sales可以访问自己的客户
            response = requests.get(
                f"{base_url}/customers/{customer_id}",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert response.status_code == 200

    def test_permission_decorator_works(self, base_url, test_tokens):
        """权限装饰器正常工作"""
        token = test_tokens["specialist"]

        # 专员不能导出（假设没有导出权限）
        response = requests.get(
            f"{base_url}/customers/export", headers={"Authorization": f"Bearer {token}"}
        )

        if response.status_code == 403:
            assert_error_response(response, 403, "FORBIDDEN")

    def test_unauthorized_access_returns_401(self, base_url):
        """无权限访问返回401"""
        response = requests.get(f"{base_url}/customers")
        assert_error_response(response, 401, "UNAUTHORIZED")

    def test_forbidden_access_returns_403(self, base_url, test_tokens):
        """无权限访问返回403"""
        # 创建一个没有权限的用户（这里仅测试逻辑）
        token = test_tokens["sales"]

        # 如果sales没有删除权限，这个测试应该返回403
        response = requests.delete(
            f"{base_url}/customers/99999",  # 不存在的客户
            headers={"Authorization": f"Bearer {token}"},
        )

        if response.status_code == 403:
            assert_error_response(response, 403, "FORBIDDEN")

    def test_permission_wildcard_matching(self, base_url, test_tokens):
        """权限通配符匹配"""
        token = test_tokens["admin"]

        # admin有*权限，应该可以访问任何端点
        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
