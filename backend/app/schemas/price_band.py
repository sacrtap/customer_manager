"""Price Band Schema - 价格区间 Pydantic Schema"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class PriceBandBase(BaseModel):
    """价格区间基础 Schema"""

    name: str = Field(..., description="区间名称", max_length=100)
    code: str = Field(..., description="区间代码", max_length=50)
    description: Optional[str] = Field(None, description="描述")
    price_config_id: Optional[int] = Field(None, description="关联的价格配置 ID")

    # 区间条件
    min_quantity: Optional[Decimal] = Field(None, description="最小数量")
    max_quantity: Optional[Decimal] = Field(None, description="最大数量")
    min_amount: Optional[Decimal] = Field(None, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, description="最大金额")

    # 价格定义
    unit_price: Optional[Decimal] = Field(None, description="单价")
    discount_rate: Optional[Decimal] = Field(None, description="折扣率（百分比）")
    final_price: Optional[Decimal] = Field(None, description="最终价格")

    # 优先级和状态
    priority: int = Field(0, description="优先级")
    is_active: bool = Field(True, description="是否启用")

    # 有效期
    valid_from: Optional[datetime] = Field(None, description="生效日期")
    valid_until: Optional[datetime] = Field(None, description="失效日期")


class PriceBandCreateRequest(PriceBandBase):
    """创建价格区间请求"""

    pass


class PriceBandUpdateRequest(BaseModel):
    """更新价格区间请求"""

    name: Optional[str] = Field(None, description="区间名称", max_length=100)
    code: Optional[str] = Field(None, description="区间代码", max_length=50)
    description: Optional[str] = Field(None, description="描述")
    price_config_id: Optional[int] = Field(None, description="关联的价格配置 ID")

    # 区间条件
    min_quantity: Optional[Decimal] = Field(None, description="最小数量")
    max_quantity: Optional[Decimal] = Field(None, description="最大数量")
    min_amount: Optional[Decimal] = Field(None, description="最小金额")
    max_amount: Optional[Decimal] = Field(None, description="最大金额")

    # 价格定义
    unit_price: Optional[Decimal] = Field(None, description="单价")
    discount_rate: Optional[Decimal] = Field(None, description="折扣率（百分比）")
    final_price: Optional[Decimal] = Field(None, description="最终价格")

    # 优先级和状态
    priority: Optional[int] = Field(None, description="优先级")
    is_active: Optional[bool] = Field(None, description="是否启用")

    # 有效期
    valid_from: Optional[datetime] = Field(None, description="生效日期")
    valid_until: Optional[datetime] = Field(None, description="失效日期")


class PriceBandResponse(PriceBandBase):
    """价格区间响应"""

    id: int = Field(..., description="ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True


class PriceBandQuery(BaseModel):
    """价格区间查询参数"""

    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

    # 筛选条件
    code: Optional[str] = Field(None, description="区间代码（模糊匹配）")
    name: Optional[str] = Field(None, description="区间名称（模糊匹配）")
    price_config_id: Optional[int] = Field(None, description="价格配置 ID")
    is_active: Optional[bool] = Field(None, description="是否启用")

    # 排序
    sort_by: str = Field("priority", description="排序字段")
    sort_order: str = Field("desc", description="排序方向", pattern="^(asc|desc)$")
