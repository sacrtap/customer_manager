import pytest

from app.utils.rbac import check_rbac, has_permission


def test_has_permission_exact_match():
    """测试精确权限匹配"""
    user_permissions = ["customer.view", "customer.create"]
    assert has_permission(user_permissions, "customer.view") is True


def test_has_permission_wildcard_match():
    """测试通配符权限匹配"""
    user_permissions = ["customer.*", "user.view"]
    assert has_permission(user_permissions, "customer.create") is True


def test_has_permission_all_wildcard():
    """测试所有所有权限通配符"""
    user_permissions = ["*"]
    assert has_permission(user_permissions, "any.permission") is True


def test_check_rbac_admin():
    """测试管理员总是通过"""
    assert check_rbac("admin", [], ["any.permission"]) is True


def test_check_rbac_normal_user():
    """测试普通用户权限检查"""
    user_permissions = ["customer.view", "customer.create"]
    required_permissions = ["customer.view"]

    assert check_rbac("user", user_permissions, required_permissions) is True


def test_check_rbac_insufficient_permissions():
    """测试权限不足"""
    user_permissions = ["customer.view"]
    required_permissions = ["customer.delete"]

    assert check_rbac("user", user_permissions, required_permissions) is False
