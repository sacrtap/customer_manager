"""
Health Service - 客户健康度统计服务
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, case
from sqlalchemy.sql import text

from app.models.customer import Customer


class HealthService:
    """健康度服务"""

    @staticmethod
    async def get_dashboard_stats(session: AsyncSession) -> Dict[str, Any]:
        """获取健康度仪表盘统计数据"""
        # 总客户数
        total_result = await session.execute(select(func.count(Customer.id)))
        total_customers = total_result.scalar() or 0

        # 健康客户 (health_score >= 70)
        healthy_result = await session.execute(
            select(func.count(Customer.id)).where(Customer.health_score >= 70)
        )
        healthy_customers = healthy_result.scalar() or 0

        # 风险客户 (health_score >= 40 and < 70)
        at_risk_result = await session.execute(
            select(func.count(Customer.id)).where(
                (Customer.health_score >= 40) & (Customer.health_score < 70)
            )
        )
        at_risk_customers = at_risk_result.scalar() or 0

        # 僵尸客户 (health_score < 40)
        zombie_result = await session.execute(
            select(func.count(Customer.id)).where(Customer.health_score < 40)
        )
        zombie_customers = zombie_result.scalar() or 0

        # 7 天健康趋势 (基于 created_at 模拟)
        health_trend = await HealthService._get_health_trend(session)

        # 价值分布 (按 tier_level)
        value_distribution = await HealthService._get_value_distribution(session)

        return {
            "total_customers": total_customers,
            "healthy_customers": healthy_customers,
            "at_risk_customers": at_risk_customers,
            "zombie_customers": zombie_customers,
            "health_trend": health_trend,
            "value_distribution": value_distribution,
        }

    @staticmethod
    async def _get_health_trend(session: AsyncSession) -> List[int]:
        """获取 7 天健康趋势"""
        # 简化：根据现有数据计算一个趋势
        # 实际项目中应该有 health_score_history 表
        today = datetime.now()
        trend = []

        for i in range(6, -1, -1):
            date = today - timedelta(days=i)
            # 模拟趋势数据
            base_score = 75 + (6 - i) * 2
            trend.append(base_score)

        return trend

    @staticmethod
    async def _get_value_distribution(session: AsyncSession) -> List[Dict[str, Any]]:
        """获取价值分布统计"""
        # 按 tier_level 分组统计
        result = await session.execute(
            select(
                Customer.tier_level,
                func.count(Customer.id).label("count"),
                func.sum(Customer.annual_consumption).label("total_value"),
            )
            .group_by(Customer.tier_level)
            .order_by(Customer.tier_level)
        )

        distribution = []
        for row in result:
            tier_level, count, total_value = row
            distribution.append(
                {
                    "tier": tier_level or "D",
                    "count": count or 0,
                    "value": float(total_value) if total_value else 0,
                }
            )

        # 确保所有层级都有数据
        tiers = ["A", "B", "C", "D"]
        tier_map = {item["tier"]: item for item in distribution}

        result = []
        for tier in tiers:
            if tier in tier_map:
                result.append(tier_map[tier])
            else:
                result.append({"tier": tier, "count": 0, "value": 0})

        return result
