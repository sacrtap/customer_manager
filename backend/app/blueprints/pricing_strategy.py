from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime

from app.database import get_db_session
from app.services.pricing_strategy_service import PricingStrategyService
from app.decorators.rbac import require_permissions
from app.schemas.pricing_strategy import (
    PricingStrategyCreateRequest,
    PricingStrategyUpdateRequest,
)


pricing_strategy_bp = Blueprint(
    "pricing_strategy", url_prefix="/api/v1/pricing-strategies"
)


@pricing_strategy_bp.get("/")
@require_permissions("pricing.view")
async def list_strategies(request: Request):
    """定价策略列表 API"""
    params = request.args

    # 构建过滤条件
    filters = {}
    if params.get("keyword"):
        filters["keyword"] = params["keyword"]
    if params.get("status"):
        status = params["status"]
        filters["status"] = status if isinstance(status, list) else status.split(",")
    if params.get("discount_type"):
        filters["discount_type"] = params["discount_type"]
    if params.get("applicable_tier_levels"):
        filters["applicable_tier_levels"] = params["applicable_tier_levels"]
    if params.get("valid_from"):
        filters["valid_from"] = datetime.fromisoformat(params["valid_from"])
    if params.get("valid_to"):
        filters["valid_to"] = datetime.fromisoformat(params["valid_to"])

    # 排序
    order_by = []
    if params.get("sort_field"):
        direction = "desc" if params.get("sort_desc", "false") == "true" else "asc"
        order_by.append(f"{params['sort_field']} {direction}")
    else:
        order_by.append("priority asc")

    # 分页
    page = int(params.get("page", 1))
    size = int(params.get("size", 10))

    # 查询
    async for session in get_db_session():
        result = await PricingStrategyService.list_strategies(
            session=session, filters=filters, page=page, size=size, order_by=order_by
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})


@pricing_strategy_bp.post("/")
@require_permissions("pricing.create")
async def create_strategy(request: Request):
    """创建定价策略 API"""
    try:
        data = PricingStrategyCreateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        strategy = await PricingStrategyService.create_strategy(
            session=session, data=data.model_dump(), created_by=user["user_id"]
        )

        return json(
            {"data": strategy.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@pricing_strategy_bp.get("/<strategy_id:int>")
@require_permissions("pricing.view")
async def get_strategy(request: Request, strategy_id: int):
    """获取定价策略详情 API"""
    async for session in get_db_session():
        strategy = await PricingStrategyService.get_strategy(
            session=session, strategy_id=strategy_id
        )

        if not strategy:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "定价策略不存在"}},
                status=404,
            )

        return json(
            {"data": strategy.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@pricing_strategy_bp.put("/<strategy_id:int>")
@require_permissions("pricing.update")
async def update_strategy(request: Request, strategy_id: int):
    """更新定价策略 API"""
    try:
        data = PricingStrategyUpdateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        strategy = await PricingStrategyService.update_strategy(
            session=session,
            strategy_id=strategy_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=user["user_id"],
        )

        if not strategy:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "定价策略不存在"}},
                status=404,
            )

        return json(
            {"data": strategy.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@pricing_strategy_bp.delete("/<strategy_id:int>")
@require_permissions("pricing.delete")
async def delete_strategy(request: Request, strategy_id: int):
    """删除定价策略 API"""
    async for session in get_db_session():
        success = await PricingStrategyService.delete_strategy(
            session=session, strategy_id=strategy_id
        )

        if not success:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "定价策略不存在"}},
                status=404,
            )

        return json(
            {
                "data": {"message": "定价策略删除成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
