from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime

from app.database import get_db_session
from app.services.transfer_service import TransferService
from app.decorators.rbac import require_permissions
from app.schemas.transfer import TransferCreateRequest


transfer_bp = Blueprint("transfer", url_prefix="/api/v1/transfers")


@transfer_bp.get("/")
@require_permissions("customer.transfer.view")
async def list_transfers(request: Request):
    """转移记录列表 API"""
    params = request.args

    # 解析分页参数
    page = int(params.get("page", 1))
    size = int(params.get("size", 10))

    # 解析过滤条件
    filters = {}
    if params.get("status"):
        filters["status"] = params["status"]
    if params.get("customer_id"):
        try:
            filters["customer_id"] = int(params["customer_id"])
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "customer_id 必须是整数",
                    }
                },
                status=400,
            )
    if params.get("from_sales_rep_id"):
        try:
            filters["from_sales_rep_id"] = int(params["from_sales_rep_id"])
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "from_sales_rep_id 必须是整数",
                    }
                },
                status=400,
            )
    if params.get("to_sales_rep_id"):
        try:
            filters["to_sales_rep_id"] = int(params["to_sales_rep_id"])
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "to_sales_rep_id 必须是整数",
                    }
                },
                status=400,
            )
    if params.get("created_at_start"):
        try:
            filters["created_at_start"] = datetime.fromisoformat(
                params["created_at_start"]
            )
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "created_at_start 格式错误",
                    }
                },
                status=400,
            )
    if params.get("created_at_end"):
        try:
            filters["created_at_end"] = datetime.fromisoformat(params["created_at_end"])
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "created_at_end 格式错误",
                    }
                },
                status=400,
            )

    # 销售只能查看自己相关的转移
    user = request.ctx.user
    if user["role"] == "sales":
        user_id = user["user_id"]
    else:
        user_id = None

    # 排序
    order_by = []
    if params.get("sort_field"):
        direction = "desc" if params.get("sort_desc", "false") == "true" else "asc"
        order_by.append(f"{params['sort_field']} {direction}")
    else:
        order_by.append("created_at desc")

    async for session in get_db_session():
        result = await TransferService.list_transfers(
            session=session,
            filters=filters,
            page=page,
            size=size,
            order_by=order_by,
            user_id=user_id,
            user_role=user["role"],
        )

        return json(
            {
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@transfer_bp.post("/")
@require_permissions("customer.transfer")
async def create_transfer(request: Request):
    """创建转移申请 API"""
    try:
        data = TransferCreateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    # 验证转出和转入销售不能相同
    from_sales_rep_id = user["user_id"]
    if from_sales_rep_id == data.to_sales_rep_id:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "转出销售和转入销售不能相同",
                }
            },
            status=400,
        )

    async for session in get_db_session():
        # 验证客户存在
        from app.models.customer import Customer
        from sqlalchemy import select

        customer_query = select(Customer).where(Customer.id == data.customer_id)
        customer_result = await session.execute(customer_query)
        customer = customer_result.scalar_one_or_none()

        if not customer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "客户不存在"}}, status=404
            )

        # 创建转移
        transfer = await TransferService.create_transfer(
            session=session,
            data=data.model_dump(),
            from_sales_rep_id=from_sales_rep_id,
            created_by=user["user_id"],
        )

        return json(
            {
                "data": transfer.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@transfer_bp.get("/<transfer_id:int>")
@require_permissions("customer.transfer.view")
async def get_transfer(request: Request, transfer_id: int):
    """获取转移详情 API"""
    user = request.ctx.user

    async for session in get_db_session():
        transfer = await TransferService.get_transfer(
            session=session,
            transfer_id=transfer_id,
            user_id=user["user_id"],
            user_role=user["role"],
        )

        if not transfer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "转移记录不存在"}},
                status=404,
            )

        return json(
            {
                "data": transfer.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@transfer_bp.post("/<transfer_id:int>/approve")
@require_permissions("customer.transfer.approve")
async def approve_transfer(request: Request, transfer_id: int):
    """审批转移申请 API"""
    user = request.ctx.user

    async for session in get_db_session():
        transfer = await TransferService.approve_transfer(
            session=session,
            transfer_id=transfer_id,
            approved_by=user["user_id"],
        )

        if not transfer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "转移记录不存在"}},
                status=404,
            )

        return json(
            {
                "data": transfer.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@transfer_bp.post("/<transfer_id:int>/reject")
@require_permissions("customer.transfer.approve")
async def reject_transfer(request: Request, transfer_id: int):
    """拒绝转移申请 API"""
    user = request.ctx.user

    async for session in get_db_session():
        transfer = await TransferService.reject_transfer(
            session=session,
            transfer_id=transfer_id,
            approved_by=user["user_id"],
        )

        if not transfer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "转移记录不存在"}},
                status=404,
            )

        return json(
            {
                "data": transfer.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@transfer_bp.post("/<transfer_id:int>/complete")
@require_permissions("customer.transfer")
async def complete_transfer(request: Request, transfer_id: int):
    """完成转移申请 API"""
    user = request.ctx.user

    async for session in get_db_session():
        try:
            transfer = await TransferService.complete_transfer(
                session=session,
                transfer_id=transfer_id,
            )
        except ValueError as e:
            return JSONResponse(
                {"error": {"code": "INVALID_STATE", "message": str(e)}}, status=400
            )

        if not transfer:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "转移记录不存在"}},
                status=404,
            )

        return json(
            {
                "data": transfer.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
