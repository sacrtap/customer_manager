from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """登录请求"""

    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=100)


class LoginResponse(BaseModel):
    """登录响应"""

    token: str
    user: dict
    permissions: list


class RefreshTokenRequest(BaseModel):
    """刷新 Token 请求"""

    refresh_token: str
