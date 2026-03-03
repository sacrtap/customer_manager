import pytest
import requests
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture(scope="session")
def base_url():
    """基础URL"""
    return "http://localhost:8000/api/v1"


@pytest.fixture(scope="session")
def test_data():
    """测试数据"""
    import test_helpers

    return {
        "users": test_helpers.get_test_users(),
        "customers": test_helpers.get_test_customers(),
    }


@pytest.fixture(scope="session")
def test_tokens():
    """预创建测试用户的Token"""
    import test_helpers

    tokens = {}

    for user in test_helpers.get_test_users():
        response = requests.post(
            f"http://localhost:8000/api/v1/auth/login",
            json={"username": user["username"], "password": user["password"]},
        )

        if response.status_code == 200:
            data = response.json()
            tokens[user["username"]] = data["data"]["token"]
        else:
            print(f"Failed to create token for {user['username']}: {response.text}")

    return tokens


@pytest.fixture(scope="session")
def api_client():
    """创建API客户端fixture"""
    import test_helpers

    return test_helpers.APIClient()
