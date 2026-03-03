# E2E测试

本目录包含客户信息管理系统的端到端（E2E）测试。

## 目录结构

- `backend/` - 后端API集成测试
- `frontend/` - 前端UI自动化测试
- `fixtures/` - 测试数据fixtures
- `helpers/` - 测试辅助工具
- `reports/` - 测试报告

## 运行测试

### 后端E2E测试

```bash
cd backend
source venv/bin/activate
pytest ../test-e2e/backend/ -v --html=../test-e2e/reports/backend-report.html
```

### 前端E2E测试

```bash
cd frontend
npx playwright test ../test-e2e/frontend/ --reporter=html --reporter=../test-e2e/reports/frontend-report
```

## 测试覆盖范围

### 后端功能
- 用户认证（登录、登出、JWT）
- RBAC权限系统
- 客户CRUD操作
- 批量导入导出
- 操作日志

### 前端功能
- 用户登录流程
- Dashboard展示
- 客户管理界面
- 批量导入导出界面
- 导航和路由

## 测试报告

测试完成后，查看生成的HTML报告：
- `reports/backend-report.html`
- `reports/frontend-report.html`
