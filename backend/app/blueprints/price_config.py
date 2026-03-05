"""Price Config Blueprint - 价格配置 API 路由"""

from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime

from app.database import get_db_session
from app.services.price_config_service import PriceConfigService
from app.decorators.rbac import require_permissions
from app.schemas.price_config import (
    PriceConfigCreateRequest,
    PriceConfigUpdateRequest,
)


price_config_bp = Blueprint("price_config", url_prefix="/api/v1/price-configs")


@price_config_bp.get("/")
@require_permissions("pricing.view")
async def list_configs(request: Request):
    """价格配置列表 API"""
    params = request.args

    # 构建过滤条件
    filters = {}
    if params.get("code"):
        filters["code"] = params["code"]
    if params.get("name"):
        filters["name"] = params["name"]
    if params.get("status"):
        filters["status"] = params["status"]

    # 排序
    order_by = []
    if params.get("sort_field"):
        direction = "desc" if params.get("sort_desc", "false") == "true" else "asc"
        order_by.append(f"{params['sort_field']} {direction}")
    else:
        order_by.append("id desc")

    # 分页
    page = int(params.get("page", 1))
    size = int(params.get("size", 10))

    # 查询
    async for session in get_db_session():
        result = await PriceConfigService.list_price_configs(
            session=session, filters=filters, page=page, size=size, order_by=order_by
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})


@price_config_bp.get("/<config_id:int>")
@require_permissions("pricing.view")
async def get_config(request: Request, config_id: int):
    """获取价格配置详情 API"""
    async for session in get_db_session():
        config = await PriceConfigService.get_price_config(
            session=session, price_config_id=config_id
        )

        if not config:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "价格配置不存在"}},
                status=404,
            )

        return json(
            {"data": config.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@price_config_bp.post("/")
@require_permissions("pricing.create")
async def create_config(request: Request):
    """创建价格配置 API"""
    try:
        data = PriceConfigCreateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        config = await PriceConfigService.create_price_config(
            session=session, data=data.model_dump(), created_by=user["user_id"]
        )

        return json(
            {"data": config.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@price_config_bp.put("/<config_id:int>")
@require_permissions("pricing.update")
async def update_config(request: Request, config_id: int):
    """更新价格配置 API"""
    try:
        data = PriceConfigUpdateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        config = await PriceConfigService.update_price_config(
            session=session,
            price_config_id=config_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=user["user_id"],
        )

        if not config:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "价格配置不存在"}},
                status=404,
            )

        return json(
            {"data": config.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@price_config_bp.delete("/<config_id:int>")
@require_permissions("pricing.delete")
async def delete_config(request: Request, config_id: int):
    """删除价格配置 API"""
    async for session in get_db_session():
        success = await PriceConfigService.delete_price_config(
            session=session, price_config_id=config_id
        )

        if not success:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "价格配置不存在"}},
                status=404,
            )

        return json(
            {
                "data": {"message": "价格配置删除成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@price_config_bp.get("/<config_id:int>/price-bands")
@require_permissions("pricing.view")
async def list_config_price_bands(request: Request, config_id: int):
    """获取价格配置下的所有价格区间"""
    from app.services.price_band_service import PriceBandService

    async for session in get_db_session():
        result = await PriceBandService.list_price_bands(
            session=session,
            filters={"price_config_id": config_id},
            page=1,
            size=100,
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})
