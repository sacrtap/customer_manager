# MVP 前端页面重构实施计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 基于 HTML 原型设计和现有代码结构，完成 MVP 所有前端页面的重构，确保与设计规范一致并正确对接后端 API。

**Architecture:** 在现有 Vue 3 + TypeScript + Arco Design 代码基础上，按照 `theme/login-preview.html` 和 `theme/dashboard-preview.html` 的设计风格重构所有页面，保持现有 API 封装和路由结构不变。

**Tech Stack:**
- Vue 3 (组合式 API)
- TypeScript 5.x
- Arco Design Vue 2.54.0
- Pinia 状态管理
- Vue Router 4.x
- Axios HTTP 客户端
- ECharts 5.5.0 (数据可视化)

---

## 工作区信息

**Worktree 位置**: `.worktrees/frontend-redesign`

**分支**: `feature/frontend-redesign`

**重要提示**: 所有开发工作必须在此 worktree 中进行，使用 `workdir` 参数指定正确目录。

---

## Phase 1: 核心页面优化 (P0)

### Task 1: 登录页面样式优化 (LoginView.vue)

**目标**: 按照 `theme/login-preview.html` 的设计更新登录页面样式

**Files:**
- Modify: `frontend/src/views/LoginView.vue`

**Step 1: 分析当前代码与原型差异**
- 对比现有 LoginView.vue 和 theme/login-preview.html
- 确认需要调整的样式细节（颜色、间距、布局）

**Step 2: 更新样式以匹配原型**
```vue
// 更新 .brand-section 背景渐变
background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);

// 更新按钮样式
background: #165DFF;
height: 44px;

// 确保左侧品牌展示区包含玻璃态统计卡片
```

**Step 3: 验证页面渲染**
```bash
cd frontend
npm run dev
# 在浏览器中访问 http://localhost:5173/login
# 验证样式与原型一致
```

**Step 4: 运行 E2E 测试**
```bash
cd frontend
npx playwright test tests/e2e/login/login.spec.ts
# 确保登录功能正常
```

**Step 5: 提交**
```bash
git add frontend/src/views/LoginView.vue
git commit -m "style(login): 优化登录页面样式以匹配设计规范"
```

---

### Task 2: 仪表盘页面优化 (Dashboard.vue)

**目标**: 按照 `theme/dashboard-preview.html` 的设计更新仪表盘页面

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

**Step 1: 分析当前代码与原型差异**
- 对比现有 Dashboard.vue 和 theme/dashboard-preview.html
- 确认需要调整的样式细节

**Step 2: 更新欢迎横幅样式**
```vue
// 更新背景渐变
background: linear-gradient(135deg, #165DFF 0%, #0E42D2 100%);

// 更新横幅布局，使用 flex 左右布局
display: flex;
justify-content: space-between;
align-items: center;
```

**Step 3: 更新统计卡片样式**
```vue
// 添加卡片边框
border: 1px solid #E5E6EB;

// 更新图标背景为渐变
background: linear-gradient(135deg, rgba(22,93,255,0.1) 0%, rgba(22,93,255,0.05) 100%);
```

**Step 4: 验证页面渲染**
```bash
npm run dev
# 访问 http://localhost:5173/dashboard 验证样式
```

**Step 5: 运行 E2E 测试**
```bash
npx playwright test tests/e2e/dashboard/dashboard.spec.ts
```

**Step 6: 提交**
```bash
git add frontend/src/views/Dashboard.vue
git commit -m "style(dashboard): 优化仪表盘页面样式以匹配设计规范"
```

---

### Task 3: 主布局组件优化 (MainLayout.vue)

**目标**: 按照原型设计优化侧边栏和顶部导航样式

**Files:**
- Modify: `frontend/src/layouts/MainLayout.vue`

**Step 1: 更新侧边栏样式**
```vue
// 侧边栏背景渐变
background: linear-gradient(180deg, #1D2129 0%, #0A0C10 100%);

// 更新 Logo 区域样式
padding: 24px 20px;
```

**Step 2: 优化导航菜单样式**
```vue
// 菜单项选中状态
background: linear-gradient(90deg, #165DFF 0%, #0E42D2 100%);

// 添加子菜单支持
```

