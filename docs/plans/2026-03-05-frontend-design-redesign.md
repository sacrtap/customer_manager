# Frontend Design Redesign 实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于 PRD 需求和 UI/UX 设计规范，使用 Arco Design 框架完成客户管理系统前端页面的设计和开发，确保与服务端 API 正确对接。

**Architecture:** 采用 Vue 3 + Composition API + TypeScript + Arco Design 组件库，Pinia 状态管理，Vue Router 路由控制。所有页面组件使用 MainLayout 布局，API 调用统一封装。

**Tech Stack:**
- Vue 3 (组合式 API)
- TypeScript 5.x
- Arco Design Vue 2.54.0
- Pinia 状态管理
- Vue Router 4.x
- Axios HTTP 客户端
- ECharts 5.5.0 (数据可视化)

---

## MVP 功能页面清单

基于 PRD 文档整理的 MVP 功能模块和对应页面：

### 模块 1：基础系统能力 (FR49-58)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 登录页 | /login | views/LoginView.vue | ✅ 已有 | POST /api/v1/auth/login | - |
| 工作台/仪表盘 | /dashboard | views/Dashboard.vue | ⚠️ 需优化 | GET /api/v1/health/dashboard | 全部 |
| 修改密码 | /change-password | views/ChangePassword.vue | ✅ 已有 | POST /api/v1/users/:id/password | 全部 |
| 个人信息 | /profile | views/Profile.vue | ✅ 已有 | GET/PUT /api/v1/users/:id | 全部 |

### 模块 2：系统管理 (RBAC 权限管理)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 用户管理 | /system/users | views/system/UserManage.vue | ⚠️ 占位符 | CRUD /api/v1/users | admin |
| 角色管理 | /system/roles | views/system/RoleManage.vue | ⚠️ 基础实现 | CRUD /api/v1/roles | admin |
| 操作日志 | /system/logs | views/system/LogView.vue | ✅ 已有 | GET /api/v1/logs | admin |
| 权限配置 | /system/permissions | views/system/PermissionConfig.vue | ❌ 待创建 | GET/PUT /api/v1/permissions | admin |

### 模块 3：客户主数据管理 (FR1-8)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 客户列表 | /customers | views/customer/CustomerList.vue | ✅ 已有 | GET/POST/PUT/DELETE /api/v1/customers | customer.view |
| 批量导入 | /customers/import | views/customer/CustomerImport.vue | ✅ 已有 | POST /api/v1/customers/import | customer.import |
| 客户详情 | /customers/:id | views/customer/CustomerDetail.vue | ❌ 待创建 | GET/PUT /api/v1/customers/:id | customer.view |
| 客户新增 | /customers/new | views/customer/CustomerForm.vue | ❌ 待创建 | POST /api/v1/customers | customer.create |
| 客户编辑 | /customers/:id/edit | views/customer/CustomerForm.vue | ❌ 待创建 | PUT /api/v1/customers/:id | customer.edit |

### 模块 3：客户健康度监控 (FR9-16)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 健康度仪表盘 | /health/dashboard | views/health/Dashboard.vue | ❌ 待创建 | GET /api/v1/health/dashboard | manager |
| 风险客户列表 | /health/risks | views/health/RiskList.vue | ❌ 待创建 | GET /api/v1/health/risks | manager |
| 僵尸客户列表 | /health/zombies | views/health/ZombieList.vue | ❌ 待创建 | GET /api/v1/health/zombies | manager |

### 模块 4：客户价值评估 (FR17-22)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 价值等级配置 | /tiers/config | views/tier/TierConfig.vue | ❌ 待创建 | GET/PUT /api/v1/tiers/config | admin, manager |
| 定级历史 | /tiers/history | views/tier/TierHistory.vue | ❌ 待创建 | GET /api/v1/tiers/history | manager |

### 模块 5：定价管理 (MVP 核心)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 价格区间列表 | /pricing/bands | views/pricing/PriceBandList.vue | ✅ 已有 | CRUD /api/v1/price-bands | pricing.view |
| 定价策略列表 | /pricing/strategies | views/pricing/PricingStrategyList.vue | ❌ 待创建 | CRUD /api/v1/pricing-strategies | pricing.view |
| 价格配置列表 | /pricing/configs | views/pricing/PricingConfigList.vue | ❌ 待创建 | CRUD /api/v1/price-configs | pricing.view |
| 客户结算模式配置 | /customers/:id/pricing | views/customer/CustomerPricing.vue | ❌ 待创建 | GET/PUT /api/v1/customers/:id/pricing | pricing.edit |

