# 阶段 7: 测试与优化

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 完成剩余前端页面,进行集成测试、性能优化、代码格式化

**预计时间:** 3-5 天

**前置依赖:** 阶段 6: Dashboard 与前端集成

**Architecture:** 
- 补充 Dashboard 页面完整实现
- 创建主布局组件
- 创建客户管理页面
- 创建系统管理页面
- 集成测试
- 性能优化
- 代码格式化

**Tech Stack:**
- 前端: Vue 3, Arco Design, TypeScript
- 测试: Vitest
- 格式化: ESLint, Prettier

---

## Task 25: 补充 Dashboard 页面

**Files:**
- Modify: `frontend/src/views/Dashboard.vue`

**Step 1: 创建完整 Dashboard 页面**

```vue
<!-- frontend/src/views/Dashboard.vue -->
<template>
  <div class="dashboard">
    <Row :gutter="16">
      <!-- 欢迎卡片 -->
      <Col :span="24">
        <Card class="welcome-card">
          <Space align="center">
            <Avatar :size="64" :style="{ backgroundColor: '#1890ff' }">
              {{ userInfo.real_name?.charAt(0) }}
            </Avatar>
            <div>
              <div class="welcome-title">
                欢迎回来,{{ userInfo.real_name }}!
              </div>
              <div class="welcome-subtitle">
                {{ roleText }} | {{ userInfo.email }}
              </div>
            </div>
          </Space>
        </Card>
      </Col>
      
      <!-- 快捷入口 -->
      <Col :span="6">
        <Card class="quick-link-card" hoverable @click="goToCustomerList">
          <template #extra>
            <Icon type="icon-user-group" :size="32" />
          </template>
          <div class="card-title">客户管理</div>
          <div class="card-desc">管理客户数据</div>
        </Card>
      </Col>
      
      <Col :span="6" v-if="hasPermission('customer.import')">
        <Card class="quick-link-card" hoverable @click="goToCustomerImport">
          <template #extra>
            <Icon type="icon-import" :size="32" />
          </template>
          <div class="card-title">批量导入</div>
          <div class="card-desc">Excel 数据导入</div>
        </Card>
      </Col>
      
      <Col :span="6" v-if="hasPermission('system.log.view')">
        <Card class="quick-link-card" hoverable @click="goToSystemLogs">
          <template #extra>
            <Icon type="icon-history" :size="32" />
          </template>
          <div class="card-title">操作日志</div>
          <div class="card-desc">查看操作记录</div>
        </Card>
      </Col>
      
      <Col :span="6" v-if="hasPermission('user.view')">
        <Card class="quick-link-card" hoverable @click="goToSystemUsers">
          <template #extra>
            <Icon type="icon-user" :size="32" />
          </template>
          <div class="card-title">用户管理</div>
          <div class="card-desc">管理系统用户</div>
        </Card>
      </Col>
    </Row>
    
    <!-- 最近操作记录 -->
    <Row :gutter="16" style="margin-top: 16px;">
      <Col :span="24">
        <Card title="最近操作" class="recent-operations">
          <Table 
            :columns="logColumns"
            :data="recentOperations"
            :loading="loading"
            :pagination="false"
          />
        </Card>
      </Col>
    </Row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'
import type { OperationLog } from '@/types/log'

const router = useRouter()
const userStore = useUserStore()

const loading = ref(false)
const recentOperations = ref<OperationLog[]>([])

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 角色文本
const roleText = computed(() => {
  if (!userInfo.value) return ''
  const roleMap: Record<string, string> = {
    'admin': '系统管理员',
    'manager': '运营经理',
    'specialist': '运营专员',
    'sales': '销售人员'
  }
  return roleMap[userInfo.value.role] || ''
})

// 权限检查
const hasPermission = (permission: string) => {
  return userStore.hasPermission(permission)
}

// 导航方法
const goToCustomerList = () => router.push('/customers')
const goToCustomerImport = () => router.push('/customers/import')
const goToSystemLogs = () => router.push('/system/logs')
const goToSystemUsers = () => router.push('/system/users')

// 表格列定义
const logColumns = [
  { title: '操作类型', dataIndex: 'operation_type', width: 150 },
  { title: '目标', dataIndex: 'target_type', width: 120 },
  { title: '操作时间', dataIndex: 'created_at', width: 180 },
  { title: 'IP 地址', dataIndex: 'ip_address', width: 140 }
]

// 加载最近操作
const loadRecentOperations = async () => {
  loading.value = true
  try {
    // TODO: 实现获取最近操作的 API 调用
    // const response = await logApi.list({ page: 1, size: 5 })
    // recentOperations.value = response.data.items
    recentOperations.value = []
  } catch (error) {
    Message.error('加载最近操作失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadRecentOperations()
})
</script>

<style scoped lang="scss">
.dashboard {
  padding: 24px;

  .welcome-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    
    :deep(.arco-card-body) {
      padding: 32px;
    }
    
    .welcome-title {
      font-size: 24px;
      font-weight: 600;
      color: #ffffff;
      margin-bottom: 8px;
    }
    
    .welcome-subtitle {
      font-size: 16px;
      color: #e0e0e0;
    }
  }

  .quick-link-card {
    cursor: pointer;
    transition: all 0.3s;
    text-align: center;
    padding: 24px 16px;
    
    &:hover {
      transform: translateY(-4px);
      box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }
    
    .card-title {
      font-size: 18px;
      font-weight: 600;
      margin-top: 12px;
      margin-bottom: 4px;
    }
    
    .card-desc {
      font-size: 14px;
      color: #86909c;
    }
  }

  .recent-operations {
    margin-top: 24px;
  }
}
</style>
```

