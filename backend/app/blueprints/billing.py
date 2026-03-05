from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime
import uuid

from app.database import get_db_session
from app.services.billing_service import BillingService
from app.decorators.rbac import require_permissions


billing_bp = Blueprint("billing", url_prefix="/api/v1/billing")


@billing_bp.get("/")
@require_permissions("billing.view")
async def list_billings(request: Request):
    """获取结算记录列表 API"""
    params = request.args

    # 解析分页参数
    page = int(params.get("page", 1))
    size = int(params.get("size", 10))

    # 解析过滤条件
    customer_id = None
    if params.get("customer_id"):
        try:
            customer_id = int(params["customer_id"])
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

    status = params.get("status")
    billing_date_start = None
    billing_date_end = None

    if params.get("billing_date_start"):
        try:
            billing_date_start = datetime.fromisoformat(params["billing_date_start"])
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "billing_date_start 格式错误",
                    }
                },
                status=400,
            )

    if params.get("billing_date_end"):
        try:
            billing_date_end = datetime.fromisoformat(params["billing_date_end"])
        except ValueError:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "billing_date_end 格式错误",
                    }
                },
                status=400,
            )

    async for session in get_db_session():
        result = await BillingService.get_billing_list(
            session=session,
            page=page,
            size=size,
            customer_id=customer_id,
            status=status,
            billing_date_start=billing_date_start,
            billing_date_end=billing_date_end,
        )

        return json(
            {
                "data": result,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@billing_bp.post("/")
@require_permissions("billing.create")
async def create_billing(request: Request):
    """创建结算记录 API"""
    try:
        data = request.json
        customer_id = data.get("customer_id")
        customer_name = data.get("customer_name")
        amount = float(data.get("amount", 0))
        billing_date_str = data.get("billing_date")

        if not customer_id or not customer_name:
            return JSONResponse(
                {
                    "error": {
                        "code": "VALIDATION_ERROR",
                        "message": "customer_id 和 customer_name 是必填项",
                    }
                },
                status=400,
            )

        if not billing_date_str:
            billing_date = datetime.now()
        else:
            billing_date = datetime.fromisoformat(billing_date_str)

        billing_id = str(uuid.uuid4())

    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    async for session in get_db_session():
        billing = await BillingService.create_billing(
            session=session,
            customer_id=customer_id,
            customer_name=customer_name,
            amount=amount,
            billing_date=billing_date,
            billing_id=billing_id,
        )

        return json(
            {
                "data": billing.to_dict(),
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
