from pydantic import BaseModel, Field
from typing import Optional, List, Generic, TypeVar
from datetime import datetime


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应"""
    items: List[T]
    total: int
    page: int
    size: int
    pages: int


class ErrorResponse(BaseModel):
    """错误响应"""
    code: str
    message: str
    details: Optional[list] = None
    timestamp: str
    path: str


class SuccessResponse(BaseModel):
    """成功响应"""
    data: dict
    timestamp: str
