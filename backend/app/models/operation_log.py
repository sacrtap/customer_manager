from sqlalchemy import BigInteger, String, DateTime, func, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column
from ..database import Base
from datetime import datetime
import json


class OperationLog(Base):
    """操作日志模型"""
    __tablename__ = "operation_logs"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False, index=True)
    operation_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    target_type: Mapped[str] = mapped_column(String(100), nullable=True)
    target_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    old_value: Mapped[dict] = mapped_column(JSON, nullable=True)
    new_value: Mapped[dict] = mapped_column(JSON, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), index=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "operation_type": self.operation_type,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "ip_address": self.ip_address,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
