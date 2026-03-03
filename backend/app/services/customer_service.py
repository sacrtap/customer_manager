from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict
from datetime import datetime

from app.models.customer import Customer


class CustomerService:
    """客户服务层"""

    @staticmethod
    async def create_customer(
        session: AsyncSession, data: Dict, created_by: int
    ) -> Customer:
        """创建客户"""
        customer = Customer(
            name=data["name"],
            code=data.get("code"),
            industry=data.get("industry"),
            sales_rep_id=data["sales_rep_id"],
            tier_level=data.get("tier_level", "D"),
            annual_consumption=data.get("annual_consumption", 0),
            status=data.get("status", "active"),
            contact_person=data.get("contact_person"),
            contact_phone=data.get("contact_phone"),
            contact_email=data.get("contact_email"),
            address=data.get("address"),
            remark=data.get("remark"),
        )

        session.add(customer)
        await session.commit()
        await session.refresh(customer)

        return customer

    @staticmethod
    async def get_customer(
        session: AsyncSession, customer_id: int, user_id: int, user_role: str
    ) -> Optional[Customer]:
        """获取客户详情"""
        query = select(Customer).where(Customer.id == customer_id)

        # 销售只能看自己客户
        if user_role == "sales":
            query = query.where(Customer.sales_rep_id == user_id)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update_customer(
        session: AsyncSession,
        customer_id: int,
        data: Dict,
        user_id: int,
        user_role: str,
    ) -> Optional[Customer]:
        """更新客户"""
        query = select(Customer).where(Customer.id == customer_id)

        # 销售只能看自己客户
        if user_role == "sales":
            query = query.where(Customer.sales_rep_id == user_id)

        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            return None

        # 更新字段
        if "name" in data:
            customer.name = data["name"]
        if "code" in data:
            customer.code = data["code"]
        if "industry" in data:
            customer.industry = data["industry"]
        if "tier_level" in data:
            customer.tier_level = data["tier_level"]
        if "annual_consumption" in data:
            customer.annual_consumption = data["annual_consumption"]
        if "status" in data:
            customer.status = data["status"]
        if "contact_person" in data:
            customer.contact_person = data["contact_person"]
        if "contact_phone" in data:
            customer.contact_phone = data["contact_phone"]
        if "contact_email" in data:
            customer.contact_email = data["contact_email"]
        if "address" in data:
            customer.address = data["address"]
        if "remark" in data:
            customer.remark = data["remark"]

        customer.updated_at = datetime.utcnow()

        await session.commit()
        await session.refresh(customer)

        return customer

    @staticmethod
    async def delete_customer(
        session: AsyncSession, customer_id: int, user_id: int, user_role: str
    ) -> bool:
        """删除客户"""
        query = select(Customer).where(Customer.id == customer_id)

        # 销售只能看自己客户
        if user_role == "sales":
            query = query.where(Customer.sales_rep_id == user_id)

        result = await session.execute(query)
        customer = result.scalar_one_or_none()

        if not customer:
            return False

        await session.delete(customer)
        await session.commit()

        return True

    @staticmethod
    async def list_customers(
        session: AsyncSession, filters: Dict, page: int, size: int, order_by: List[str]
    ) -> Dict:
        """分页查询客户列表"""
        query = select(Customer)

        # 应用过滤条件
        if "keyword" in filters and filters["keyword"]:
            keyword = filters["keyword"]
            query = query.where(
                or_(
                    Customer.name.ilike(f"%{keyword}%"),
                    Customer.code.ilike(f"%{keyword}%"),
                    Customer.contact_person.ilike(f"%{keyword}%"),
                )
            )

        if "sales_rep_ids" in filters and filters["sales_rep_ids"]:
            query = query.where(Customer.sales_rep_id.in_(filters["sales_rep_ids"]))

        if "industries" in filters and filters["industries"]:
            query = query.where(Customer.industry.in_(filters["industries"]))

        if "status" in filters and filters["status"]:
            query = query.where(Customer.status.in_(filters["status"]))

        if "tier_levels" in filters and filters["tier_levels"]:
            query = query.where(Customer.tier_level.in_(filters["tier_levels"]))

        if "annual_consumption_min" in filters:
            query = query.where(
                Customer.annual_consumption >= filters["annual_consumption_min"]
            )

        if "annual_consumption_max" in filters:
            query = query.where(
                Customer.annual_consumption <= filters["annual_consumption_max"]
            )

        if "created_at_start" in filters:
            query = query.where(Customer.created_at >= filters["created_at_start"])

        if "created_at_end" in filters:
            query = query.where(Customer.created_at <= filters["created_at_end"])

        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await session.execute(count_query)
        total = total_result.scalar()

        # 应用排序
        for order in order_by:
            if order.endswith(" desc"):
                field = order.replace(" desc", "")
                column = getattr(Customer, field)
                query = query.order_by(column.desc())
            else:
                field = order.replace(" asc", "")
                column = getattr(Customer, field)
                query = query.order_by(column.asc())

        # 分页
        offset = (page - 1) * size
        query = query.offset(offset).limit(size)

        # 执行查询
        result = await session.execute(query)
        customers = result.scalars().all()

        return {
            "items": [customer.to_dict() for customer in customers],
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size,
        }
