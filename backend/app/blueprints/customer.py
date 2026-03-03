from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from datetime import datetime

from app.database import get_db_session
from app.services.customer_service import CustomerService
from app.decorators.rbac import require_permissions
from app.schemas.customer import CustomerCreateRequest, CustomerUpdateRequest


customer_bp = Blueprint("customer", url_prefix="/api/v1/customers")


@customer_bp.get("/")
@require_permissions("customer.view")
async def list_customers(request: Request):
    """客户列表 API"""
    # 解析查询参数
    params = request.args

    # 构建过滤条件
    filters = {}
    if params.get("keyword"):
        filters["keyword"] = params["keyword"]
    if params.get("sales_rep_ids"):
        filters["sales_rep_ids"] = params["sales_rep_ids"].split(",")
    if params.get("industries"):
        filters["industries"] = params["industries"].split(",")
    if params.get("status"):
        filters["status"] = params["status"].split(",")
    if params.get("tier_levels"):
        filters["tier_levels"] = params["tier_levels"].split(",")
    if params.get("annual_consumption_min"):
        filters["annual_consumption_min"] = float(params["annual_consumption_min"])
    if params.get("annual_consumption_max"):
        filters["annual_consumption_max"] = float(params["annual_consumption_max"])
    if params.get("created_at_start"):
        filters["created_at_start"] = datetime.fromisoformat(params["created_at_start"])
    if params.get("created_at_end"):
        filters["created_at_end"] = datetime.fromisoformat(params["created_at_end"])

    # 销售只能看自己客户
    user = request.ctx.user
    if user["role"] == "sales":
        filters["sales_rep_ids"] = [str(user["user_id"])]

    # 排序
    order_by = []
    if params.get("sort_field"):
        direction = "desc" if params.get("sort_desc", "false") == "true" else "asc"
        order_by.append(f"{params['sort_field']} {direction}")
    else:
        order_by.append("created_at desc")

    # 分页
    page = int(params.get("page", 1))
    size = int(params.get("size", 10))

    # 查询
    async for session in get_db_session():
        result = await CustomerService.list_customers(
            session=session, filters=filters, page=page, size=size, order_by=order_by
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})


@customer_bp.post("/")
@require_permissions("customer.create")
async def create_customer(request: Request):
    """创建客户 API"""
    try:
        data = CustomerCreateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        # 创建客户
        customer = await CustomerService.create_customer(
            session=session, data=data.model_dump(), created_by=user["user_id"]
        )

        return json(
            {"data": customer.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@customer_bp.get("/<customer_id:int>")
@require_permissions("customer.view")
async def get_customer(request: Request, customer_id: int):
    """获取客户详情 API"""
    user = request.ctx.user

    async for session in get_db_session():
        customer = await CustomerService.get_customer(
            session=session,
            customer_id=customer_id,
            user_id=user["user_id"],
            user_role=user["role"],
        )

        if not customer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "客户不存在"}}, status=404
            )

        return json(
            {"data": customer.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@customer_bp.put("/<customer_id:int>")
@require_permissions("customer.update")
async def update_customer(request: Request, customer_id: int):
    """更新客户 API"""
    try:
        data = CustomerUpdateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        customer = await CustomerService.update_customer(
            session=session,
            customer_id=customer_id,
            data=data.model_dump(exclude_unset=True),
            user_id=user["user_id"],
            user_role=user["role"],
        )

        if not customer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "客户不存在"}}, status=404
            )

        return json(
            {"data": customer.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@customer_bp.delete("/<customer_id:int>")
@require_permissions("customer.delete")
async def delete_customer(request: Request, customer_id: int):
    """删除客户 API"""
    user = request.ctx.user

    async for session in get_db_session():
        success = await CustomerService.delete_customer(
            session=session,
            customer_id=customer_id,
            user_id=user["user_id"],
            user_role=user["role"],
        )

        if not success:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "客户不存在或无权限"}},
                status=404,
            )

        return json(
            {
                "data": {"message": "客户删除成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