**Step 3: 添加用户信息区域**
```vue
// 在侧边栏底部添加用户信息卡片
<div class="user-info">
  <div class="user-avatar">{{ userInfo.real_name?.charAt(0) }}</div>
  <div class="user-details">
    <div class="user-name">{{ userInfo.real_name }}</div>
    <div class="user-role">{{ userInfo.role }}</div>
  </div>
</div>
```

**Step 4: 验证布局渲染**
```bash
npm run dev
# 访问任意页面验证主布局样式
```

**Step 5: 提交**
```bash
git add frontend/src/layouts/MainLayout.vue
git commit -m "style(layout): 优化主布局组件样式以匹配设计规范"
```

---

## Phase 2: 系统管理页面 (P0)

### Task 4: 用户管理页面完整实现 (UserManage.vue)

**目标**: 从占位符升级为完整的用户 CRUD 页面

**Files:**
- Modify: `frontend/src/views/system/UserManage.vue`
- API: `frontend/src/api/user.ts` (已有)

**Step 1: 查看当前占位符实现**
```bash
cat frontend/src/views/system/UserManage.vue
```

**Step 2: 实现用户列表展示**
```vue
<template>
  <div class="user-manage">
    <a-card title="用户管理">
      <template #extra>
        <a-button type="primary" @click="showCreateModal">
          <icon-plus />
          新增用户
        </a-button>
      </template>
      
      <a-table :columns="columns" :data="userList" :loading="loading">
        <template #status="{ record }">
          <a-tag :color="record.status === 'active' ? 'green' : 'red'">
            {{ record.status === 'active' ? '启用' : '禁用' }}
          </a-tag>
        </template>
        <template #action="{ record }">
          <a-space>
            <a-button type="text" size="mini" @click="editUser(record)">编辑</a-button>
            <a-button type="text" size="mini" status="danger" @click="deleteUser(record)">删除</a-button>
          </a-space>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/user'
import type { User } from '@/types/user'

const loading = ref(false)
const userList = ref<User[]>([])

const columns = [
  { title: '用户名', dataIndex: 'username', width: 120 },
  { title: '姓名', dataIndex: 'real_name', width: 120 },
  { title: '角色', dataIndex: 'role', width: 100 },
  { title: '邮箱', dataIndex: 'email' },
  { title: '状态', dataIndex: 'status', slotName: 'status', width: 80 },
  { title: '操作', slotName: 'action', width: 150 }
]

const loadUsers = async () => {
  loading.value = true
  try {
    userList.value = await userApi.getList()
  } finally {
    loading.value = false
  }
}

const showCreateModal = () => { /* 实现 */ }
const editUser = (user: User) => { /* 实现 */ }
const deleteUser = (user: User) => { /* 实现 */ }

onMounted(() => loadUsers())
</script>
```

**Step 3: 实现新增/编辑用户模态框**

**Step 4: 对接后端 API**
```typescript
// 使用已有的 userApi
// GET /api/v1/users - 列表
// POST /api/v1/users - 创建
// PUT /api/v1/users/:id - 更新
// DELETE /api/v1/users/:id - 删除
```

**Step 5: 验证功能**
```bash
npm run dev
# 访问 /system/users 验证 CRUD 功能
```

**Step 6: 提交**
```bash
git add frontend/src/views/system/UserManage.vue
git commit -m "feat(user-manage): 完整实现用户管理页面 CRUD 功能"
```

---

### Task 5: 角色管理页面优化 (RoleManage.vue)

**目标**: 完善角色权限配置界面

**Files:**
- Modify: `frontend/src/views/system/RoleManage.vue`
- API: `frontend/src/api/role.ts` (已有)

**Step 1: 查看当前实现**
```bash
cat frontend/src/views/system/RoleManage.vue
```

**Step 2: 优化角色列表展示**

**Step 3: 实现权限分配界面**
```vue
// 使用树形组件展示权限
<a-tree
  v-model:checked-keys="checkedPermissions"
  :data="permissionTree"
  checkable
/>
```

**Step 4: 对接后端 API**
```typescript
// GET /api/v1/roles - 角色列表
// POST /api/v1/roles - 创建角色
// PUT /api/v1/roles/:id - 更新角色
// DELETE /api/v1/roles/:id - 删除角色
// GET /api/v1/role-permissions - 获取角色权限
// POST /api/v1/role-permissions - 分配角色权限
```

**Step 5: 验证功能**
```bash
npm run dev
# 访问 /system/roles 验证功能
```

**Step 6: 提交**
```bash
git add frontend/src/views/system/RoleManage.vue
git commit -m "feat(role-manage): 完善角色权限管理界面"
```

---

### Task 6: 操作日志页面优化 (LogView.vue)

**目标**: 优化操作日志页面展示

**Files:**
- Modify: `frontend/src/views/system/LogView.vue`
- API: `frontend/src/api/log.ts` (已有)

**Step 1: 查看当前实现**

**Step 2: 优化日志列表展示**
- 添加筛选功能（按操作类型、时间范围）
- 优化表格列展示

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/system/LogView.vue
git commit -m "style(log-view): 优化操作日志页面展示"
```

---

## Phase 3: 客户管理页面 (P0)

### Task 7: 客户列表页面优化 (CustomerList.vue)

**Files:**
- Modify: `frontend/src/views/customer/CustomerList.vue`
- API: `frontend/src/api/customer.ts` (已有)

**Step 1: 优化统计卡片样式**
```vue
// 按照设计规范更新统计卡片
border: 1px solid #E5E6EB;
border-radius: 12px;
```

**Step 2: 优化表格展示**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/customer/CustomerList.vue
git commit -m "style(customer-list): 优化客户列表页面样式"
```

---

### Task 8: 客户详情页面创建 (CustomerDetail.vue)

**Files:**
- Create: `frontend/src/views/customer/CustomerDetail.vue`
- API: `frontend/src/api/customer.ts` (已有)

**Step 1: 创建客户详情页面**
```vue
<template>
  <div class="customer-detail">
    <a-page-header :back-icon="icon-arrow-left" @back="router.back()">
      <template #title>客户详情</template>
    </a-page-header>
    
    <!-- 客户基本信息卡片 -->
    <a-card title="基本信息" :style="{ marginTop: '24px' }">
      <!-- 客户信息展示 -->
    </a-card>
    
    <!-- 健康度信息 -->
    <a-card title="健康度状态" :style="{ marginTop: '24px' }">
      <!-- 健康度展示 -->
    </a-card>
    
    <!-- 价值等级信息 -->
    <a-card title="价值等级" :style="{ marginTop: '24px' }">
      <!-- 等级信息展示 -->
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { customerApi } from '@/api/customer'
import type { Customer } from '@/types/customer'

const route = useRoute()
const router = useRouter()
const customer = ref<Customer | null>(null)
const loading = ref(false)

const loadCustomer = async () => {
  loading.value = true
  try {
    customer.value = await customerApi.getDetail(route.params.id as string)
  } finally {
    loading.value = false
  }
}

onMounted(() => loadCustomer())
</script>
```

**Step 2: 添加路由配置**
```typescript
// 在 router/index.ts 中添加
{
  path: '/customers/:id',
  name: 'CustomerDetail',
  component: () => import('@/views/customer/CustomerDetail.vue'),
  meta: { title: '客户详情', requiresAuth: true }
}
```

**Step 3: 验证功能**
```bash
npm run dev
# 访问 /customers/1 验证详情页面
```

**Step 4: 提交**
```bash
git add frontend/src/views/customer/CustomerDetail.vue
git add frontend/src/router/index.ts
git commit -m "feat(customer-detail): 创建客户详情页面"
```

---

### Task 9: 客户表单组件创建/优化 (CustomerForm.vue)

**Files:**
- Modify/Create: `frontend/src/views/customer/CustomerForm.vue`
- API: `frontend/src/api/customer.ts` (已有)

**Step 1: 创建/优化客户表单**
- 支持新增和编辑共用
- 完整的表单验证

