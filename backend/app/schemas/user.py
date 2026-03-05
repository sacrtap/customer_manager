from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    """创建用户请求"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)
    real_name: str = Field(..., min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: str = Field("active", pattern="^(active|inactive)$")


class UserUpdateRequest(BaseModel):
    """更新用户请求"""

    real_name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=20)
    status: Optional[str] = Field(None, pattern="^(active|inactive)$")


class UserResponse(BaseModel):
    """用户响应"""

    id: int
    username: str
    real_name: str
    email: Optional[str]
    phone: Optional[str]
    status: str
    created_at: str
    updated_at: str
