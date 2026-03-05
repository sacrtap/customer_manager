from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict
from datetime import datetime

from app.models.transfer import CustomerTransfer
from app.models.customer import Customer


class TransferService:
    """客户转移服务层"""

    @staticmethod
    async def create_transfer(
        session: AsyncSession,
        data: Dict,
        from_sales_rep_id: int,
        created_by: int,
    ) -> CustomerTransfer:
        """创建转移申请"""
        transfer = CustomerTransfer(
            customer_id=data["customer_id"],
            from_sales_rep_id=from_sales_rep_id,
            to_sales_rep_id=data["to_sales_rep_id"],
            reason=data["reason"],
            status="pending",
            created_by=created_by,
        )

        session.add(transfer)
        await session.commit()
        await session.refresh(transfer)

        return transfer

    @staticmethod
    async def get_transfer(
        session: AsyncSession,
        transfer_id: int,
        user_id: int,
        user_role: str,
    ) -> Optional[CustomerTransfer]:
        """获取转移详情"""
        query = (
            select(CustomerTransfer)
            .options(
                selectinload(CustomerTransfer.customer),
                selectinload(CustomerTransfer.from_sales_rep),
                selectinload(CustomerTransfer.to_sales_rep),
            )
            .where(CustomerTransfer.id == transfer_id)
        )

        # 销售只能查看自己相关的转移
        if user_role == "sales":
            query = query.where(
                or_(
                    CustomerTransfer.from_sales_rep_id == user_id,
                    CustomerTransfer.to_sales_rep_id == user_id,
                )
            )

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_transfer_status(
        session: AsyncSession,
        transfer_id: int,
        status: str,
        approved_by: Optional[int] = None,
    ) -> Optional[CustomerTransfer]:
        """更新转移状态"""
        query = select(CustomerTransfer).where(CustomerTransfer.id == transfer_id)
        result = await session.execute(query)
        transfer = result.scalar_one_or_none()

        if not transfer:
            return None

        transfer.status = status
        if approved_by is not None:
            transfer.approved_by = approved_by
            transfer.approved_at = datetime.utcnow()
        transfer.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(transfer)

        return transfer

    @staticmethod
    async def approve_transfer(
        session: AsyncSession,
        transfer_id: int,
        approved_by: int,
    ) -> Optional[CustomerTransfer]:
        """审批通过转移"""
        return await TransferService.update_transfer_status(
            session, transfer_id, "approved", approved_by
        )

    @staticmethod
    async def reject_transfer(
        session: AsyncSession,
        transfer_id: int,
        approved_by: int,
    ) -> Optional[CustomerTransfer]:
        """拒绝转移"""
        return await TransferService.update_transfer_status(
            session, transfer_id, "rejected", approved_by
        )

    @staticmethod
    async def complete_transfer(
        session: AsyncSession,
        transfer_id: int,
    ) -> Optional[CustomerTransfer]:
        """完成转移（更新客户销售）"""
        # 获取转移记录
        query = select(CustomerTransfer).where(CustomerTransfer.id == transfer_id)
        result = await session.execute(query)
        transfer = result.scalar_one_or_none()

        if not transfer:
            return None

        if transfer.status != "approved":
            raise ValueError("只有已审批的转移才能完成")

        # 更新客户的销售代表
        customer_query = select(Customer).where(Customer.id == transfer.customer_id)
        customer_result = await session.execute(customer_query)
        customer = customer_result.scalar_one_or_none()

        if not customer:
            raise ValueError("客户不存在")

        customer.sales_rep_id = transfer.to_sales_rep_id
        customer.updated_at = datetime.utcnow()

        # 更新转移状态为 completed
        transfer.status = "completed"
        transfer.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(transfer)

        return transfer

    @staticmethod
    async def list_transfers(
        session: AsyncSession,
        filters: Dict,
        page: int,
        size: int,
        order_by: List[str],
        user_id: Optional[int] = None,
        user_role: Optional[str] = None,
    ) -> Dict:
        """分页查询转移列表"""
        query = select(CustomerTransfer).options(
            selectinload(CustomerTransfer.customer),
            selectinload(CustomerTransfer.from_sales_rep),
            selectinload(CustomerTransfer.to_sales_rep),
        )

        # 应用过滤条件
        if "status" in filters and filters["status"]:
            query = query.where(CustomerTransfer.status == filters["status"])

        if "customer_id" in filters and filters["customer_id"]:
            query = query.where(CustomerTransfer.customer_id == filters["customer_id"])

        if "from_sales_rep_id" in filters and filters["from_sales_rep_id"]:
            query = query.where(
                CustomerTransfer.from_sales_rep_id == filters["from_sales_rep_id"]
            )

        if "to_sales_rep_id" in filters and filters["to_sales_rep_id"]:
            query = query.where(
                CustomerTransfer.to_sales_rep_id == filters["to_sales_rep_id"]
            )

        if "created_at_start" in filters and filters["created_at_start"]:
            query = query.where(
                CustomerTransfer.created_at >= filters["created_at_start"]
            )

        if "created_at_end" in filters and filters["created_at_end"]:
            query = query.where(
                CustomerTransfer.created_at <= filters["created_at_end"]
            )

        # 销售只能查看自己相关的转移
        if user_role == "sales" and user_id is not None:
            query = query.where(
                or_(
                    CustomerTransfer.from_sales_rep_id == user_id,
                    CustomerTransfer.to_sales_rep_id == user_id,
                )
            )

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # 应用排序
        for order in order_by:
            if order.endswith(" desc"):
                field = order.replace(" desc", "")
                column = getattr(CustomerTransfer, field, None)
                if column:
                    query = query.order_by(column.desc())
            else:
                field = order.replace(" asc", "")
                column = getattr(CustomerTransfer, field, None)
                if column:
                    query = query.order_by(column.asc())

        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        # 执行查询
        result = await session.execute(query)
        transfers = result.scalars().all()

        return {
            "items": [transfer.to_dict() for transfer in transfers],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }
