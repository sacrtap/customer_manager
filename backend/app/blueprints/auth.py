from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime
from sqlalchemy import select

from app.database import get_db_session
from app.models.user import User
from app.models.role import Role, UserRole
from app.utils.password import verify_password
from app.utils.jwt import create_access_token
from app.schemas.auth import LoginRequest


auth_bp = Blueprint("auth", url_prefix="/api/v1/auth")


@auth_bp.post("/login")
async def login(request: Request):
    """用户登录 API"""
    try:
        data = LoginRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    async for session in get_db_session():
        # 查找用户
        user = (
            await session.execute(select(User).where(User.username == data.username))
        ).scalar_one_or_none()

        if not user:
            return JSONResponse(
                {
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "用户名或密码错误",
                    }
                },
                status=401,
            )

        # 验证密码
        if not verify_password(data.password, user.password_hash):
            return JSONResponse(
                {
                    "error": {
                        "code": "INVALID_CREDENTIALS",
                        "message": "用户名或密码错误",
                    }
                },
                status=401,
            )

        # 检查用户状态
        if user.status != "active":
            return JSONResponse(
                {"error": {"code": "USER_INACTIVE", "message": "用户账号已被禁用"}},
                status=403,
            )

        # 获取用户角色和权限
        role_result = (
            (
                await session.execute(
                    select(Role)
                    .join(UserRole, Role.id == UserRole.role_id)
                    .where(UserRole.user_id == user.id)
                )
            )
            .scalars()
            .all()
        )

        permissions = set()
        role_names = []
        for role in role_result:
            role_names.append(role.code)
            if role.permissions:
                # 兼容 list 和 dict 格式
                if isinstance(role.permissions, list):
                    permissions.update(role.permissions)
                elif isinstance(role.permissions, dict):
                    permissions.update(role.permissions.keys())

        # 创建 Token
        token = create_access_token(
            user_id=user.id,
            role=role_names[0] if role_names else "user",
            permissions=list(permissions),
        )

        return json(
            {
                "data": {
                    "token": token,
                    "user": user.to_dict(),
                    "permissions": list(permissions),
                    "role": role_names[0] if role_names else "user",
                },
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@auth_bp.post("/logout")
async def logout(request: Request):
    """用户登出 API"""
    # 客户端删除 token 即可，服务端无需额外操作
    return json(
        {"data": {"message": "登出成功"}, "timestamp": datetime.utcnow().isoformat()}
    )


@auth_bp.get("/me")
async def get_current_user(request: Request):
    """获取当前用户信息 API"""
    user_id = request.ctx.user.get("user_id") if request.ctx.user else None

    if not user_id:
        return JSONResponse(
            {"error": {"code": "UNAUTHORIZED", "message": "未授权访问"}}, status=401
        )

    async for session in get_db_session():
        user = (
            await session.execute(select(User).where(User.id == user_id))
        ).scalar_one_or_none()

        if not user:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "用户不存在"}}, status=404
            )

        return json(
            {
                "data": user.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@auth_bp.post("/refresh")
async def refresh_token(request: Request):
    """刷新 Token API"""
    # 获取当前用户信息
    user_id = request.ctx.user.get("user_id") if request.ctx.user else None
    role = request.ctx.user.get("role") if request.ctx.user else None
    permissions = request.ctx.user.get("permissions") if request.ctx.user else []

    if not user_id:
        return JSONResponse(
            {"error": {"code": "UNAUTHORIZED", "message": "未授权访问"}}, status=401
        )

    # 创建新 Token
    new_token = create_access_token(
        user_id=user_id,
        role=role or "user",
        permissions=permissions or [],
    )

    return json(
        {
            "data": {"token": new_token},
            "timestamp": datetime.utcnow().isoformat(),
        }
    )
