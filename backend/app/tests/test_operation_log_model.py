from datetime import datetime

import pytest

from app.database import async_session_maker
from app.models.operation_log import OperationLog


@pytest.mark.asyncio
async def test_create_operation_log():
    """测试创建操作日志"""
    async with async_session_maker() as session:
        log = OperationLog(
            user_id=1,
            operation_type="customer.create",
            target_type="customer",
            target_id=100,
            new_value={"name": "测试客户"},
            ip_address="192.168.1.1",
        )
        session.add(log)
        await session.commit()
        await session.refresh(log)

        assert log.id is not None
        assert log.operation_type == "customer.create"
        assert log.target_id == 100