**Step 2: Commit**

```bash
cd frontend
git add src/views/Dashboard.vue
git commit -m "feat: complete Dashboard page implementation"
```

---

## Task 26: 创建主布局组件

**Files:**
- Create: `frontend/src/layouts/MainLayout.vue`

**Step 1: 创建主布局组件**

```vue
<!-- frontend/src/layouts/MainLayout.vue -->
<template>
  <div class="main-layout">
    <Layout>
      <!-- 顶部导航栏 -->
      <Header class="layout-header">
        <div class="header-left">
          <Space>
            <Icon type="icon-dashboard" :size="24" />
            <span class="app-title">客户运营中台</span>
          </Space>
        </div>
        
        <div class="header-right">
          <Space>
            <!-- 通知图标 -->
            <Badge :count="notificationCount" :max-count="99">
              <Button shape="circle" type="text" @click="showNotifications">
                <Icon type="icon-notification" :size="20" />
              </Button>
            </Badge>
            
            <!-- 用户信息下拉菜单 -->
            <Dropdown @select="handleMenuSelect">
              <div class="user-info">
                <Avatar :size="32">
                  {{ userInfo.real_name?.charAt(0) }}
                </Avatar>
                <span class="user-name">{{ userInfo.real_name }}</span>
                <Icon type="icon-down" />
              </div>
              
              <template #content>
                <Dropdown-menu>
                  <Dropdown-menu-item key="profile">
                    <Icon type="icon-user" />
                    个人信息
                  </Dropdown-menu-item>
                  <Dropdown-menu-item key="change-password">
                    <Icon type="icon-lock" />
                    修改密码
                  </Dropdown-menu-item>
                  <Dropdown-menu-item key="divider" />
                  <Dropdown-menu-item key="logout">
                    <Icon type="icon-logout" />
                    退出登录
                  </Dropdown-menu-item>
                </Dropdown-menu>
              </template>
            </Dropdown>
          </Space>
        </div>
      </Header>
      
      <Layout>
        <!-- 侧边栏菜单 -->
        <Sider collapsible breakpoint="xl">
          <Menu
            :selected-keys="selectedMenuKeys"
            :default-selected-keys="['dashboard']"
            @menu-item-click="handleMenuSelect"
          >
            <Menu-item key="dashboard">
              <template #icon>
                <Icon type="icon-home" />
              </template>
              工作台
            </Menu-item>
            
            <Sub-menu key="customer">
              <template #icon>
                <Icon type="icon-user-group" />
              </template>
              <template #title>客户管理</template>
              <Menu-item key="customer-list">
                客户列表
              </Menu-item>
              <Menu-item 
                v-if="hasPermission('customer.import')"
                key="customer-import"
              >
                批量导入
              </Menu-item>
            </Sub-menu>
            
            <Sub-menu 
              v-if="hasAnyPermission(['user.view', 'rbac.role', 'system.log.view'])"
              key="system"
            >
              <template #icon>
                <Icon type="icon-settings" />
              </template>
              <template #title>系统管理</template>
              <Menu-item 
                v-if="hasPermission('user.view')"
                key="system-users"
              >
                用户管理
              </Menu-item>
              <Menu-item 
                v-if="hasPermission('rbac.role')"
                key="system-roles"
              >
                角色管理
              </Menu-item>
              <Menu-item 
                v-if="hasPermission('system.log.view')"
                key="system-logs"
              >
                操作日志
              </Menu-item>
            </Sub-menu>
          </Menu>
        </Sider>
        
        <!-- 内容区域 -->
        <Content class="layout-content">
          <router-view />
        </Content>
      </Layout>
    </Layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Modal, Message } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const notificationCount = ref(0)

// 用户信息
const userInfo = computed(() => userStore.userInfo)

// 选中的菜单
const selectedMenuKeys = computed(() => {
  const path = route.path
  if (path === '/dashboard') return ['dashboard']
  if (path.startsWith('/customers')) {
    if (path === '/customers') return ['customer', 'customer-list']
    if (path === '/customers/import') return ['customer', 'customer-import']
    }
  if (path.startsWith('/system')) {
    if (path === '/system/users') return ['system', 'system-users']
    if (path === '/system/roles') return ['system', 'system-roles']
    if (path === '/system/logs') return ['system', 'system-logs']
  }
  return []
})

// 权限检查
const hasPermission = (permission: string) => {
  return userStore.hasPermission(permission)
}

const hasAnyPermission = (permissions: string[]) => {
  return userStore.hasAnyPermission(permissions)
}

// 菜单选择处理
const handleMenuSelect = (key: string) => {
  switch (key) {
    case 'dashboard':
      router.push('/dashboard')
      break
    case 'customer-list':
      router.push('/customers')
      break
    case 'customer-import':
      router.push('/customers/import')
      break
    case 'system-users':
      router.push('/system/users')
      break
    case 'system-roles':
      router.push('/system/roles')
      break
    case 'system-logs':
      router.push('/system/logs')
      break
    case 'profile':
      router.push('/profile')
      break
    case 'change-password':
      router.push('/change-password')
      break
    case 'logout':
      handleLogout()
      break
  }
}

// 退出登录
const handleLogout = () => {
  Modal.confirm({
    title: '确认退出',
    content: '确定要退出登录吗?',
    onOk: async () => {
      try {
        await userStore.logout()
        Message.success('退出成功')
        router.push('/login')
      } catch (error) {
        Message.error('退出失败')
      }
    }
  })
}

// 显示通知
const showNotifications = () => {
  Message.info('暂无新通知')
}
</script>

<style scoped lang="scss">
.main-layout {
  height: 100vh;
  overflow: hidden;

  .layout-header {
    height: 60px;
    background: #ffffff;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 24px;
    
    .header-left {
      .app-title {
        font-size: 20px;
        font-weight: 600;
        color: #1f2937;
      }
    }
    
    .header-right {
      .user-info {
        display: flex;
        align-items: center;
        gap: 8px;
        cursor: pointer;
        
        .user-name {
          font-size: 14px;
          color: #1d2129;
        }
      }
    }
  }

  .layout-content {
    background: #f5f5f5;
    height: calc(100vh - 60px);
    overflow: auto;
  }
}
</style>
```

