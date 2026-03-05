# 阶段 5: 批量导入导出功能

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 实现客户数据的批量导入和批量导出功能,支持 Excel 文件处理

**预计时间:** 3-5 天

**前置依赖:** 阶段 4: 客户 MDM 核心功能

**Architecture:** 
- 创建导入模板生成功能
- 实现批量导入 API(Excel 解析、数据验证、错误处理)
- 实现批量导出 API(Excel 生成)
- 创建 Excel 处理工具

**Tech Stack:**
- Excel 处理: openpyxl 3.1.2
- 文件上传: Sanic 文件处理
- 数据验证: Pydantic

---

## Task 18: 创建 Excel 处理工具

**Files:**
- Create: `backend/app/utils/excel.py`
- Create: `backend/app/tests/test_excel_utils.py`

**Step 1: 创建 Excel 工具模块**

```python
# backend/app/utils/excel.py
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List, Dict
from io import BytesIO


def generate_import_template() -> BytesIO:
    """生成导入模板"""
    wb = Workbook()
    ws = wb.active
    ws.title = "客户导入模板"
    
    # 设置表头
    headers = [
        "客户名称*",
        "客户编码",
        "行业",
        "负责销售 ID*",
        "价值等级",
        "年消费金额",
        "联系人",
        "联系电话",
        "联系邮箱",
        "地址",
        "备注"
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC")
        cell.alignment = Alignment(horizontal="center")
    
    # 设置列宽
    column_widths = [20, 15, 15, 15, 10, 15, 15, 15, 25, 40, 40]
    for col, width in enumerate(column_widths, 1):
        ws.column_dimensions[chr(64 + col)].width = width
    
    # 添加示例数据
    ws.append([
        "XX 科技公司",
        "CUST001",
        "科技",
        "1",
        "A",
        "500000.00",
        "张三",
        "13800138000",
        "zhangsan@example.com",
        "北京市朝阳区",
        "示例备注"
    ])
    
    # 保存到 BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output


def parse_import_excel(file_content: bytes) -> List[Dict]:
    """解析导入的 Excel 文件"""
    wb = load_workbook(BytesIO(file_content))
    ws = wb.active
    
    customers = []
    errors = []
    
    # 跳过表头,从第 2 行开始
    for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 2):
        if not any(row):  # 空行跳过
            continue
        
        # 解析数据
        customer_data = {
            "name": row[0] if len(row) > 0 else None,
            "code": row[1] if len(row) > 1 else None,
            "industry": row[2] if len(row) > 2 else None,
            "sales_rep_id": row[3] if len(row) > 3 else None,
            "tier_level": row[4] if len(row) > 4 else None,
            "annual_consumption": row[5] if len(row) > 5 else None,
            "contact_person": row[6] if len(row) > 6 else None,
            "contact_phone": row[7] if len(row) > 7 else None,
            "contact_email": row[8] if len(row) > 8 else None,
            "address": row[9] if len(row) > 9 else None,
            "remark": row[10] if len(row) > 10 else None
        }
        
        # 验证必填字段
        if not customer_data["name"]:
            errors.append({
                "row": row_idx,
                "field": "客户名称",
                "message": "客户名称不能为空"
            })
            continue
        
        if not customer_data["sales_rep_id"]:
            errors.append({
                "row": row_idx,
                "field": "负责销售 ID",
                "message": "负责销售 ID 不能为空"
            })
            continue
        
        customers.append({
            "data": customer_data,
            "row": row_idx
        })
    
    return {"customers": customers, "errors": errors}


def generate_export_excel(customers: List[Dict]) -> BytesIO:
    """生成导出的 Excel 文件"""
    wb = Workbook()
    ws = wb.active
    ws.title = "客户数据"
    
    # 设置表头
    headers = [
        "客户 ID",
        "客户名称",
        "客户编码",
        "行业",
        "负责销售 ID",
        "价值等级",
        "年消费金额",
        "状态",
        "联系人",
        "联系电话",
        "联系邮箱",
        "地址",
        "备注",
        "创建时间",
        "更新时间"
    ]
    
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = Font(bold=True)
        cell.fill = PatternFill(start_color="CCCCCC", end_color="CCCCCC")
        cell.alignment = Alignment(horizontal="center")
    
    # 添加客户数据
    for customer in customers:
        ws.append([
            customer.get("id"),
            customer.get("name"),
            customer.get("code"),
            customer.get("industry"),
            customer.get("sales_rep_id"),
            customer.get("tier_level"),
            customer.get("annual_consumption"),
            customer.get("status"),
            customer.get("contact_person"),
            customer.get("contact_phone"),
            customer.get("contact_email"),
            customer.get("address"),
            customer.get("remark"),
            customer.get("created_at"),
            customer.get("updated_at")
        ])
    
    # 保存到 BytesIO
    output = BytesIO()
    wb.save(output)
    output.seek(0)
    return output
```

