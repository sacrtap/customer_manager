"""Price Config Schema - 价格配置 Pydantic 模式"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class PriceConfigBase(BaseModel):
    """价格配置基础模式"""

    code: str = Field(..., description="代码", max_length=50)
    name: str = Field(..., description="名称", max_length=200)
    description: Optional[str] = Field(None, description="描述", max_length=500)
    base_price: float = Field(..., description="基准价格", ge=0)
    status: str = Field("active", description="状态 (active/disabled)")


class PriceConfigCreateRequest(PriceConfigBase):
    """创建价格配置请求"""

    created_by: int = Field(..., description="创建人 ID")


class PriceConfigUpdateRequest(BaseModel):
    """更新价格配置请求"""

    name: Optional[str] = Field(None, description="名称", max_length=200)
    description: Optional[str] = Field(None, description="描述", max_length=500)
    base_price: Optional[float] = Field(None, description="基准价格", ge=0)
    status: Optional[str] = Field(None, description="状态 (active/disabled)")
    updated_by: Optional[int] = Field(None, description="更新人 ID")


class PriceConfigResponse(BaseModel):
    """价格配置响应"""

    id: int
    code: str
    name: str
    description: Optional[str]
    base_price: float
    status: str
    created_at: datetime
    created_by: int
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class PriceConfigQuery(BaseModel):
    """价格配置查询参数"""

    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")
    code: Optional[str] = Field(None, description="代码")
    name: Optional[str] = Field(None, description="名称")
    status: Optional[str] = Field(None, description="状态")
