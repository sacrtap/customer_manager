import pytest
from pydantic import ValidationError

from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreateRequest


def test_login_request_valid():
    """测试有效的登录请求"""
    data = {"username": "testuser", "password": "test123"}
    request = LoginRequest(**data)
    assert request.username == "testuser"


def test_login_request_invalid_password():
    """测试无效密码"""
    data = {"username": "testuser", "password": "123"}
    with pytest.raises(ValidationError):
        LoginRequest(**data)


def test_user_create_request_valid():
    """测试有效的创建用户请求"""
    data = {"username": "newuser", "password": "newpass123", "real_name": "新用户"}
    request = UserCreateRequest(**data)
    assert request.username == "newuser"