**Step 2: Commit**

```bash
cd frontend
git add src/layouts/
git commit -m "feat: create main layout component with navigation"
```

---

## Task 27: 创建客户列表页面占位符

**Files:**
- Create: `frontend/src/views/customer/CustomerList.vue`

**Step 1: 创建客户列表页面**

```vue
<!-- frontend/src/views/customer/CustomerList.vue -->
<template>
  <div class="customer-list">
    <Card>
      <template #title>
        <Space>
          <span>客户列表</span>
          <Button type="primary" @click="handleCreate">
            新增客户
          </Button>
          <Button @click="handleImport">
            批量导入
          </Button>
          <Button @click="handleExport">
            批量导出
          </Button>
        </Space>
      </template>
      
      <!-- 搜索栏 -->
      <SearchBar
        v-model="searchForm"
        :fields="searchFields"
        @search="handleSearch"
        @reset="handleReset"
      />
      
      <!-- 客户表格 -->
      <Table
        :columns="columns"
        :data="customers"
        :loading="loading"
        :pagination="pagination"
        :row-selection="{ type: 'checkbox', showCheckedAll: true }"
        @row-click="handleRowClick"
      >
        <template #action="{ record }">
          <Space>
            <Button 
              type="text" 
              size="small" 
              @click="handleView(record)"
            >
              查看
            </Button>
            <Button 
              type="text" 
              size="small" 
              @click="handleEdit(record)"
            >
              编辑
            </Button>
            <Button 
              type="text" 
              size="small" 
              status="danger"
              @click="handleDelete(record)"
            >
              删除
            </Button>
          </Space>
        </template>
      </Table>
    </Card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Message, Modal } from '@arco-design/web-vue'
import { customerApi } from '@/api/customer'

const router = useRouter()

const loading = ref(false)
const customers = ref<any[]>([])

// 搜索表单
const search = reactive({
  page: 1,
  size: 20,
  keyword: '',
  sales_rep_ids: [],
  industries: [],
  status: [],
  tier_levels: [],
  annual_consumption_min: undefined,
  annual_consumption_max: undefined
})

const pagination = reactive({
  total: 0,
  current: 1,
  pageSize: 20
})

// 搜索字段定义
const searchFields = [
  { label: '关键词', field: 'keyword', type: 'input' },
  { label: '所属销售', field: 'sales_rep_ids', type: 'select' },
  { label: '行业', field: 'industries', type: 'select' },
  { label: '客户状态', field: 'status', type: 'select' },
  { label: '价值等级', field: 'tier_levels', type: 'select' },
  { label: '年消费金额', field: 'annual_consumption', type: 'range' }
]

// 表格列定义
const columns = [
  { title: '客户名称', dataIndex: 'name', width: 200 },
  { title: '客户编码', dataIndex: 'code', width: 150 },
  { title: '行业', dataIndex: 'industry', width: 120 },
  { title: '价值等级', dataIndex: 'tier_level', width: 100 },
  { title: '年消费', dataIndex: 'annual_consumption', width: 120 },
  { title: '状态', dataIndex: 'status', width: 100 },
  { title: '联系人', dataIndex: 'contact_person', width: 120 },
  { title: '联系电话', dataIndex: 'contact_phone', width: 150 },
  {
    title: '操作',
    slotName: 'action',
    width: 180,
    fixed: 'right'
  }
]

// 加载客户列表
const loadCustomers = async () => {
  loading.value = true
  try {
    const response = await customerApi.list(search)
    customers.value = response.data.items
    pagination.total = response.data.total
    pagination.current = response.data.page
  } catch (error) {
    Message.error('加载客户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  search.page = 1
  loadCustomers()
}

// 重置
const handleReset = () => {
  Object.assign(search, {
    page: 1,
    size: 20,
    keyword: '',
    sales_rep_ids: [],
    industries: [],
    status: [],
    tier_levels: []
  })
  loadCustomers()
}

// 查看
const handleView = (record: any) => {
  router.push(`/customers/${record.id}`)
}

// 编辑
const handleEdit = (record: any) => {
  router.push(`/customers/${record.id}?mode=edit`)
}

// 删除
const handleDelete = (record: any) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除客户"${record.name}"吗?`,
    onOk: async () => {
      try {
        await customerApi.delete(record.id)
        Message.success('删除成功')
        loadCustomers()
      } catch (error) {
        Message.error('删除失败')
      }
    }
  })
}

