def has_permission(user_permissions: list, required_permission: str) -> bool:
    """检查用户是否拥有所需权限"""
    if "*" in user_permissions:
        return True

    if required_permission in user_permissions:
        return True

    for perm in user_permissions:
        if ".*" in perm:
            parts = perm.split(".*")
            if len(parts) == 2:
                prefix = parts[0]
                if required_permission.startswith(prefix):
                    return True

    return False


def check_rbac(
    user_role: str, user_permissions: list, required_permissions: list
) -> bool:
    """检查 RBAC 权限"""
    if user_role == "admin":
        return True

    for required in required_permissions:
        if not has_permission(user_permissions, required):
            return False

    return True
