import pytest

from app.utils.password import hash_password, verify_password


def test_hash_password():
    """测试密码哈希"""
    password = "test123"
    hashed = hash_password(password)

    assert hashed != password
    assert len(hashed) > 50
    assert hashed.startswith("$2b$")


def test_verify_password_correct():
    """测试验证正确密码"""
    password = "test123"
    hashed = hash_password(password)

    assert verify_password(password, hashed) is True


def test_verify_password_incorrect():
    """测试验证错误密码"""
    password = "test123"
    hashed = hash_password(password)
    wrong_password = "wrong123"

    assert verify_password(wrong_password, hashed) is False