**Step 2: 创建 Excel 工具测试**

```python
# backend/app/tests/test_excel_utils.py
import pytest
from app.utils.excel import (
    generate_import_template,
    parse_import_excel,
    generate_export_excel
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
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_excel_utils.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/utils/excel.py backend/app/tests/test_excel_utils.py
git commit -m "feat: implement Excel utility functions with tests"
```

---

## Task 19: 实现批量导入 API

**Files:**
- Modify: `backend/app/blueprints/customer.py`
- Create: `backend/app/tests/test_import_api.py`

**Step 1: 添加导入模板端点**

```python
# 在 backend/app/blueprints/customer.py 中添加
from sanic.response import raw
from app.utils.excel import generate_import_template, parse_import_excel


@customer_bp.get("/import-template")
@require_permissions("customer.view")
async def download_import_template(request: Request):
    """下载导入模板"""
    template = generate_import_template()
    
    return raw(
        template.getvalue(),
        headers={
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": "attachment; filename=客户导入模板.xlsx"
        }
    )
```

**Step 2: 添加批量导入端点**

```python
# 在 backend/app/blueprints/customer.py 中添加
from app.services.customer_service import CustomerService


@customer_bp.post("/import")
@require_permissions("customer.import")
async def import_customers(request: Request):
    """批量导入客户"""
    # 检查文件上传
    if not request.files.get("file"):
        return JSONResponse(
            {
                "error": {
                    "code": "NO_FILE",
                    "message": "请上传 Excel 文件"
                }
            },
            status=400
        )
    
    # 读取文件内容
    file = request.files.get("file")
    file_content = await file.read()
    
    # 解析 Excel 文件
    parse_result = parse_import_excel(file_content)
    
    # 检查是否有错误
    if parse_result["errors"]:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "文件中存在错误数据",
                    "details": parse_result["errors"]
                }
            },
            status=400
        )
    
    # 批量导入
    imported_count = 0
    failed_count = 0
    errors = []
    
    user = request.ctx.user
    
    async for session in get_db_session():
        for customer_item in parse_result["customers"]:
            try:
                customer_data = customer_item["data"]
                
                # 转换数据类型
                if customer_data["annual_consumption"]:
                    customer_data["annual_consumption"] = float(customer_data["annual_consumption"])
                else:
                    customer_data["annual_consumption"] = 0.0
                
                if customer_data["sales_rep_id"]:
                    customer_data["sales_rep_id"] = int(customer_data["sales_rep_id"])
                
                # 创建客户
                await CustomerService.create_customer(
                    session=session,
                    data=customer_data,
                    created_by=user["user_id"]
                )
                
                imported_count += 1
                
            except Exception as e:
                failed_count += 1
                errors.append({
                    "row": customer_item["row"],
                    "name": customer_item["data"]["name"],
                    "message": str(e)
                })
        
        await session.commit()
    
    return JSONResponse(
        {
            "data": {
                "imported_count": imported_count,
                "failed_count": failed_count,
                "errors": errors
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    )
```

**Step 3: 创建导入 API 测试**

```python
# backend/app/tests/test_import_api.py
import pytest
from sanic import Sanic
from app.blueprints.customer import customer_bp
from app.middlewares.auth import attach_auth_middleware


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    app.blueprint(customer_bp)
    return app


@pytest.mark.asyncio
async def test_download_template_without_token(app):
    """测试下载模板无 Token"""
    request, response = app.test_client.get("/api/v1/customers/import-template")
    assert response.status == 401


@pytest.mark.asyncio
async def test_download_template_with_token(app):
    """测试下载模板有效 Token"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(1, "admin", ["*"])
    
    request, response = app.test_client.get(
        "/api/v1/customers/import-template",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status == 200
    assert response.headers.get("Content-Type").startswith("application/vnd.openxmlformats")
```

