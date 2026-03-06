from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class CustomerCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    sales_rep_id: int
    tier_level: Optional[str] = Field("D", pattern="^[A-D]$")
    annual_consumption: Optional[float] = Field(0, ge=0)
    status: Optional[str] = Field("active", pattern="^(active|inactive)$")
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, pattern=r"^\d{11}$")
    contact_email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    remark: Optional[str] = Field(None, max_length=1000)


class CustomerUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, max_length=50)
    industry: Optional[str] = Field(None, max_length=100)
    tier_level: Optional[str] = Field(None, pattern="^[A-D]$")
    annual_consumption: Optional[float] = Field(None, ge=0)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")
    contact_person: Optional[str] = Field(None, max_length=100)
    contact_phone: Optional[str] = Field(None, pattern=r"^\d{11}$")
    contact_email: Optional[EmailStr] = None
    address: Optional[str] = Field(None, max_length=500)
    remark: Optional[str] = Field(None, max_length=1000)


class CustomerResponse(BaseModel):
    id: int
    name: str
    code: Optional[str]
    industry: Optional[str]
    sales_rep_id: int
    tier_level: str
    annual_consumption: float
    status: str
    contact_person: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    address: Optional[str]
    remark: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
