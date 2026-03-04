from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime
from sqlalchemy import select

from app.database import get_db_session
from app.models.role import Role
from app.services.role_service import RoleService


role_bp = Blueprint("role", url_prefix="/api/v1/roles")


@role_bp.get("/")
async def list_roles(request: Request):
    """角色列表 API"""
    params = request.args

    page = int(params.get("page", 1))
    size = int(params.get("size", 20))
    keyword = params.get("keyword")

    async for session in get_db_session():
        result = await RoleService.list_roles(
            session=session, page=page, size=size, keyword=keyword
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})


@role_bp.get("/<role_id:int>")
async def get_role(request: Request, role_id: int):
    """获取角色详情 API"""
    async for session in get_db_session():
        role = await RoleService.get_role(session=session, role_id=role_id)

        if not role:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "角色不存在"}}, status=404
            )

        return json(
            {"data": role.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@role_bp.post("/")
async def create_role(request: Request):
    """创建角色 API"""
    data = request.json

    # 验证必填字段
    if not data.get("name"):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "角色名称不能为空"}},
            status=400,
        )

    if not data.get("code"):
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": "角色编码不能为空"}},
            status=400,
        )

    async for session in get_db_session():
        # 检查编码是否已存在
        existing_role = await RoleService.get_role_by_code(
            session=session, code=data["code"]
        )
        if existing_role:
            return JSONResponse(
                {
                    "error": {
                        "code": "DUPLICATE_CODE",
                        "message": "角色编码已存在",
                    }
                },
                status=400,
            )

        # 创建角色
        role = await RoleService.create_role(session=session, data=data)

        return json(
            {"data": role.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@role_bp.put("/<role_id:int>")
async def update_role(request: Request, role_id: int):
    """更新角色 API"""
    data = request.json

    async for session in get_db_session():
        # 检查角色是否存在
        role = await RoleService.get_role(session=session, role_id=role_id)

        if not role:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "角色不存在"}}, status=404
            )

        # 系统角色不允许修改
        if role.is_system:
            return JSONResponse(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "系统角色不允许修改",
                    }
                },
                status=403,
            )

        # 更新角色
        updated_role = await RoleService.update_role(
            session=session, role_id=role_id, data=data
        )

        return json(
            {"data": updated_role.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@role_bp.delete("/<role_id:int>")
async def delete_role(request: Request, role_id: int):
    """删除角色 API"""
    async for session in get_db_session():
        # 检查角色是否存在
        role = await RoleService.get_role(session=session, role_id=role_id)

        if not role:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "角色不存在"}}, status=404
            )

        # 系统角色不允许删除
        if role.is_system:
            return JSONResponse(
                {
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "系统角色不允许删除",
                    }
                },
                status=403,
            )

        # 删除角色
        success = await RoleService.delete_role(session=session, role_id=role_id)

        if not success:
            return JSONResponse(
                {"error": {"code": "ERROR", "message": "删除失败"}}, status=500
            )

        return json(
            {
                "data": {"message": "角色删除成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
