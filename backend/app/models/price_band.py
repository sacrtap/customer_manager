"""Price Band Model - 价格区间管理"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import BigInteger, ForeignKey, Numeric, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB as PGJSONB
from sqlalchemy.types import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.config import settings


class PriceBand(Base):
    """价格区间 - 定义不同数量/金额范围内的价格"""

    __tablename__ = "price_bands"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    # 基本信息
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="区间名称")
    code: Mapped[str] = mapped_column(
        String(50), nullable=False, unique=True, comment="区间代码"
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text, nullable=True, comment="描述"
    )

    # 关联配置
    price_config_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("price_configs.id", ondelete="CASCADE"),
        nullable=True,
        comment="关联的价格配置 ID",
    )

    # 区间条件
    min_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="最小数量（包含）"
    )
    max_quantity: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="最大数量（包含）"
    )
    min_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="最小金额（包含）"
    )
    max_amount: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="最大金额（包含）"
    )

    # 价格定义
    unit_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="单价"
    )
    discount_rate: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(5, 2), nullable=True, comment="折扣率（百分比）"
    )
    final_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True, comment="最终价格"
    )

    # 优先级和状态
    priority: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, comment="优先级（数字越大优先级越高）"
    )
    is_active: Mapped[bool] = mapped_column(
        nullable=False, default=True, comment="是否启用"
    )

    # 有效期
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="生效日期"
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="失效日期"
    )

    # 元数据
    metadata_json: Mapped[Optional[dict]] = mapped_column(
        PGJSONB if settings.db_type == "postgresql" else JSON,
        nullable=True,
        comment="元数据",
    )
    # 审计字段
    created_at: Mapped[datetime] = mapped_column(nullable=False, comment="创建时间")
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        nullable=True, comment="更新时间"
    )
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="创建人 ID"
    )
    updated_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, comment="更新人 ID"
    )

    # 关系
    price_config: Mapped[Optional["PriceConfig"]] = relationship(
        "PriceConfig", back_populates="price_bands"
    )

    __table_args__ = (
        UniqueConstraint("price_config_id", "code", name="uq_price_config_band"),
        {"comment": "价格区间表 - 定义不同数量/金额范围内的价格"},
    )

    def __repr__(self) -> str:
        return f"<PriceBand(id={self.id}, code='{self.code}', name='{self.name}')>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "price_config_id": self.price_config_id,
            "min_quantity": float(self.min_quantity) if self.min_quantity else None,
            "max_quantity": float(self.max_quantity) if self.max_quantity else None,
            "min_amount": float(self.min_amount) if self.min_amount else None,
            "max_amount": float(self.max_amount) if self.max_amount else None,
            "unit_price": float(self.unit_price) if self.unit_price else None,
            "discount_rate": float(self.discount_rate) if self.discount_rate else None,
            "final_price": float(self.final_price) if self.final_price else None,
            "priority": self.priority,
            "status": "active" if self.is_active else "disabled",
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }
