from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class PricingStrategyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    applicable_customer_type: Optional[str] = Field(None, max_length=50)
    applicable_tier_levels: Optional[str] = Field(None, max_length=50)
    discount_type: str = Field("percentage", pattern="^(percentage|fixed)$")
    discount_value: float = Field(0, ge=0, le=1000000)
    priority: int = Field(0, ge=0)
    status: str = Field("active", pattern="^(active|inactive|draft)$")
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class PricingStrategyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = Field(None, max_length=1000)
    applicable_customer_type: Optional[str] = Field(None, max_length=50)
    applicable_tier_levels: Optional[str] = Field(None, max_length=50)
    discount_type: Optional[str] = Field(None, pattern="^(percentage|fixed)$")
    discount_value: Optional[float] = Field(None, ge=0, le=1000000)
    priority: Optional[int] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive|draft)$")
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class PricingStrategyResponse(BaseModel):
    id: int
    name: str
    code: str
    description: Optional[str]
    applicable_customer_type: Optional[str]
    applicable_tier_levels: Optional[str]
    discount_type: str
    discount_value: float
    priority: int
    status: str
    valid_from: Optional[datetime]
    valid_to: Optional[datetime]
    created_by: int
    updated_by: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PricingStrategyQuery(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)
    keyword: Optional[str] = None
    status: Optional[str] = None
    discount_type: Optional[str] = None
    applicable_tier_levels: Optional[str] = None
