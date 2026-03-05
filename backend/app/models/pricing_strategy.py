from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class PricingStrategy(Base):
    """定价策略模型"""

    __tablename__ = "pricing_strategies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=True)

    # 适用客户类型
    applicable_customer_type: Mapped[str] = mapped_column(String(50), nullable=True)
    applicable_tier_levels: Mapped[str] = mapped_column(
        String(50), nullable=True, comment="适用价值等级，如 A,B,C 或 *"
    )

    # 折扣类型和比率
    discount_type: Mapped[str] = mapped_column(
        String(20),
        default="percentage",
        nullable=False,
        comment="percentage(百分比) 或 fixed(固定金额)",
    )
    discount_value: Mapped[Decimal] = mapped_column(
        Numeric(10, 4),
        default=0,
        nullable=False,
        comment="折扣值，百分比类型为 0-100，固定金额类型为具体数值",
    )

    # 优先级
    priority: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False)

    # 状态
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False,
        index=True,
        comment="active(启用), inactive(禁用), draft(草稿)",
    )

    # 有效期
    valid_from: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    valid_to: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    # 审计字段
    created_by: Mapped[int] = mapped_column(BigInteger, nullable=False)
    updated_by: Mapped[int] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (
        Index("idx_status_priority", "status", "priority"),
        Index("idx_validity", "valid_from", "valid_to"),
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "applicable_customer_type": self.applicable_customer_type,
            "applicable_tier_levels": self.applicable_tier_levels,
            "discount_type": self.discount_type,
            "discount_value": float(self.discount_value) if self.discount_value else 0,
            "priority": self.priority,
            "status": self.status,
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "created_by": self.created_by,
            "updated_by": self.updated_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
