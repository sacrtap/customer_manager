from datetime import datetime

import pytest

from app.models.operation_log import OperationLog


@pytest.mark.asyncio
async def test_create_operation_log(test_session):
    """测试创建操作日志"""
    log = OperationLog(
        user_id=1,
        operation_type="customer.create",
        target_type="customer",
        target_id=100,
        new_value={"name": "测试客户"},
        ip_address="192.168.1.1",
    )
    test_session.add(log)
    await test_session.commit()
    await test_session.refresh(log)

    assert log.id is not None
    assert log.operation_type == "customer.create"
    assert log.target_id == 100
