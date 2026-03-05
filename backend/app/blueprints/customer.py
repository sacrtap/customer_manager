from sanic import Blueprint, Request
from sanic.response import json, JSONResponse, raw
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict
from datetime import datetime

from app.database import get_db_session
from app.services.customer_service import CustomerService
from app.decorators.rbac import require_permissions
from app.schemas.customer import CustomerCreateRequest, CustomerUpdateRequest
from app.utils.excel import (
    generate_import_template,
    parse_import_excel,
    generate_export_excel,
)


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
        sales_rep_ids = params["sales_rep_ids"]
        filters["sales_rep_ids"] = (
            sales_rep_ids
            if isinstance(sales_rep_ids, list)
            else sales_rep_ids.split(",")
        )
    if params.get("industries"):
        industries = params["industries"]
        filters["industries"] = (
            industries if isinstance(industries, list) else industries.split(",")
        )
    if params.get("status"):
        status = params["status"]
        filters["status"] = status if isinstance(status, list) else status.split(",")
    if params.get("tier_levels"):
        tier_levels = params["tier_levels"]
        filters["tier_levels"] = (
            tier_levels if isinstance(tier_levels, list) else tier_levels.split(",")
        )
    if params.get("annual_consumption_min"):
        min_val = params["annual_consumption_min"]
        filters["annual_consumption_min"] = (
            float(min_val[0]) if isinstance(min_val, list) else float(min_val)
        )
    if params.get("annual_consumption_max"):
        max_val = params["annual_consumption_max"]
        filters["annual_consumption_max"] = (
            float(max_val[0]) if isinstance(max_val, list) else float(max_val)
        )
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


@customer_bp.get("/import-template")
@require_permissions("customer.view")
async def download_import_template(request: Request):
    """下载导入模板"""
    template = generate_import_template()

    return raw(
        template.getvalue(),
        headers={
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": "attachment; filename=客户导入模板.xlsx",
        },
    )


@customer_bp.post("/import")
@require_permissions("customer.import")
async def import_customers(request: Request):
    """批量导入客户"""
    # 检查文件上传
    if not request.files.get("file"):
        return JSONResponse(
            {
                "error": {
                    "code": "NO_FILE",
                    "message": "请上传 Excel 文件",
                }
            },
            status=400,
        )

    # 读取文件内容
    file = request.files.get("file")
    file_content = file.body

    # 解析 Excel 文件
    parse_result = parse_import_excel(file_content)

    # 检查是否有错误
    if parse_result["errors"]:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "文件中存在错误数据",
                    "details": parse_result["errors"],
                }
            },
            status=400,
        )

    # 批量导入
    imported_count = 0
    failed_count = 0
    errors = []

    user = request.ctx.user

    async for session in get_db_session():
        for customer_item in parse_result["customers"]:
            try:
                customer_data = customer_item["data"]

                # 转换数据类型
                if customer_data["annual_consumption"]:
                    customer_data["annual_consumption"] = float(
                        customer_data["annual_consumption"]
                    )
                else:
                    customer_data["annual_consumption"] = 0.0

                if customer_data["sales_rep_id"]:
                    customer_data["sales_rep_id"] = int(customer_data["sales_rep_id"])

                # 创建客户
                await CustomerService.create_customer(
                    session=session, data=customer_data, created_by=user["user_id"]
                )

                imported_count += 1

            except Exception as e:
                failed_count += 1
                errors.append(
                    {
                        "row": customer_item["row"],
                        "name": customer_item["data"]["name"],
                        "message": str(e),
                    }
                )

    return json(
        {
            "data": {
                "imported_count": imported_count,
                "failed_count": failed_count,
                "errors": errors,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }
    )


@customer_bp.get("/export")
@require_permissions("customer.export")
async def export_customers(request: Request):
    """批量导出客户"""
    # 解析查询参数(同列表查询)
    params = request.args

    # 构建过滤条件(同列表查询)
    filters = {}
    if params.get("keyword"):
        filters["keyword"] = params["keyword"]
    if params.get("sales_rep_ids"):
        sales_rep_ids = params["sales_rep_ids"]
        filters["sales_rep_ids"] = (
            sales_rep_ids
            if isinstance(sales_rep_ids, list)
            else sales_rep_ids.split(",")
        )
    if params.get("industries"):
        industries = params["industries"]
        filters["industries"] = (
            industries if isinstance(industries, list) else industries.split(",")
        )
    if params.get("status"):
        filters["status"] = params["status"]
    if params.get("tier_levels"):
        tier_levels = params["tier_levels"]
        filters["tier_levels"] = (
            tier_levels if isinstance(tier_levels, list) else tier_levels.split(",")
        )

    # 销售只能导出自己客户
    user = request.ctx.user
    if user["role"] == "sales":
        filters["sales_rep_ids"] = [str(user["user_id"])]

    # 查询所有客户(不分页)
    async for session in get_db_session():
        result = await CustomerService.list_customers(
            session=session,
            filters=filters,
            page=1,
            size=10000,  # 大数量
            order_by=["name asc"],
        )

        customers = result["items"]

    # 生成 Excel 文件
    excel_content = generate_export_excel(customers)

    return raw(
        excel_content.getvalue(),
        headers={
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": f"attachment; filename=客户数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        },
    )
