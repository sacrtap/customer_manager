import { createRouter, createWebHistory } from 'vue-router'
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
        component: () => import('@/views/customer/CustomerImport.vue'),
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
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.requiresAuth && !token) {
    next({ name: 'Login', query: { redirect: to.fullPath } })
    return
  }

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