**Step 4: 运行测试**

```bash
cd backend
pytest app/tests/test_import_api.py -v
```

Expected: PASS

**Step 5: Commit**

```bash
git add backend/app/blueprints/customer.py backend/app/tests/test_import_api.py
git commit -m "feat: implement batch import API with tests"
```

---

## Task 20: 实现批量导出 API

**Files:**
- Modify: `backend/app/blueprints/customer.py`
- Create: `backend/app/tests/test_export_api.py`

**Step 1: 添加批量导出端点**

```python
# 在 backend/app/blueprints/customer.py 中添加
from app.utils.excel import generate_export_excel


@customer_bp.get("/export")
@require_permissions("customer.export")
async def export_customers(request: Request):
    """批量导出客户"""
    # 解析查询参数(同列表查询)
    try:
        params = CustomerQuerySchema(**request.args)
    except Exception as e:
        return JSONResponse(
            {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": str(e)
                }
            },
            status=400
        )
    
    # 构建过滤条件(同列表查询)
    filters = {}
    if params.keyword:
        filters["keyword"] = params.keyword
    if params.sales_rep_ids:
        filters["sales_rep_ids"] = params.sales_rep_ids
    if params.industries:
        filters["industries"] = params.industries
    if params.status:
        filters["status"] = params.status
    if params.tier_levels:
        filters["tier_levels"] = params.tier_levels
    
    # 销售只能导出自己客户
    user = request.ctx.user
    if user["role"] == "sales":
        filters["sales_rep_ids"] = [user["user_id"]]
    
    # 查询所有客户(不分页)
    async for session in get_db_session():
        result = await CustomerService.list_customers(
            session=session,
            filters=filters,
            page=1,
            size=10000,  # 大数量
            order_by=["name asc"]
        )
        
        customers = result["items"]
    
    # 生成 Excel 文件
    excel_content = generate_export_excel(customers)
    
    return raw(
        excel_content.getvalue(),
        headers={
            "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "Content-Disposition": f"attachment; filename=客户数据_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        }
    )
```

**Step 2: 创建导出 API 测试**

```python
# backend/app/tests/test_export_api.py
import pytest
from sanic import Sanic
from app.blueprints.customer import customer_bp
from app.middlewares.auth import attach_auth_middleware


@pytest.fixture
def app():
    """创建测试应用"""
    app = Sanic("test_app")
    attach_auth_middleware(app)
    app.blueprint(customer_bp)
    return app


@pytest.mark.asyncio
async def test_export_without_token(app):
    """测试导出无 Token"""
    request, response = app.test_client.get("/api/v1/customers/export")
    assert response.status == 401


@pytest.mark.asyncio
async def test_export_with_token(app):
    """测试导出有效 Token"""
    from app.utils.jwt import create_access_token
    
    token = create_access_token(1, "admin", ["*"])
    
    request, response = app.test_client.get(
        "/api/v1/customers/export",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status == 200
    assert response.headers.get("Content-Type").startswith("application/vnd.openxmlformats")
```

**Step 3: 运行测试**

```bash
cd backend
pytest app/tests/test_export_api.py -v
```

Expected: PASS

**Step 4: Commit**

```bash
git add backend/app/blueprints/customer.py backend/app/tests/test_export_api.py
git commit -m "feat: implement batch export API with tests"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 5 即可视为完成:

- [ ] Excel 处理工具已实现并测试
- [ ] 导入模板生成功能已实现
- [ ] 批量导入 API 已实现并测试
- [ ] 批量导出 API 已实现并测试
- [ ] 数据验证和错误处理已实现
- [ ] 权限控制已实现(销售只能导出自己客户)
- [ ] 所有测试通过

---

## 下一步

完成阶段 5 后,请继续执行 **阶段 6: Dashboard 与前端集成**

文档: `docs/plans/2026-03-03-customer-manager-phase6-frontend.md`