**Step 2: 添加路由配置**
```typescript
// 新增客户
{ path: '/customers/new', name: 'CustomerCreate', component: () => import('@/views/customer/CustomerForm.vue') }

// 编辑客户
{ path: '/customers/:id/edit', name: 'CustomerEdit', component: () => import('@/views/customer/CustomerForm.vue') }
```

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/customer/CustomerForm.vue
git add frontend/src/router/index.ts
git commit -m "feat(customer-form): 创建客户表单组件(新增/编辑共用)"
```

---

### Task 10: 客户导入页面优化 (CustomerImport.vue)

**Files:**
- Modify: `frontend/src/views/customer/CustomerImport.vue`
- API: `frontend/src/api/customer.ts` (已有)

**Step 1: 优化页面样式**

**Step 2: 验证功能**

**Step 3: 提交**
```bash
git add frontend/src/views/customer/CustomerImport.vue
git commit -m "style(customer-import): 优化客户导入页面样式"
```

---

## Phase 4: 健康度监控页面 (P1)

### Task 11: 健康度仪表盘创建 (HealthDashboard.vue)

**Files:**
- Create: `frontend/src/views/health/Dashboard.vue`
- API: `frontend/src/api/health.ts` (已有)

**Step 1: 创建健康度仪表盘页面**
```vue
<template>
  <div class="health-dashboard">
    <!-- 欢迎横幅 -->
    <div class="welcome-banner">
      <!-- 与 Dashboard.vue 类似 -->
    </div>
    
    <!-- 统计卡片 -->
    <div class="stats-grid">
      <!-- 健康度相关统计 -->
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-grid">
      <!-- ECharts 趋势图 -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { healthApi } from '@/api/health'
import * as echarts from 'echarts'

const loadDashboardData = async () => {
  const data = await healthApi.getDashboard()
  // 渲染图表
}

onMounted(() => loadDashboardData())
</script>
```

**Step 2: 添加路由配置**
```typescript
{
  path: '/health/dashboard',
  name: 'HealthDashboard',
  component: () => import('@/views/health/Dashboard.vue'),
  meta: { title: '健康度仪表盘', requiresAuth: true, permissions: ['health.view'] }
}
```

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/health/Dashboard.vue
git add frontend/src/router/index.ts
git commit -m "feat(health-dashboard): 创建健康度仪表盘页面"
```

---

### Task 12: 风险客户列表创建 (RiskList.vue)

**Files:**
- Create: `frontend/src/views/health/RiskList.vue`
- API: `frontend/src/api/health.ts` (已有)

**Step 1: 创建风险客户列表页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/health/RiskList.vue
git add frontend/src/router/index.ts
git commit -m "feat(risk-list): 创建风险客户列表页面"
```

---

### Task 13: 僵尸客户列表创建 (ZombieList.vue)

**Files:**
- Create: `frontend/src/views/health/ZombieList.vue`
- API: `frontend/src/api/health.ts` (已有)

**Step 1: 创建僵尸客户列表页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/health/ZombieList.vue
git add frontend/src/router/index.ts
git commit -m "feat(zombie-list): 创建僵尸客户列表页面"
```

---

## Phase 5: 定价管理页面 (P1)

### Task 14: 定价策略列表创建 (PricingStrategyList.vue)

**Files:**
- Create: `frontend/src/views/pricing/PricingStrategyList.vue`
- API: `frontend/src/api/pricing-strategy.ts` (已有)

**Step 1: 创建定价策略列表页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/pricing/PricingStrategyList.vue
git add frontend/src/router/index.ts
git commit -m "feat(pricing-strategy): 创建定价策略列表页面"
```

---

### Task 15: 价格配置列表创建 (PricingConfigList.vue)

**Files:**
- Create: `frontend/src/views/pricing/PricingConfigList.vue`
- API: `frontend/src/api/index.ts` (需确认)

**Step 1: 创建价格配置列表页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/pricing/PricingConfigList.vue
git add frontend/src/router/index.ts
git commit -m "feat(pricing-config): 创建价格配置列表页面"
```

---

### Task 16: 价格区间列表优化 (PriceBandList.vue)

**Files:**
- Modify: `frontend/src/views/pricing/PriceBandList.vue`
- API: `frontend/src/api/price-band.ts` (已有)

**Step 1: 优化页面样式**

**Step 2: 验证功能**

**Step 3: 提交**
```bash
git add frontend/src/views/pricing/PriceBandList.vue
git commit -m "style(price-band): 优化价格区间列表页面样式"
```