### 模块 6：结算管理 (FR23-32)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 结算单生成 | /billing/generate | views/billing/Generate.vue | ❌ 待创建 | POST /api/v1/billing/generate | billing.create |
| 结算单列表 | /billing/list | views/billing/BillingList.vue | ❌ 待创建 | GET /api/v1/billing | billing.view |
| 结算单详情 | /billing/:id | views/billing/BillingDetail.vue | ❌ 待创建 | GET /api/v1/billing/:id | billing.view |
| 异常数据处理 | /billing/exceptions | views/billing/ExceptionList.vue | ❌ 待创建 | GET/PUT /api/v1/billing/exceptions | billing.edit |

### 模块 7：客户转移 (FR33-40)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 客户转移 | /transfers/new | views/transfer/TransferCreate.vue | ❌ 待创建 | POST /api/v1/transfers | transfer.create |
| 转移历史 | /transfers/history | views/transfer/TransferHistory.vue | ❌ 待创建 | GET /api/v1/transfers | transfer.view |

### 模块 2：系统管理 - RBAC 权限管理 (FR49-58) - Phase 2 (P0)

| 页面名称 | 路由 | 组件路径 | 状态 | API 端点 | 权限 |
|----------|------|----------|------|----------|------|
| 用户管理 | /system/users | views/system/UserManage.vue | ⚠️ 占位符 | CRUD /api/v1/users | admin |
| 角色管理 | /system/roles | views/system/RoleManage.vue | ⚠️ 基础实现 | CRUD /api/v1/roles | admin |
| 操作日志 | /system/logs | views/system/LogView.vue | ✅ 已有 | GET /api/v1/logs | admin |
| 权限配置 | /system/permissions | views/system/PermissionConfig.vue | ❌ 待创建 | GET/PUT /api/v1/permissions | admin |

**RBAC 功能说明：**
- 后端 API 已完整：用户 CRUD、角色 CRUD、权限分配
- 前端需完善：用户管理页面（目前仅占位符）、角色权限配置界面优化
- 权限点已预定义：customer.*, pricing.*, billing.*, system.*, * (通配符)

---

## 后端 API 接口清单

基于后端 blueprints 整理的 API 端点：

### Auth (认证)
```
POST   /api/v1/auth/login         # 用户登录
POST   /api/v1/auth/logout        # 用户登出
GET    /api/v1/auth/me            # 获取当前用户信息
```

### Customer (客户管理)
```
GET    /api/v1/customers          # 客户列表（分页、筛选）
POST   /api/v1/customers          # 新增客户
GET    /api/v1/customers/:id      # 客户详情
PUT    /api/v1/customers/:id      # 更新客户
DELETE /api/v1/customers/:id      # 删除客户
POST   /api/v1/customers/import   # 批量导入
GET    /api/v1/customers/export   # 批量导出
```

### Health (健康度监控)
```
GET    /api/v1/health/dashboard   # 健康度仪表盘数据
GET    /api/v1/health/risks       # 风险客户列表
GET    /api/v1/health/zombies     # 僵尸客户列表
POST   /api/v1/health/alerts      # 发送预警通知
```

### Pricing (定价管理)
```
# 价格配置
GET    /api/v1/price-configs      # 价格配置列表
POST   /api/v1/price-configs      # 新增价格配置
GET    /api/v1/price-configs/:id  # 价格配置详情
PUT    /api/v1/price-configs/:id  # 更新价格配置
DELETE /api/v1/price-configs/:id  # 删除价格配置

# 价格区间
GET    /api/v1/price-bands        # 价格区间列表
POST   /api/v1/price-bands        # 新增价格区间
GET    /api/v1/price-bands/:id    # 价格区间详情
PUT    /api/v1/price-bands/:id    # 更新价格区间
DELETE /api/v1/price-bands/:id    # 删除价格区间

# 定价策略
GET    /api/v1/pricing-strategies     # 定价策略列表
POST   /api/v1/pricing-strategies     # 新增定价策略
GET    /api/v1/pricing-strategies/:id # 定价策略详情
PUT    /api/v1/pricing-strategies/:id # 更新定价策略
DELETE /api/v1/pricing-strategies/:id # 删除定价策略
```

