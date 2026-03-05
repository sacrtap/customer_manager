import pytest

from app.utils.jwt import create_access_token, decode_token


def test_create_and_decode_token():
    """测试创建和解码 Token"""
    user_id = 123
    role = "admin"
    permissions = ["*"]

    token = create_access_token(user_id, role, permissions)
    assert isinstance(token, str)
    assert len(token) > 0

    payload = decode_token(token)
    assert payload is not None
    assert payload["user_id"] == user_id
    assert payload["role"] == role
    assert payload["permissions"] == permissions


def test_decode_invalid_token():
    """测试解码无效 Token"""
    invalid_token = "invalid.token.string"
    payload = decode_token(invalid_token)
    assert payload is None