---

### Task 17: 客户结算模式配置创建 (CustomerPricing.vue)

**Files:**
- Create: `frontend/src/views/customer/CustomerPricing.vue`
- API: 需确认

**Step 1: 创建客户结算模式配置页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/customer/CustomerPricing.vue
git add frontend/src/router/index.ts
git commit -m "feat(customer-pricing): 创建客户结算模式配置页面"
```

---

## Phase 6: 结算管理页面 (P1)

### Task 18: 结算单生成创建 (Generate.vue)

**Files:**
- Create: `frontend/src/views/billing/Generate.vue`
- API: `frontend/src/api/billing.ts` (已有)

**Step 1: 创建结算单生成页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/billing/Generate.vue
git add frontend/src/router/index.ts
git commit -m "feat(billing-generate): 创建结算单生成页面"
```

---

### Task 19: 结算单列表创建 (BillingList.vue)

**Files:**
- Create: `frontend/src/views/billing/BillingList.vue`
- API: `frontend/src/api/billing.ts` (已有)

**Step 1: 创建结算单列表页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/billing/BillingList.vue
git add frontend/src/router/index.ts
git commit -m "feat(billing-list): 创建结算单列表页面"
```

---

### Task 20: 结算单详情创建 (BillingDetail.vue)

**Files:**
- Create: `frontend/src/views/billing/BillingDetail.vue`
- API: `frontend/src/api/billing.ts` (已有)

**Step 1: 创建结算单详情页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/billing/BillingDetail.vue
git add frontend/src/router/index.ts
git commit -m "feat(billing-detail): 创建结算单详情页面"
```

---

### Task 21: 异常数据处理创建 (ExceptionList.vue)

**Files:**
- Create: `frontend/src/views/billing/ExceptionList.vue`
- API: `frontend/src/api/billing.ts` (已有)

**Step 1: 创建异常数据处理页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/billing/ExceptionList.vue
git add frontend/src/router/index.ts
git commit -m "feat(billing-exception): 创建异常数据处理页面"
```

---

## Phase 7: 客户转移页面 (P2)

### Task 22: 客户转移创建 (TransferCreate.vue)

**Files:**
- Create: `frontend/src/views/transfer/TransferCreate.vue`
- API: `frontend/src/api/transfer.ts` (已有)

**Step 1: 创建客户转移页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/transfer/TransferCreate.vue
git add frontend/src/router/index.ts
git commit -m "feat(transfer-create): 创建客户转移页面"
```

---

### Task 23: 转移历史记录 (TransferHistory.vue)

**Files:**
- Create: `frontend/src/views/transfer/TransferHistory.vue`
- API: `frontend/src/api/transfer.ts` (已有)

**Step 1: 创建转移历史页面**

**Step 2: 添加路由配置**

**Step 3: 验证功能**

**Step 4: 提交**
```bash
git add frontend/src/views/transfer/TransferHistory.vue
git add frontend/src/router/index.ts
git commit -m "feat(transfer-history): 创建转移历史记录页面"
```

---

## 最终验证与测试

### Task 24: 全量测试与验证

**Step 1: 运行所有 E2E 测试**
```bash
cd frontend
npx playwright test
```

**Step 2: 运行 Lint 检查**
```bash
npm run lint
```

**Step 3: 手动验证关键流程**
- 登录流程
- 客户 CRUD 流程
- 仪表盘展示

**Step 4: 提交（如无修改则跳过）**

---

## 设计规范参考

所有页面开发需遵循以下设计规范：

### 色彩系统
- 主色：#165DFF (Arco Blue)
- 成功：#00B42A
- 警告：#FF7D00
- 错误：#F53F3F

### 组件尺寸
- 按钮高度：36px(默认) / 44px(大)
- 输入框：44px(大)
- 卡片圆角：8px
- 表格行高：48px

### 参考原型
- `theme/login-preview.html` - 登录页设计
- `theme/dashboard-preview.html` - 仪表盘设计

---

*文档版本：v1.0*
*创建日期：2026-03-06*
*工作区：.worktrees/frontend-redesign*
*分支：feature/frontend-redesign*