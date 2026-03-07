"""Price Band Service - 价格区间业务逻辑"""

from typing import Any, Dict, List, Optional
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_band import PriceBand


class PriceBandService:
    """价格区间服务类"""

    @staticmethod
    async def create_price_band(
        session: AsyncSession, data: Dict[str, Any], created_by: int
    ) -> PriceBand:
        """创建价格区间"""
        price_band = PriceBand(
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
            price_config_id=data["price_config_id"],
            min_quantity=data.get("min_quantity"),
            max_quantity=data.get("max_quantity"),
            min_amount=data.get("min_amount"),
            max_amount=data.get("max_amount"),
            unit_price=data.get("unit_price"),
            discount_rate=data.get("discount_rate"),
            final_price=data.get("final_price"),
            priority=data.get("priority", 1),
            is_active=data.get("status", "active") == "active",
            valid_from=data.get("valid_from"),
            valid_until=data.get("valid_until"),
            created_by=created_by,
            created_at=datetime.now(),
        )
        session.add(price_band)
        await session.flush()
        await session.refresh(price_band)
        return price_band

    @staticmethod
    async def get_price_band(
        session: AsyncSession, price_band_id: int
    ) -> Optional[PriceBand]:
        """根据 ID 获取价格区间"""
        result = await session.execute(
            select(PriceBand).where(PriceBand.id == price_band_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_price_band(
        session: AsyncSession,
        price_band_id: int,
        data: Dict[str, Any],
        updated_by: int,
    ) -> Optional[PriceBand]:
        """更新价格区间"""
        price_band = await PriceBandService.get_price_band(session, price_band_id)
        if not price_band:
            return None

        for key, value in data.items():
            if value is not None and key != "updated_by":
                setattr(price_band, key, value)

        price_band.updated_by = updated_by
        await session.flush()
        await session.refresh(price_band)
        return price_band

    @staticmethod
    async def delete_price_band(session: AsyncSession, price_band_id: int) -> bool:
        """删除价格区间"""
        price_band = await PriceBandService.get_price_band(session, price_band_id)
        if not price_band:
            return False

        await session.delete(price_band)
        await session.flush()
        return True

    @staticmethod
    async def list_price_bands(
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20,
        order_by: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """获取价格区间列表"""
        filters = filters or {}

        # 构建查询
        stmt = select(PriceBand)
        conditions = []

        # 代码筛选
        if filters.get("code"):
            conditions.append(PriceBand.code.ilike(f"%{filters['code']}%"))

        # 名称筛选
        if filters.get("name"):
            conditions.append(PriceBand.name.ilike(f"%{filters['name']}%"))

        # 价格配置 ID 筛选
        if filters.get("price_config_id"):
            conditions.append(PriceBand.price_config_id == filters["price_config_id"])

        # 状态筛选
        if filters.get("status"):
            conditions.append(PriceBand.status == filters["status"])

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 总数
        count_stmt = select(PriceBand.id)
        if conditions:
            count_stmt = count_stmt.where(and_(*conditions))
        total_result = await session.execute(count_stmt)
        total = len(total_result.scalars().all())

        # 排序
        if order_by:
            order_clauses = []
            for order in order_by:
                parts = order.split()
                field = parts[0]
                direction = parts[1] if len(parts) > 1 else "asc"

                if hasattr(PriceBand, field):
                    col = getattr(PriceBand, field)
                    order_clauses.append(
                        col.desc() if direction == "desc" else col.asc()
                    )

            if order_clauses:
                stmt = stmt.order_by(*order_clauses)
        else:
            # 默认按优先级降序
            stmt = stmt.order_by(PriceBand.priority.desc())

        # 分页
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)

        # 执行查询
        result = await session.execute(stmt)
        price_bands = result.scalars().all()

        return {
            "items": [band.to_dict() for band in price_bands],
            "total": total,
            "page": page,
            "page_size": size,
        }
