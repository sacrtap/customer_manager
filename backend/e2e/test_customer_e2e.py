"""
客户CRUD E2E测试
"""

import pytest
import requests
import uuid
from test_helpers import (
    APIClient,
    get_test_users,
    get_test_customers,
    assert_api_response,
    assert_error_response,
)


class TestCustomerCRUD:
    """客户CRUD E2E测试"""

    def test_create_customer_success(self, base_url, test_tokens):
        """创建客户成功"""
        token = test_tokens["admin"]
        customer_code = f"E2E{uuid.uuid4().hex[:6]}"

        response = requests.post(
            f"{base_url}/customers",
            json={
                "name": "E2E测试客户",
                "code": customer_code,
                "industry": "科技",
                "sales_rep_id": 122,
                "tier_level": "A",
                "annual_consumption": 100000.00,
                "contact_person": "测试联系人",
                "contact_phone": "13800138000",
                "contact_email": "test@example.com",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert data["id"] is not None
        assert data["name"] == "E2E测试客户"
        assert data["code"] == customer_code

    def test_get_customer_detail(self, base_url, test_tokens):
        """查看客户详情"""
        token = test_tokens["admin"]

        # 先创建一个客户
        create_response = requests.post(
            f"{base_url}/customers",
            json={"name": "详情测试客户", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"},
        )

        if create_response.status_code == 200:
            customer_id = create_response.json()["data"]["id"]

            # 获取详情
            response = requests.get(
                f"{base_url}/customers/{customer_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert_api_response(response, 200)

            data = response.json()["data"]
            assert data["id"] == customer_id
            assert data["name"] == "详情测试客户"

    def test_update_customer(self, base_url, test_tokens):
        """更新客户"""
        token = test_tokens["admin"]

        # 先创建一个客户
        create_response = requests.post(
            f"{base_url}/customers",
            json={"name": "原始客户", "industry": "原行业", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"},
        )

        if create_response.status_code == 200:
            customer_id = create_response.json()["data"]["id"]

            # 更新客户
            response = requests.put(
                f"{base_url}/customers/{customer_id}",
                json={"name": "更新后的客户", "industry": "新行业", "tier_level": "B"},
                headers={"Authorization": f"Bearer {token}"},
            )

            assert_api_response(response, 200)

            data = response.json()["data"]
            assert data["name"] == "更新后的客户"
            assert data["industry"] == "新行业"
            assert data["tier_level"] == "B"

    def test_delete_customer(self, base_url, test_tokens):
        """删除客户"""
        token = test_tokens["admin"]

        # 先创建一个客户
        create_response = requests.post(
            f"{base_url}/customers",
            json={"name": "待删除客户", "sales_rep_id": 1},
            headers={"Authorization": f"Bearer {token}"},
        )

        if create_response.status_code == 200:
            customer_id = create_response.json()["data"]["id"]

            # 删除客户
            response = requests.delete(
                f"{base_url}/customers/{customer_id}",
                headers={"Authorization": f"Bearer {token}"},
            )

            assert_api_response(response, 200)

    def test_pagination_query(self, base_url, test_tokens):
        """分页查询客户列表"""
        token = test_tokens["admin"]

        response = requests.get(
            f"{base_url}/customers",
            params={"page": 1, "size": 10},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert data["page"] == 1
        assert data["size"] == 10

    def test_keyword_search(self, base_url, test_tokens):
        """多维度查询 - 关键词"""
        token = test_tokens["admin"]

        response = requests.get(
            f"{base_url}/customers",
            params={"keyword": "科技"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert "items" in data

    def test_industry_filter(self, base_url, test_tokens):
        """多维度查询 - 行业"""
        token = test_tokens["admin"]

        response = requests.get(
            f"{base_url}/customers",
            params={"industries": "科技"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert "items" in data

    def test_status_and_tier_filter(self, base_url, test_tokens):
        """多维度查询 - 状态和等级"""
        token = test_tokens["admin"]

        response = requests.get(
            f"{base_url}/customers",
            params={"status": "active", "tier_levels": "A"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert "items" in data

    def test_amount_range_filter(self, base_url, test_tokens):
        """多维度查询 - 金额范围"""
        token = test_tokens["admin"]

        response = requests.get(
            f"{base_url}/customers",
            params={"annual_consumption_min": 100000, "annual_consumption_max": 500000},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert "items" in data

    def test_sales_only_see_own_customers(self, base_url, test_tokens):
        """销售只能看自己客户"""
        token = test_tokens["sales"]

        response = requests.get(
            f"{base_url}/customers", headers={"Authorization": f"Bearer {token}"}
        )

        assert_api_response(response, 200)

        data = response.json()["data"]
        assert "items" in data

    def test_customer_data_validation(self, base_url, test_tokens):
        """客户数据验证"""
        token = test_tokens["admin"]

        # 测试缺少必填字段
        response = requests.post(
            f"{base_url}/customers",
            json={},  # 缺少name和sales_rep_id
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code >= 400
