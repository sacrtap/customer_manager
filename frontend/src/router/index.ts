import { createRouter, createWebHistory } from 'vue-router'
import type { AppRouteRecordRaw } from '@/types/router'

const routes: AppRouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/LoginView.vue'),
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
        path: 'customers/:id',
        name: 'CustomerDetail',
        component: () => import('@/views/customer/CustomerDetail.vue'),
        meta: {
          title: '客户详情',
          requiresAuth: true,
          permissions: ['customer.view']
        }
      },
      {
        path: 'customers/create',
        name: 'CustomerCreate',
        component: () => import('@/views/customer/CustomerForm.vue'),
        meta: {
          title: '新增客户',
          requiresAuth: true,
          permissions: ['customer.create']
        }
      },
      {
        path: 'customers/:id/edit',
        name: 'CustomerEdit',
        component: () => import('@/views/customer/CustomerForm.vue'),
        meta: {
          title: '编辑客户',
          requiresAuth: true,
          permissions: ['customer.update']
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
      },
      // 定价策略路由 - 组件待创建
      // {
      //   path: 'pricing/strategies',
      //   name: 'PricingStrategyList',
      //   component: () => import('@/views/pricing/PricingStrategyList.vue'),
      //   meta: {
      //     title: '定价策略',
      //     requiresAuth: true,
      //     icon: 'icon-coins',
      //     permissions: ['pricing.view']
      //   }
      // },
      // {
      //   path: 'pricing/configs',
      //   name: 'PricingConfigList',
      //   component: () => import('@/views/pricing/PricingConfigList.vue'),
      //   meta: {
      //     title: '价格配置',
      //     requiresAuth: true,
      //     icon: 'icon-coins',
      //     permissions: ['pricing.view']
      //   }
      // },
      {
        path: 'pricing/bands',
        name: 'PriceBandList',
        component: () => import('@/views/pricing/PriceBandList.vue'),
        meta: {
          title: '价格区间',
          requiresAuth: true,
          icon: 'icon-coins',
          permissions: ['pricing.view']
        }
      },
      {
        path: 'transfers/create',
        name: 'TransferCreate',
        component: () => import('@/views/transfer/TransferCreate.vue'),
        meta: {
          title: '发起客户转移',
          requiresAuth: true,
          icon: 'icon-swap',
          permissions: ['customer.transfer']
        }
      },
      {
        path: 'transfers/history',
        name: 'TransferHistory',
        component: () => import('@/views/transfer/TransferHistory.vue'),
        meta: {
          title: '转移历史记录',
          requiresAuth: true,
          icon: 'icon-history',
          permissions: ['customer.transfer.view']
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
    
    const hasPermission = permissions.some((perm: string) => {
      if (perm === '*') return true
      if (perm.includes('.*')) {
        const prefix = perm.replace('.*', '')
        return to.meta.permissions.some((p: string) => p.startsWith(prefix))
      }
      return to.meta.permissions.includes(perm)
    })

    if (!hasPermission) {
      next({ name: 'Dashboard' })
      return
    }
  }

  next()
})

export default router
