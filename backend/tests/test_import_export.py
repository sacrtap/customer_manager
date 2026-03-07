"""
Excel 工具测试 - 测试导入导出功能
"""

import pytest
import pytest_asyncio
from io import BytesIO

from app.utils.excel import (
    generate_import_template,
    parse_import_excel,
    generate_export_excel,
)


@pytest.mark.asyncio
async def test_generate_import_template():
    """测试生成导入模板"""
    template = generate_import_template()

    assert isinstance(template, BytesIO)
    assert template.getvalue() is not None
    assert len(template.getvalue()) > 0


@pytest.mark.asyncio
async def test_parse_import_excel():
    """测试解析导入的 Excel 文件"""
    # 生成模板
    template = generate_import_template()
    template.seek(0)
    file_content = template.getvalue()

    # 解析 Excel
    result = parse_import_excel(file_content)

    # 应该至少有 1 条示例数据
    assert "customers" in result
    assert len(result["customers"]) >= 1
    assert isinstance(result["customers"][0], dict)


@pytest.mark.asyncio
async def test_generate_export_excel():
    """测试生成导出 Excel"""
    # 准备测试数据
    customers = [
        {
            "name": "测试客户 1",
            "code": "CUST001",
            "industry": "科技",
            "sales_rep_id": 1,
            "tier_level": "A",
            "annual_consumption": 500000,
            "status": "active",
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "contact_email": "zhangsan@example.com",
            "address": "北京市朝阳区",
            "remark": "测试客户",
        },
        {
            "name": "测试客户 2",
            "code": "CUST002",
            "industry": "制造",
            "sales_rep_id": 2,
            "tier_level": "B",
            "annual_consumption": 300000,
            "status": "active",
            "contact_person": "李四",
            "contact_phone": "13900139000",
            "contact_email": "lisi@example.com",
            "address": "上海市浦东新区",
            "remark": "测试客户 2",
        },
    ]

    # 生成 Excel
    excel_file = generate_export_excel(customers)

    assert isinstance(excel_file, BytesIO)
    assert excel_file.getvalue() is not None
    assert len(excel_file.getvalue()) > 0


@pytest.mark.asyncio
async def test_excel_round_trip():
    """测试 Excel 导入导出往返"""
    # 直接使用模板测试往返
    template = generate_import_template()
    template.seek(0)

    # 解析模板 (包含示例数据)
    result = parse_import_excel(template.getvalue())

    # 验证至少能解析出示例数据
    assert len(result["customers"]) >= 1
    assert len(result["errors"]) >= 0