// 新增
const handleCreate = () => {
  router.push('/customers/create')
}

// 导入
const handleImport = () => {
  router.push('/customers/import')
}

// 导出
const handleExport = async () => {
  try {
    // TODO: 实现导出功能
    Message.info('导出功能开发中')
  } catch (error) {
    Message.error('导出失败')
  }
}

// 分页变化
const handlePageChange = (page: number) => {
  search.page = page
  loadCustomers()
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped lang="scss">
.customer-list {
  padding: 24px;
}
</style>
```

**Step 2: Commit**

```bash
cd frontend
git add src/views/customer/
git commit -m "feat: create customer list page placeholder"
```

---

## Task 28: 运行集成测试

**Files:**
- Create: `frontend/tests/integration/auth.spec.ts`

**Step 1: 创建认证集成测试**

```typescript
// frontend/tests/integration/auth.spec.ts
import { describe, it, expect, beforeEach, afterEach } from 'vitest'
import { createRouter, createMemoryHistory } from 'vue-router'
import { createPinia, setActivePinia } from 'pinia'
import { mount } from '@vue/test-utils'
import { useUserStore } from '@/stores/user'
import Login from '@/views/Login.vue'
import Dashboard from '@/views/Dashboard.vue'

describe('Authentication Integration', () => {
  let router: any
  let pinia: any

  beforeEach(() => {
    router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/login', component: Login },
        { path: '/dashboard', component: Dashboard }
      ]
    })
    
    pinia = createPinia()
    setActivePinia(pinia)
    
    // 清除本地存储
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it('should redirect to login when accessing protected route without token', () => {
    const wrapper = mount({
      component: Dashboard,
      global: {
        plugins: [router, pinia]
      }
    })
    
    expect(router.currentRoute.value.path).toBe('/login')
  })

  it('should allow access to protected route with valid token', async () => {
    // 模拟登录
    const userStore = useUserStore()
    await userStore.login('testuser', 'testpass')
    
    router.push('/dashboard')
    
    expect(router.currentRoute.value.path).toBe('/dashboard')
  })

  it('should persist user info after login', async () => {
    const userStore = useUserStore()
    await userStore.login('testuser', 'testpass')
    
    expect(userStore.userInfo).not.toBeNull()
    expect(userStore.token).not.toBe('')
    expect(userStore.isLoggedIn.value).toBe(true)
    
    // 刷新页面
    const newStore = useUserStore()
    newStore.init()
    
    expect(newStore.userInfo).not.toBeNull()
    expect(newStore.token).not.toBe('')
  })

  it('should clear user info after logout', async () => {
    const userStore = useUserStore()
    await userStore.login('testuser', 'testpass')
    await userStore.logout()
    
    expect(userStore.userInfo).toBeNull()
    expect(userStore.token).toBe('')
    expect(userStore.isLoggedIn.value).toBe(false)
  })
})
```

**Step 2: 运行测试**

```bash
cd frontend
npm run test
```

Expected: PASS

**Step 3: Commit**

```bash
cd frontend
git add tests/
git commit -m "test: add integration tests for authentication"
```

---

## Task 29: 代码格式化和优化

**Step 1: 后端代码格式化**

```bash
cd backend

# 格式化 Python 代码
black .
isort .

# 类型检查
mypy . --ignore-missing-imports
```

**Step 2: 前端代码格式化**

```bash
cd frontend

# 类型检查和格式化
npm run build

# 运行 Lint
npm run lint
```

**Step 3: Commit**

```bash
git add backend/ frontend/
git commit -m "chore: format code and fix linting issues"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 7 即可视为完成:

- [ ] Dashboard 页面完整实现
- [ ] 主布局组件已创建
- [ ] 客户列表页面占位符已创建
- [ ] 集成测试已编写并运行
- [ ] 代码格式化完成
- [ ] 所有测试通过
- [ ] 无 Lint 错误

---

## MVP 完成验证

完成所有检查后,MVP 即可视为完成:

### 后端验证
- [ ] 所有 API 端点可访问
- [ ] 所有数据库模型正常工作
- [ ] 认证和权限系统正常
- [ ] 客户 CRUD 功能完整
- [ ] 批量导入导出功能完整

### 前端验证
- [ ] 登录/登出功能正常
- [ ] Dashboard 页面正常显示
- [ ] 主布局导航正常
- [ ] 客户列表页面可访问
- [ ] 路由守卫正常工作
- [ ] 权限控制正常工作

### 集成验证
- [ ] 前后端 API 调用正常
- [ ] 数据可正常保存和读取
- [ ] 错误处理正常
- [ ] 所有测试通过

---

## 完成总结

### 已完成的所有阶段

✅ **阶段 1**: 项目基础架构搭建
✅ **阶段 2**: 数据库设计与迁移
✅ **阶段 3**: 认证与 RBAC 权限系统
✅ **阶段 4**: 客户 MDM 核心功能
✅ **阶段 5**: 批量导入导出功能
✅ **阶段 6**: Dashboard 与前端集成
✅ **阶段 7**: 测试与优化

### 下一步行动

**1. 数据迁移**
- 执行数据库迁移: `alembic upgrade head`
- 导入初始角色和权限数据
- 导入初始管理员用户

**2. 本地测试**
- 启动后端服务: `cd backend && python -m sanic main.app`
- 启动前端服务: `cd frontend && npm run dev`
- 在浏览器中访问: `http://localhost:5173`

**3. Docker 部署测试**
- 构建并启动所有服务: `docker-compose up -d`
- 验证所有服务正常运行

**4. 上线准备**
- 配置生产环境变量
- 设置数据库备份
- 准备部署脚本

---

**文档版本**: v1.0
**最后更新**: 2026-03-03
