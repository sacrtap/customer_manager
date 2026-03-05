"""Price Config Model - 价格配置数据库模型"""

from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from app.database import Base


class PriceConfig(Base):
    """价格配置模型 - 定义产品/服务的基础价格"""

    __tablename__ = "price_configs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="代码")
    name = Column(String(200), nullable=False, comment="名称")
    description = Column(Text, nullable=True, comment="描述")
    base_price = Column(Float, nullable=False, default=0.0, comment="基准价格")
    status = Column(
        String(20), nullable=False, default="active", comment="状态 (active/disabled)"
    )

    # 审计字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    created_by = Column(
        Integer, ForeignKey("users.id"), nullable=False, comment="创建人 ID"
    )
    updated_at = Column(DateTime, onupdate=datetime.utcnow, comment="更新时间")
    updated_by = Column(
        Integer, ForeignKey("users.id"), nullable=True, comment="更新人 ID"
    )

    # 关联关系
    price_bands = relationship(
        "PriceBand",
        back_populates="price_config",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "base_price": self.base_price,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }
