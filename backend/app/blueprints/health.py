from sanic import Blueprint, Request
from sanic.response import json
from datetime import datetime

from app.database import get_db_session
from app.services.health_service import HealthService
from app.decorators.rbac import require_permissions


health_bp = Blueprint("health", url_prefix="/api/v1/health")


@health_bp.get("/dashboard")
@require_permissions("dashboard.view")
async def get_health_dashboard(request: Request):
    """获取健康度仪表盘数据 API"""
    async for session in get_db_session():
        stats = await HealthService.get_dashboard_stats(session)

        return json(
            {
                "data": stats,
                "timestamp": datetime.utcnow().isoformat(),
            }
        )
