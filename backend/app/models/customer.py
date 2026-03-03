from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Index, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base


class Customer(Base):
    """客户模型"""

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=True, index=True
    )
    industry: Mapped[str] = mapped_column(String(100), nullable=True)
    sales_rep_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    tier_level: Mapped[str] = mapped_column(
        String(1), default="D", nullable=False, index=True
    )
    annual_consumption: Mapped[float] = mapped_column(Numeric(15, 2), default=0)
    status: Mapped[str] = mapped_column(String(20), default="active", index=True)
    contact_person: Mapped[str] = mapped_column(String(100), nullable=True)
    contact_phone: Mapped[str] = mapped_column(String(20), nullable=True)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=True)
    address: Mapped[str] = mapped_column(Text, nullable=True)
    remark: Mapped[dict[str, str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    __table_args__ = (Index("idx_sales_tier", "sales_rep_id", "tier_level"),)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "industry": self.industry,
            "sales_rep_id": self.sales_rep_id,
            "tier_level": self.tier_level,
            "annual_consumption": float(self.annual_consumption)
            if self.annual_consumption
            else 0,
            "status": self.status,
            "contact_person": self.contact_person,
            "contact_phone": self.contact_phone,
            "contact_email": self.contact_email,
            "address": self.address,
            "remark": self.remark,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
