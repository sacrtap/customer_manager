from pydantic import BaseModel, Field, model_validator
from typing import Optional


class TransferCreateRequest(BaseModel):
    """创建转移请求"""

    customer_id: int = Field(..., gt=0, description="客户 ID")
    to_sales_rep_id: int = Field(..., gt=0, description="转入销售 ID")
    reason: str = Field(..., min_length=1, max_length=1000, description="转移原因")

    @model_validator(mode="after")
    def validate_sales_rep_different(self):
        """验证转出和转入销售不能相同"""
        # 注意：from_sales_rep_id 在创建时从当前用户获取，不在请求体中
        # 这里只验证 to_sales_rep_id 不为空
        if self.to_sales_rep_id <= 0:
            raise ValueError("转入销售 ID 必须大于 0")
        return self


class TransferUpdateRequest(BaseModel):
    """更新转移请求"""

    reason: Optional[str] = Field(
        None, min_length=1, max_length=1000, description="转移原因"
    )


class TransferResponse(BaseModel):
    """转移响应"""

    id: int
    customer_id: int
    from_sales_rep_id: int
    to_sales_rep_id: int
    reason: str
    status: str
    approved_by: Optional[int]
    approved_at: Optional[str]
    created_by: int
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True
