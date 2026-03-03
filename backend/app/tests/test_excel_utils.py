# backend/app/tests/test_excel_utils.py
import pytest
from app.utils.excel import (
    generate_import_template,
    parse_import_excel,
    generate_export_excel,
)


def test_generate_import_template():
    """测试生成导入模板"""
    output = generate_import_template()
    assert output is not None
    assert len(output.getvalue()) > 0


def test_parse_import_excel_valid():
    """测试解析有效的 Excel 文件"""
    # 创建测试 Excel 文件
    from openpyxl import Workbook
    from io import BytesIO

    wb = Workbook()
    ws = wb.active
    ws.append(["客户名称", "客户编码", "行业", "负责销售 ID"])
    ws.append(["测试客户", "CUST001", "科技", "1"])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    # 解析
    result = parse_import_excel(output.getvalue())

    assert "customers" in result
    assert "errors" in result
    assert len(result["customers"]) == 1
    assert result["customers"][0]["data"]["name"] == "测试客户"


def test_parse_import_excel_empty_name():
    """测试解析空客户名称"""
    from openpyxl import Workbook
    from io import BytesIO

    wb = Workbook()
    ws = wb.active
    ws.append(["客户名称", "客户编码", "行业", "负责销售 ID"])
    ws.append(["", "CUST001", "科技", "1"])  # 客户名称为空

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    result = parse_import_excel(output.getvalue())

    assert len(result["errors"]) == 1
    assert result["errors"][0]["field"] == "客户名称"


def test_generate_export_excel():
    """测试生成导出 Excel"""
    customers = [
        {
            "id": 1,
            "name": "测试客户",
            "code": "CUST001",
            "industry": "科技",
            "sales_rep_id": 1,
            "tier_level": "A",
            "annual_consumption": 500000.00,
            "status": "active",
            "contact_person": "张三",
            "contact_phone": "13800138000",
            "contact_email": "zhangsan@example.com",
            "address": "北京市朝阳区",
            "remark": "备注",
            "created_at": "2026-03-03T00:00:00",
            "updated_at": "2026-03-03T00:00:00",
        }
    ]

    output = generate_export_excel(customers)
    assert output is not None
    assert len(output.getvalue()) > 0