### System (系统管理)
```
# 用户管理
GET    /api/v1/users              # 用户列表
POST   /api/v1/users              # 新增用户
GET    /api/v1/users/:id          # 用户详情
PUT    /api/v1/users/:id          # 更新用户
DELETE /api/v1/users/:id          # 删除用户
POST   /api/v1/users/:id/password # 修改密码

# 角色管理
GET    /api/v1/roles              # 角色列表
POST   /api/v1/roles              # 新增角色
PUT    /api/v1/roles/:id          # 更新角色
DELETE /api/v1/roles/:id          # 删除角色
GET    /api/v1/role-permissions   # 角色权限列表
POST   /api/v1/role-permissions   # 分配角色权限

# 操作日志
GET    /api/v1/logs               # 操作日志列表
GET    /api/v1/logs/:id           # 操作日志详情
```

---

## 实施阶段划分

### Phase 1: 核心页面优化 (优先级 P0)

**目标：** 完成登录页和仪表盘页面的优化，确保与设计规范一致

**任务：**
1. Task 1: 登录页面优化 (LoginView.vue)
2. Task 2: 仪表盘页面优化 (Dashboard.vue)
3. Task 3: 主布局组件优化 (MainLayout.vue)

### Phase 2: 系统管理页面 (优先级 P0) - RBAC 权限管理

**目标：** 完成系统管理模块的所有页面，实现完整的 RBAC 权限管理功能

**任务：**
4. Task 4: 用户管理页面完整实现 (UserManage.vue) - 含用户 CRUD、角色分配
5. Task 5: 角色权限管理优化 (RoleManage.vue) - 完善权限配置界面
6. Task 6: 操作日志页面优化 (LogView.vue)

**RBAC 功能确认：**
- ✅ 后端 API 已完整：角色 CRUD、权限分配、用户管理
- ⚠️ 前端需完善：用户管理页面 (目前仅占位符)、角色权限配置界面

### Phase 3: 客户管理页面 (优先级 P0)

**目标：** 完成客户管理模块的所有页面

**任务：**
7. Task 7: 客户列表页面优化 (CustomerList.vue)
8. Task 8: 客户详情页面 (CustomerDetail.vue)
9. Task 9: 客户表单组件 (CustomerForm.vue) - 新增/编辑共用
10. Task 10: 客户导入页面优化 (CustomerImport.vue)

### Phase 4: 健康度监控页面 (优先级 P1)

**目标：** 完成健康度监控模块

**任务：**
11. Task 11: 健康度仪表盘 (HealthDashboard.vue)
12. Task 12: 风险客户列表 (RiskList.vue)
13. Task 13: 僵尸客户列表 (ZombieList.vue)

### Phase 5: 定价管理页面 (优先级 P1)

**目标：** 完成定价管理模块

**任务：**
14. Task 14: 定价策略列表 (PricingStrategyList.vue)
15. Task 15: 价格配置列表 (PricingConfigList.vue)
16. Task 16: 价格区间列表优化 (PriceBandList.vue)
17. Task 17: 客户结算模式配置 (CustomerPricing.vue)

### Phase 6: 结算管理页面 (优先级 P1)

**目标：** 完成结算管理模块

**任务：**
18. Task 18: 结算单生成 (GenerateBilling.vue)
19. Task 19: 结算单列表 (BillingList.vue)
20. Task 20: 结算单详情 (BillingDetail.vue)
21. Task 21: 异常数据处理 (ExceptionList.vue)

### Phase 7: 客户转移页面 (优先级 P2)

**目标：** 完成客户转移模块

**任务：**
22. Task 22: 客户转移创建 (TransferCreate.vue)
23. Task 23: 转移历史记录 (TransferHistory.vue)

---

## 设计规范参考

所有页面开发需遵循 `docs/prd.md` 中的 UI/UX Design System 规范：

### 色彩系统
- 主色：#165DFF (Arco Blue)
- 成功：#00B42A
- 警告：#FF7D00
- 错误：#F53F3F

