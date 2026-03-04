from sanic import Blueprint, Request
from sanic.response import json, JSONResponse
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session
from app.models.operation_log import OperationLog
from app.decorators.rbac import require_permissions


system_bp = Blueprint("system", url_prefix="/api/v1/system")


@system_bp.get("/logs")
@require_permissions("system.log.view")
async def list_logs(request: Request):
    """操作日志列表 API"""
    # 解析查询参数
    page = int(request.args.get("page", 1))
    size = int(request.args.get("size", 5))
    user_id = request.args.get("user_id")

    async for session in get_db_session():
        # 构建查询
        query = select(OperationLog).order_by(desc(OperationLog.created_at))

        # 用户 ID 过滤（可选）
        if user_id:
            query = query.where(OperationLog.user_id == int(user_id))

        # 分页
        offset = (page - 1) * size
        query = query.limit(size).offset(offset)

        # 执行查询
        result = await session.execute(query)
        logs = result.scalars().all()

        # 计算总数
        count_query = select(OperationLog)
        if user_id:
            count_query = count_query.where(OperationLog.user_id == int(user_id))
        total_result = await session.execute(count_query)
        total = len(total_result.scalars().all())

        return json(
            {
                "data": {
                    "items": [log.to_dict() for log in logs],
                    "total": total,
                    "page": page,
                    "size": size,
                },
                "timestamp": "2026-03-04T21:10:00Z",
            }
        )
