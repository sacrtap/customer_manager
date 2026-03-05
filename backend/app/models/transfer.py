from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base

if TYPE_CHECKING:
    from .customer import Customer
    from .user import User


class CustomerTransfer(Base):
    """客户转移记录模型"""

    __tablename__ = "customer_transfers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    customer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    from_sales_rep_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    to_sales_rep_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "pending",
            "approved",
            "rejected",
            "completed",
            name="transfer_status_enum",
            create_constraint=True,
            metadata=Base.metadata,
        ),
        default="pending",
        nullable=False,
        index=True,
    )
    approved_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_by: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )

    # 关联客户
    customer: Mapped["Customer"] = relationship(
        back_populates="transfers", foreign_keys=[customer_id]
    )

    # 关联用户
    from_sales_rep: Mapped["User"] = relationship(
        foreign_keys=[from_sales_rep_id],
        primaryjoin="CustomerTransfer.from_sales_rep_id == User.id",
    )
    to_sales_rep: Mapped["User"] = relationship(
        foreign_keys=[to_sales_rep_id],
        primaryjoin="CustomerTransfer.to_sales_rep_id == User.id",
    )
    approver: Mapped[Optional["User"]] = relationship(
        foreign_keys=[approved_by],
        primaryjoin="CustomerTransfer.approved_by == User.id",
    )
    creator: Mapped["User"] = relationship(
        foreign_keys=[created_by],
        primaryjoin="CustomerTransfer.created_by == User.id",
    )

    __table_args__ = (Index("idx_transfer_status", "status", "created_at"),)

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "customer_id": self.customer_id,
            "from_sales_rep_id": self.from_sales_rep_id,
            "to_sales_rep_id": self.to_sales_rep_id,
            "reason": self.reason,
            "status": self.status,
            "approved_by": self.approved_by,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