### 客户状态色
- 活跃：#00B42A (绿色)
- 风险：#FF7D00 (橙色)
- 僵尸：#F53F3F (红色)

### 客户等级色
- S 级：#F53F3F (红色)
- A 级：#FF7D00 (橙色)
- B 级：#FADC19 (黄色)
- C 级：#14C9C9 (青色)
- D 级：#86909C (灰色)

### 组件规范
- 按钮高度：32px(小) / 36px(中) / 44px(大)
- 输入框高度：36px(默认) / 44px(大)
- 卡片圆角：8px
- 表格行高：48px

---

## 测试规范

遵循 AGENTS.md 中的测试开发规则：

### E2E 测试规则
1. 选择器必须精确唯一（使用 data-testid）
2. Arco Design 错误消息类名需区分场景
3. 图标导入必须验证存在性
4. Mock API 路径必须完整匹配
5. 表单测试数据需满足验证规则

### 测试文件命名
- 测试文件：`tests/e2e/<feature>.spec.ts`
- 测试描述：`describe('<FeatureName>', () => {})`
- 测试用例：`it('应该 <expected behavior>', async () => {})`

---

## 提交规范

### Commit Message 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 类型
- `feat`: 新功能
- `fix`: Bug 修复
- `style`: 代码格式（不影响代码运行）
- `refactor`: 重构（既不是新功能也不是 bug 修复）
- `test`: 添加或修改测试
- `docs`: 文档变更
- `chore`: 构建过程或辅助工具变动

### 示例
```
feat(dashboard): 实现健康度仪表盘页面
- 添加 4 个统计卡片组件
- 集成 ECharts 趋势图表
- 添加风险客户预警列表

refactor(login): 优化登录页面样式
- 使用 Arco Design 组件
- 改进响应式布局
```

---

## 开发检查清单

每个页面开发完成后需检查：

- [ ] 组件使用 Composition API 语法
- [ ] TypeScript 类型定义完整
- [ ] 使用 Arco Design 组件库
- [ ] 响应式设计（支持桌面/平板/手机）
- [ ] 权限控制正确实现
- [ ] API 调用错误处理
- [ ] 加载状态处理
- [ ] 表单验证规则
- [ ] 符合设计规范（色彩/间距/圆角）
- [ ] E2E 测试通过

---

## 设计风格确认

✅ **原型设计已完成** - `theme/login-preview.html` 和 `theme/dashboard-preview.html` 已创建并确认

### 设计方案：混合风格

**登录页面：** 经典商务风格
- 左 - 右分屏布局
- 左侧品牌展示区：渐变背景 (#165DFF)、玻璃态统计卡片
- 右侧登录表单：简洁表单、Arco Design 组件
- 测试账号快捷入口（4种角色一键切换）

**仪表盘页面：** 数据驱动风格
- 深色侧边栏导航 (#1D2129 到 #0A0C10 渐变)
- 顶部欢迎横幅（个性化问候 + 关键指标）
- 主内容区：4 个统计卡片 + ECharts图表 + 列表
- 客户健康度专用色：活跃 (绿)/风险 (橙)/僵尸 (红)
- 完整导航菜单：8个主模块，含子菜单和徽章提示

### 设计规范速查

**色彩系统：**
```
主色：#165DFF (Arco Blue)
成功：#00B42A
警告：#FF7D00
错误：#F53F3F
```

**客户状态色：**
```
活跃：#00B42A (绿色)
风险：#FF7D00 (橙色)
僵尸：#F53F3F (红色)
```

**客户等级色：**
```
S 级：#F53F3F (红色)
A 级：#FF7D00 (橙色)
B 级：#FADC19 (黄色)
C 级：#14C9C9 (青色)
D 级：#86909C (灰色)
```

**组件尺寸：**
```
按钮高度：36px(默认)
输入框：44px(大)
卡片圆角：8px
表格行高：48px
```

### 参考原型文件

- `theme/login-preview.html` - 登录页高保真原型
- `theme/dashboard-preview.html` - 仪表盘高保真原型

---

*文档版本：v1.2*
*创建日期：2026-03-05*
*最后更新：2026-03-06*
*所在分支：feature/frontend-design-redesign*
*系统管理模块已调整为 Phase 2 (P0) 优先级*
*✅ 登录页和 Dashboard 页 HTML 原型已完成*
