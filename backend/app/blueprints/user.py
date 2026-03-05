from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime
from sqlalchemy import select

from app.database import get_db_session
from app.models.user import User
from app.models.role import Role, UserRole
from app.services.user_service import UserService
from app.decorators.rbac import require_permissions


user_bp = Blueprint("user", url_prefix="/api/v1/users")


@user_bp.get("/")
@require_permissions("system.user.view")
async def list_users(request: Request):
    """用户列表 API"""
    params = request.args

    page = int(params.get("page", 1))
    size = int(params.get("size", 20))
    keyword = params.get("keyword")

    async for session in get_db_session():
        result = await UserService.list_users(
            session=session, page=page, size=size, keyword=keyword
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})


@user_bp.get("/<user_id:int>")
@require_permissions("system.user.view")
async def get_user(request: Request, user_id: int):
    """获取用户详情 API"""
    async for session in get_db_session():
        user = await UserService.get_user(session=session, user_id=user_id)

        if not user:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "用户不存在"}}, status=404
            )

        role_result = await session.execute(
            select(Role)
            .join(UserRole, Role.id == UserRole.role_id)
            .where(UserRole.user_id == user_id)
        )
        roles = role_result.scalars().all()

        user_dict = user.to_dict()
        user_dict["roles"] = [role.code for role in roles]
        user_dict["role_ids"] = [role.id for role in roles]

        return json({"data": user_dict, "timestamp": datetime.utcnow().isoformat()})


@user_bp.post("/")
@require_permissions("system.user.create")
async def create_user(request: Request):
    """创建用户 API"""
    data = request.json

    if not data.get("username"):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "用户名不能为空"}},
            status=400,
        )

    if not data.get("password"):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "密码不能为空"}},
            status=400,
        )

    if not data.get("real_name"):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "真实姓名不能为空"}},
            status=400,
        )

    async for session in get_db_session():
        existing = await UserService.get_user_by_username(
            session=session, username=data["username"]
        )
        if existing:
            return JSONResponse(
                {
                    "error": {
                        "code": "DUPLICATE_USERNAME",
                        "message": "用户名已存在",
                    }
                },
                status=400,
            )

        role_ids = data.get("role_ids")
        user = await UserService.create_user(
            session=session, data=data, role_ids=role_ids
        )

        return json(
            {"data": user.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@user_bp.put("/<user_id:int>")
@require_permissions("system.user.update")
async def update_user(request: Request, user_id: int):
    """更新用户 API"""
    data = request.json

    async for session in get_db_session():
        user = await UserService.get_user(session=session, user_id=user_id)

        if not user:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "用户不存在"}}, status=404
            )

        role_ids = data.get("role_ids")
        updated_user = await UserService.update_user(
            session=session, user_id=user_id, data=data, role_ids=role_ids
        )

        return json(
            {"data": updated_user.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@user_bp.delete("/<user_id:int>")
@require_permissions("system.user.delete")
async def delete_user(request: Request, user_id: int):
    """删除用户 API"""
    async for session in get_db_session():
        user = await UserService.get_user(session=session, user_id=user_id)

        if not user:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "用户不存在"}}, status=404
            )

        success = await UserService.delete_user(session=session, user_id=user_id)

        if not success:
            return JSONResponse(
                {"error": {"code": "ERROR", "message": "删除失败"}}, status=500
            )

        return json(
            {
                "data": {"message": "用户删除成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@user_bp.post("/<user_id:int>/password")
@require_permissions("system.user.update")
async def update_password(request: Request, user_id: int):
    """更新用户密码 API"""
    data = request.json

    if not data.get("new_password"):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "新密码不能为空"}},
            status=400,
        )

    async for session in get_db_session():
        success = await UserService.update_password(
            session=session, user_id=user_id, new_password=data["new_password"]
        )

        if not success:
            return JSONResponse(
                {"error": {"code": "ERROR", "message": "更新密码失败"}}, status=500
            )

        return json(
            {
                "data": {"message": "密码更新成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
