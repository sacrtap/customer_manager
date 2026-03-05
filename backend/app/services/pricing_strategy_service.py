from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from typing import Optional, List, Dict
from datetime import datetime

from app.models.pricing_strategy import PricingStrategy


class PricingStrategyService:
    """定价策略服务层"""

    @staticmethod
    async def create_strategy(
        session: AsyncSession, data: Dict, created_by: int
    ) -> PricingStrategy:
        """创建定价策略"""
        strategy = PricingStrategy(
            name=data["name"],
            code=data["code"],
            description=data.get("description"),
            applicable_customer_type=data.get("applicable_customer_type"),
            applicable_tier_levels=data.get("applicable_tier_levels"),
            discount_type=data.get("discount_type", "percentage"),
            discount_value=data.get("discount_value", 0),
            priority=data.get("priority", 0),
            status=data.get("status", "active"),
            valid_from=data.get("valid_from"),
            valid_to=data.get("valid_to"),
            created_by=created_by,
        )

        session.add(strategy)
        await session.commit()
        await session.refresh(strategy)

        return strategy

    @staticmethod
    async def get_strategy(
        session: AsyncSession, strategy_id: int
    ) -> Optional[PricingStrategy]:
        """获取定价策略详情"""
        query = select(PricingStrategy).where(PricingStrategy.id == strategy_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_strategy(
        session: AsyncSession, strategy_id: int, data: Dict, updated_by: int
    ) -> Optional[PricingStrategy]:
        """更新定价策略"""
        query = select(PricingStrategy).where(PricingStrategy.id == strategy_id)
        result = await session.execute(query)
        strategy = result.scalar_one_or_none()

        if not strategy:
            return None

        # 更新字段
        if "name" in data:
            strategy.name = data["name"]
        if "code" in data:
            strategy.code = data["code"]
        if "description" in data:
            strategy.description = data["description"]
        if "applicable_customer_type" in data:
            strategy.applicable_customer_type = data["applicable_customer_type"]
        if "applicable_tier_levels" in data:
            strategy.applicable_tier_levels = data["applicable_tier_levels"]
        if "discount_type" in data:
            strategy.discount_type = data["discount_type"]
        if "discount_value" in data:
            strategy.discount_value = data["discount_value"]
        if "priority" in data:
            strategy.priority = data["priority"]
        if "status" in data:
            strategy.status = data["status"]
        if "valid_from" in data:
            strategy.valid_from = data["valid_from"]
        if "valid_to" in data:
            strategy.valid_to = data["valid_to"]

        strategy.updated_by = updated_by
        strategy.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(strategy)

        return strategy

    @staticmethod
    async def delete_strategy(session: AsyncSession, strategy_id: int) -> bool:
        """删除定价策略"""
        query = select(PricingStrategy).where(PricingStrategy.id == strategy_id)
        result = await session.execute(query)
        strategy = result.scalar_one_or_none()

        if not strategy:
            return False

        await session.delete(strategy)
        await session.commit()

        return True

    @staticmethod
    async def list_strategies(
        session: AsyncSession, filters: Dict, page: int, size: int, order_by: List[str]
    ) -> Dict:
        """分页查询定价策略列表"""
        query = select(PricingStrategy)

        # 应用过滤条件
        if "keyword" in filters and filters["keyword"]:
            keyword = filters["keyword"]
            query = query.where(
                or_(
                    PricingStrategy.name.ilike(f"%{keyword}%"),
                    PricingStrategy.code.ilike(f"%{keyword}%"),
                    PricingStrategy.description.ilike(f"%{keyword}%"),
                )
            )

        if "status" in filters and filters["status"]:
            query = query.where(PricingStrategy.status.in_(filters["status"]))

        if "discount_type" in filters and filters["discount_type"]:
            query = query.where(
                PricingStrategy.discount_type == filters["discount_type"]
            )

        if "applicable_tier_levels" in filters and filters["applicable_tier_levels"]:
            query = query.where(
                PricingStrategy.applicable_tier_levels.ilike(
                    f"%{filters['applicable_tier_levels']}%"
                )
            )

        if "valid_from" in filters:
            query = query.where(PricingStrategy.valid_from >= filters["valid_from"])

        if "valid_to" in filters:
            query = query.where(PricingStrategy.valid_to <= filters["valid_to"])

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # 应用排序
        for order in order_by:
            if order.endswith(" desc"):
                field = order.replace(" desc", "")
                column = getattr(PricingStrategy, field)
                query = query.order_by(column.desc())
            else:
                field = order.replace(" asc", "")
                column = getattr(PricingStrategy, field)
                query = query.order_by(column.asc())

        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        # 执行查询
        result = await session.execute(query)
        strategies = result.scalars().all()

        return {
            "items": [strategy.to_dict() for strategy in strategies],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }
