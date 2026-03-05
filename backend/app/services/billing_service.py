"""
Billing Service - 结算记录服务
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.billing import Billing
from app.models.customer import Customer


class BillingService:
    """结算服务"""

    @staticmethod
    async def get_billing_list(
        session: AsyncSession,
        page: int = 1,
        size: int = 10,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        billing_date_start: Optional[datetime] = None,
        billing_date_end: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """获取结算记录列表"""
        # 构建查询
        query = select(Billing)

        # 应用过滤条件
        if customer_id:
            query = query.where(Billing.customer_id == customer_id)
        if status:
            query = query.where(Billing.status == status)
        if billing_date_start:
            query = query.where(Billing.billing_date >= billing_date_start)
        if billing_date_end:
            query = query.where(Billing.billing_date <= billing_date_end)

        # 总数查询
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar() or 0

        # 分页排序查询
        query = query.order_by(desc(Billing.created_at))
        query = query.offset((page - 1) * size).limit(size)

        result = await session.execute(query)
        billings = result.scalars().all()

        # 转换为字典
        items = [billing.to_dict() for billing in billings]

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": size,
        }

    @staticmethod
    async def create_billing(
        session: AsyncSession,
        customer_id: int,
        customer_name: str,
        amount: float,
        billing_date: datetime,
        billing_id: str,
    ) -> Billing:
        """创建结算记录"""
        billing = Billing(
            id=billing_id,
            customer_id=customer_id,
            customer_name=customer_name,
            amount=amount,
            status="pending",
            billing_date=billing_date,
        )

        session.add(billing)
        await session.flush()

        return billing
