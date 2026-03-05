"""Price Config Service - 价格配置业务逻辑"""

from typing import Any, Dict, List, Optional
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_config import PriceConfig
from app.schemas.price_config import PriceConfigQuery


class PriceConfigService:
    """价格配置服务类"""

    @staticmethod
    async def create_price_config(
        session: AsyncSession, data: Dict[str, Any], created_by: int
    ) -> PriceConfig:
        """创建价格配置"""
        price_config = PriceConfig(
            code=data["code"],
            name=data["name"],
            description=data.get("description"),
            base_price=data["base_price"],
            status=data.get("status", "active"),
            created_by=created_by,
        )
        session.add(price_config)
        await session.flush()
        await session.refresh(price_config)
        return price_config

    @staticmethod
    async def get_price_config(
        session: AsyncSession, price_config_id: int
    ) -> Optional[PriceConfig]:
        """获取价格配置详情"""
        result = await session.execute(
            select(PriceConfig).where(PriceConfig.id == price_config_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def update_price_config(
        session: AsyncSession,
        price_config_id: int,
        data: Dict[str, Any],
        updated_by: int,
    ) -> Optional[PriceConfig]:
        """更新价格配置"""
        price_config = await PriceConfigService.get_price_config(
            session, price_config_id
        )
        if not price_config:
            return None

        for key, value in data.items():
            if value is not None and key != "updated_by":
                setattr(price_config, key, value)

        price_config.updated_by = updated_by
        await session.flush()
        await session.refresh(price_config)
        return price_config

    @staticmethod
    async def delete_price_config(session: AsyncSession, price_config_id: int) -> bool:
        """删除价格配置"""
        price_config = await PriceConfigService.get_price_config(
            session, price_config_id
        )
        if not price_config:
            return False

        await session.delete(price_config)
        await session.flush()
        return True

    @staticmethod
    async def list_price_configs(
        session: AsyncSession,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        size: int = 20,
        order_by: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """获取价格配置列表"""
        filters = filters or {}

        # 构建查询
        stmt = select(PriceConfig)
        conditions = []

        # 代码筛选
        if filters.get("code"):
            conditions.append(PriceConfig.code.ilike(f"%{filters['code']}%"))

        # 名称筛选
        if filters.get("name"):
            conditions.append(PriceConfig.name.ilike(f"%{filters['name']}%"))

        # 状态筛选
        if filters.get("status"):
            conditions.append(PriceConfig.status == filters["status"])

        if conditions:
            stmt = stmt.where(and_(*conditions))

        # 总数
        count_stmt = select(PriceConfig.id)
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

                if hasattr(PriceConfig, field):
                    col = getattr(PriceConfig, field)
                    order_clauses.append(
                        col.desc() if direction == "desc" else col.asc()
                    )

            if order_clauses:
                stmt = stmt.order_by(*order_clauses)
        else:
            # 默认按 ID 降序
            stmt = stmt.order_by(PriceConfig.id.desc())

        # 分页
        offset = (page - 1) * size
        stmt = stmt.offset(offset).limit(size)

        # 执行查询
        result = await session.execute(stmt)
        configs = result.scalars().all()

        return {
            "items": [config.to_dict() for config in configs],
            "total": total,
            "page": page,
            "page_size": size,
        }
