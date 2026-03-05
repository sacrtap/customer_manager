from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Numeric,
    String,
    text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .customer import Customer


class Billing(Base):
    """结算记录模型"""

    __tablename__ = "billings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)  # UUID
    customer_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("customers.id"), nullable=False, index=True
    )
    customer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "completed",
            "pending",
            "failed",
            name="billing_status_enum",
            create_constraint=True,
            metadata=Base.metadata,
            native_enum=True,
        ),
        default="pending",
        nullable=False,
        index=True,
    )
    billing_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    # 关联客户
    customer: Mapped["Customer"] = relationship(
        back_populates="billings", foreign_keys=[customer_id]
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "amount": float(self.amount) if self.amount else 0,
            "status": self.status,
            "billing_date": self.billing_date.isoformat()
            if self.billing_date
            else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
