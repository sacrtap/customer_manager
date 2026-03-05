"""Price Band Blueprint - 价格区间 API 路由"""

from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from datetime import datetime

from app.database import get_db_session
from app.services.price_band_service import PriceBandService
from app.decorators.rbac import require_permissions
from app.schemas.price_band import (
    PriceBandCreateRequest,
    PriceBandUpdateRequest,
)


price_band_bp = Blueprint("price_band", url_prefix="/api/v1/price-bands")


@price_band_bp.get("/")
@require_permissions("pricing.view")
async def list_price_bands(request: Request):
    """获取价格区间列表 API"""
    params = request.args

    # 构建过滤条件
    filters = {}
    if params.get("code"):
        filters["code"] = params["code"]
    if params.get("name"):
        filters["name"] = params["name"]
    if params.get("price_config_id"):
        filters["price_config_id"] = int(params["price_config_id"])
    if params.get("status"):
        filters["status"] = params["status"]

    # 排序
    order_by = []
    if params.get("sort_field"):
        direction = "desc" if params.get("sort_desc", "false") == "true" else "asc"
        order_by.append(f"{params['sort_field']} {direction}")
    else:
        order_by.append("priority desc")

    # 分页
    page = int(params.get("page", 1))
    size = int(params.get("size", 10))

    # 查询
    async for session in get_db_session():
        result = await PriceBandService.list_price_bands(
            session=session, filters=filters, page=page, size=size, order_by=order_by
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})


@price_band_bp.post("/")
@require_permissions("pricing.create")
async def create_price_band(request: Request):
    """创建价格区间 API"""
    try:
        data = PriceBandCreateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        price_band = await PriceBandService.create_price_band(
            session=session, data=data.model_dump(), created_by=user["user_id"]
        )

        return json(
            {"data": price_band.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@price_band_bp.get("/<band_id:int>")
@require_permissions("pricing.view")
async def get_price_band(request: Request, band_id: int):
    """获取价格区间详情 API"""
    async for session in get_db_session():
        price_band = await PriceBandService.get_price_band(
            session=session, price_band_id=band_id
        )

        if not price_band:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "价格区间不存在"}},
                status=404,
            )

        return json(
            {"data": price_band.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@price_band_bp.put("/<band_id:int>")
@require_permissions("pricing.update")
async def update_price_band(request: Request, band_id: int):
    """更新价格区间 API"""
    try:
        data = PriceBandUpdateRequest(**request.json)
    except Exception as e:
        return JSONResponse(
            {"error": {"code": "VALIDATION_ERROR", "message": str(e)}}, status=400
        )

    user = request.ctx.user

    async for session in get_db_session():
        price_band = await PriceBandService.update_price_band(
            session=session,
            price_band_id=band_id,
            data=data.model_dump(exclude_unset=True),
            updated_by=user["user_id"],
        )

        if not price_band:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "价格区间不存在"}},
                status=404,
            )

        return json(
            {"data": price_band.to_dict(), "timestamp": datetime.utcnow().isoformat()}
        )


@price_band_bp.delete("/<band_id:int>")
@require_permissions("pricing.delete")
async def delete_price_band(request: Request, band_id: int):
    """删除价格区间 API"""
    async for session in get_db_session():
        success = await PriceBandService.delete_price_band(
            session=session, price_band_id=band_id
        )

        if not success:
            return JSONResponse(
                {"error": {"code": "NOT_FOUND", "message": "价格区间不存在"}},
                status=404,
            )

        return json(
            {
                "data": {"message": "价格区间删除成功"},
                "timestamp": datetime.utcnow().isoformat(),
            }
        )


@price_band_bp.get("/config/<config_id:int>/price-bands")
@require_permissions("pricing.view")
async def list_config_price_bands(request: Request, config_id: int):
    """获取价格配置下的所有价格区间"""
    async for session in get_db_session():
        result = await PriceBandService.list_price_bands(
            session=session,
            filters={"price_config_id": config_id},
            page=1,
            size=100,
        )

        return json({"data": result, "timestamp": datetime.utcnow().isoformat()})
