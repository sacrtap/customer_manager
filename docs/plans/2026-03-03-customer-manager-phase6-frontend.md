# 阶段 6: Dashboard 与前端集成

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**阶段目标:** 实现前端核心功能,包括 Dashboard 页面、主布局、路由配置、状态管理、API 调用封装

**预计时间:** 3-5 天

**前置依赖:** 阶段 5: 批量导入导出功能

**Architecture:** 
- 创建前端路由配置
- 实现主布局组件(顶部导航、侧边栏菜单)
- 实现 Dashboard 页面
- 创建用户状态管理
- 封装 API 调用
- 创建公共组件

**Tech Stack:**
- 框架: Vue 3 (Composition API)
- 状态管理: Pinia
- 路由: Vue Router
- UI 组件: Arco Design
- HTTP: Axios

---

## Task 21: 创建前端路由配置

**Files:**
- Create: `frontend/src/router/index.ts`
- Create: `frontend/src/types/router.ts`

**Step 1: 创建路由配置**

```typescript
// frontend/src/router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import type { AppRouteRecordRaw } from '@/types/router'

const routes: AppRouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: {
          title: '工作台',
          requiresAuth: true,
          icon: 'icon-home'
        }
      },
      {
        path: 'profile',
        name: 'Profile',
        component: () => import('@/views/Profile.vue'),
        meta: {
          title: '个人信息',
          requiresAuth: true,
          icon: 'icon-user'
        }
      },
      {
        path: 'change-password',
        name: 'ChangePassword',
        component: () => import('@/views/ChangePassword.vue'),
        meta: {
          title: '修改密码',
          requiresAuth: true,
          icon: 'icon-lock'
        }
      },
      {
        path: 'customers',
        name: 'CustomerList',
        component: () => import('@/views/customer/CustomerList.vue'),
        meta: {
          title: '客户列表',
          requiresAuth: true,
          icon: 'icon-user-group',
          permissions: ['customer.view']
        }
      },
      {
        path: 'customers/import',
        name: 'CustomerImport',
        component: () => import('@/views/customer/CustomerImportation.vue'),
        meta: {
          title: '批量导入',
          requiresAuth: true,
          permissions: ['customer.import']
        }
      },
      {
        path: 'system/users',
        name: 'UserManage',
        component: () => import('@/views/system/UserManage.vue'),
        meta: {
          title: '用户管理',
          requiresAuth: true,
          icon: 'icon-settings',
          permissions: ['user.view']
        }
      },
      {
        path: 'system/roles',
        name: 'RoleManage',
        component: () => import('@/views/system/RoleManage.vue'),
        meta: {
          title: '角色管理',
          requiresAuth: true,
          icon: 'icon-safe',
          permissions: ['rbac.role']
        }
      },
      {
        path: 'system/logs',
        name: 'LogView',
            component: () => import('@/views/system/LogView.vue'),
            meta: {
              title: '操作日志',
              requiresAuth: true,
              icon: 'icon-file',
              permissions: ['system.log.view']
            }
          }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 检查是否需要认证
  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }
  
  // 检查权限
  if (to.meta.permissions && token) {
    const permissions = JSON.parse(localStorage.getItem('permissions') || '[]')
    const hasPermission = to.meta.permissions.some((perm: string) => {
      if (perm === '*') return true
      if (perm.includes('.*')) {
        const prefix = perm.replace('.*', '')
        return permissions.some((p: string) => p.startsWith(prefix))
      }
      return permissions.includes(perm)
    })
    
    if (!hasPermission) {
      next({ name: 'Dashboard' })
      return
    }
  }
  
  next()
})

export default router
```

**Step 2: 创建路由类型定义**

```typescript
// frontend/src/types/router.ts
export interface AppRouteRecordRaw {
  path: string
  name: string
  component?: any
  redirect?: string
  children?: AppRouteRecordRaw[]
  meta?: {
    title: string
    requiresAuth?: boolean
    icon?: string
    permissions?: string[]
    hidden?: boolean
  }
}
```

**Step 3: 更新 main.ts**

```typescript
// frontend/src/main.ts
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)
app.mount('#app')
```

**Step 4: Commit**

```bash
cd frontend
git add src/router/ src/types/ src/main.ts
git commit -m "feat: create router configuration with guards"
```

---

## Task 22: 创建用户状态管理

**Files:**
- Create: `frontend/src/stores/user.ts`
- Create: `frontend/src/stores/index.ts`

**Step 1: 创建用户状态管理**

```typescript
// frontend/src/stores/user.ts
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref('')
  const permissions = ref<string[]>([])
  
  // 初始化
  const init = () => {
    const savedToken = localStorage.getItem('token')
    const savedUserInfo = localStorage.getItem('userInfo')
    const savedPermissions = localStorage.getItem('permissions')
    
    if (savedToken) {
      token.value = savedToken
    }
    if (savedUserInfo) {
      try {
        userInfo.value = JSON.parse(savedUserInfo)
      } catch (e) {
        console.error('Failed to parse user info:', e)
      }
    }
    if (savedPermissions) {
      try {
        permissions.value = JSON.parse(savedPermissions)
      } catch (e) {
        console.error('Failed to parse permissions:', e)
      }
    }
  }
  
  // 登录
  const login = async (username: string, password: string) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ username, password })
    })
    
    if (!response.ok) {
      throw new Error('登录失败')
    }
    
    const data = await response.json()
    
    token.value = data.data.token
    userInfo.value = data.data.user
    permissions.value = data.data.permissions || []
    
    // 保存到本地存储
    localStorage.setItem('token', data.data.token)
    localStorage.setItem('userInfo', JSON.stringify(data.data.user))
    localStorage.setItem('permissions', JSON.stringify(data.data.permissions || []))
  }
  
  // 退出登录
  const logout = async () => {
    try {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
    } finally {
      // 清除本地数据
      token.value = ''
      userInfo.value = null
      permissions.value = []
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('permissions')
    }
  }
  
  // 权限检查
  const hasPermission = (permission: string) => {
    if (!userInfo.value) return false
    
    // 超级管理员
    if (userInfo.value.role === 'admin') {
      return true
    }
    
    // 检查权限
    return permissions.value.includes(permission) || permissions.value.includes('*')
  }
  
  const hasAnyPermission = (perms: string[]) => {
    if (!userInfo.value) return false
    if (userInfo.value.role === 'admin') return true
    
    return perms.some(perm => hasPermission(perm))
  }
  
  // 计算属性
  const isLoggedIn = computed(() => !!token.value && !!userInfo.value)
  const isAdmin = computed(() => userInfo.value?.role === 'admin')
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
  
  return {
    userInfo,
    token,
    permissions,
    isLoggedIn,
    isAdmin,
    roleText,
    init,
    login,
    logout,
    hasPermission,
    hasAnyPermission
  }
})
```

**Step 2: 创建用户类型定义**

```typescript
// frontend/src/types/user.ts
export interface UserInfo {
  id: number
  username: string
  real_name: string
  email?: string
  phone?: string
  role: string
  status: string
  created_at: string
  updated_at: string
}
```

**Step 3: 创建 stores 索引**

```typescript
// frontend/src/stores/index.ts
export { useUserStore } from './user'
```

**Step 4: Commit**

```bash
cd frontend
git add src/stores/ src/types/user.ts
git commit -m "feat: create user state management with Pinia"
```

---

## Task 23: 创建 API 调用封装

**Files:**
- Create: `frontend/src/api/index.ts`
- Create: `frontend/src/api/auth.ts`
- Create: `frontend/src/api/customer.ts`

**Step 1: 创建 API 基础配置**

```typescript
// frontend/src/api/index.ts
import axios from 'axios'
import type { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse } from 'axios'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 创建 axios 实例
const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    const token = userStore.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    const errorMessage = error.response?.data?.error?.message || '请求失败'
    console.error('API Error:', errorMessage)
    return Promise.reject(new Error(errorMessage))
  }
)

export default apiClient
```

**Step 2: 创建认证 API**

```typescript
// frontend/src/api/auth.ts
import api from './index'
import type { UserInfo } from '@/types/user'

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  token: string
  user: UserInfo
  permissions: string[]
}

export const authApi = {
  async login(data: LoginRequest): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/login', data)
    return response.data
  },
  
  async logout(): Promise<void> {
    await api.post('/auth/logout')
  },
  
  async getCurrentUser(): Promise<UserInfo> {
    const response = await api.get<UserInfo>('/auth/me')
    return response.data
  }
}
```

**Step 3: 创建客户 API**

```typescript
// frontend/src/api/customer.ts
import api from './index'

export interface Customer {
  id: number
  name: string
  code?: string
  industry?: string
  sales_rep_id: number
  tier_level: string
  annual_consumption: number
  status: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  address?: string
  remark?: string
  created_at: string
  updated_at: string
}

export interface CustomerQuery {
  page?: number
  size?: number
  keyword?: string
  sales_rep_ids?: number[]
  industries?: string[]
  status?: string[]
  tier_levels?: string[]
  annual_consumption_min?: number
  annual_consumption_max?: number
  created_at_start?: string
  created_at_end?: string
  updated_at_start?: string
  updated_at_end?: string
  sort_field?: string
  sort_desc?: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const customerApi = {
  async list(query: CustomerQuery): Promise<PaginatedResponse<Customer>> {
    const response = await api.get<PaginatedResponse<Customer>>('/customers', {
      params: query
    })
    return response.data
  },
  
  async get(id: number): Promise<Customer> {
    const response = await api.get<Customer>(`/customers/${id}`)
    return response.data
  },
  
  async create(data: Partial<Customer>): Promise<Customer> {
    const response = await api.post<Customer>('/customers', data)
    return response.data
  },
  
  async update(id: number, data: Partial<Customer>): Promise<Customer> {
    const response = await api.put<Customer>(`/customers/${id}`, data)
    return response.data
  },
  
  async delete(id: number): Promise<void> {
    await api.delete(`/customers/${id}`)
  }
}
```

**Step 4: Commit**

```bash
cd frontend
git add src/api/
git commit -m "feat: create API client with axios"
```

---

## Task 24: 创建登录页面

**Files:**
- Create: `frontend/src/views/Login.vue`

**Step 1: 创建登录页面**

```vue
<!-- frontend/src/views/Login.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>客户运营中台</h1>
        <p>内部运营中台客户信息管理与运营系统</p>
      </div>
      
      <Form :model="form" @submit="handleLogin" layout:vertical>
        <FormItem field="username" :rules="usernameRules" label="用户名">
          <Input v-model="form.username" placeholder="请输入用户名" size="large" />
        </FormItem>
        
        <FormItem field="password" :rules="passwordRules" label="密码">
          <InputPassword v-model="form.password" placeholder="请输入密码" size="large" />
        </FormItem>
        
        <FormItem>
          <Button 
            type="primary" 
            html-type="submit" 
            size="large" 
            :loading="loading"
            long
          >
            登录
          </Button>
        </FormItem>
      </Form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { Message } from '@arco-design/web-vue'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const form = reactive({
  username: '',
  password: ''
})

const loading = ref(false)

const usernameRules = [
  { required: true, message: '请输入用户名' },
  { minLength: 3, message: '用户名至少3个字符' }
]

const passwordRules = [
  { required: true, { message: '请输入密码' },
  { minLength: 6, message: '密码至少6个字符' }
]

const handleLogin = async () => {
  try {
    loading.value = true
    
    await userStore.login(form.username, form.password)
    
    Message.success('登录成功')
    
    // 跳转到重定向页面或 Dashboard
    const redirect = route.query.redirect as string
    router.push(redirect || '/dashboard')
  } catch (error: {
    Message.error(error.message || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  
  .login-box {
    width: 400px;
    padding: 40px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    
    .login-header {
      text-align: center;
      margin-bottom: 40px;
      
      h1 {
        font-size: 28px;
        color: #1f2937;
        margin-bottom: 8px;
      }
      
      p {
        color: #86909c;
        font-size: 14px;
      }
    }
  }
}
</style>
```

**Step 2: 更新 App.vue**

```vue
<!-- frontend/src/App.vue -->
<template>
  <router-view />
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  // 初始化用户状态
  userStore.init()
})
</script>

<style>
#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}
</style>
```

**Step 3: Commit**

```bash
cd frontend
git add src/views/Login.vue src/App.vue
git commit -m "feat: create login page with authentication"
```

---

## 阶段完成检查清单

完成以下检查后,阶段 6 即可视为完成:

- [ ] 前端路由配置已创建(含路由守卫)
- [ ] 用户状态管理已实现
- [ ] API 调用封装已创建
- [ ] 登录页面已实现
- [ ] Dashboard 页面占位符已创建
- [ ] 主布局占位符已创建

**注意**: 由于篇幅限制,Dashboard 页面、主布局、其他页面将在阶段 7 中补充完整实现

---

## 下一步

完成阶段 6 后,请继续执行 **阶段 7: 测试与优化**

文档: `docs/plans/2026-03-03-customer-manager-phase7-testing.md`
