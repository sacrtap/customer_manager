<!-- frontend/src/layouts/MainLayout.vue -->
<template>
  <div class="main-layout">
    <a-layout>
      <!-- 顶部导航栏 -->
      <a-layout-header class="layout-header">
        <div class="header-left">
          <a-space>
            <a-icon type="icon-dashboard" :size="24" />
            <span class="app-title">客户运营中台</span>
          </a-space>
        </div>

        <div class="header-right">
          <a-space>
            <!-- 通知图标 -->
            <a-badge :count="notificationCount" :max-count="99">
              <a-button shape="circle" type="text" @click="showNotifications">
                <a-icon type="icon-notification" :size="20" />
              </a-button>
            </a-badge>

            <!-- 用户信息下拉菜单 -->
            <a-dropdown @select="handleMenuSelect">
              <div class="user-info">
                <a-avatar :size="32">
                  {{ userInfo.real_name?.charAt(0) }}
                </a-avatar>
                <span class="user-name">{{ userInfo.real_name }}</span>
                <a-icon type="icon-down" />
              </div>

              <template #content>
                <a-dropdown-menu>
                  <a-dropdown-menu-item key="profile">
                    <a-icon type="icon-user" />
                    个人信息
                  </a-dropdown-menu-item>
                  <a-dropdown-menu-item key="change-password">
                    <a-icon type="icon-lock" />
                    修改密码
                  </a-dropdown-menu-item>
                  <a-dropdown-menu-item key="divider" />
                  <a-dropdown-menu-item key="logout">
                    <a-icon type="icon-logout" />
                    退出登录
                  </a-dropdown-menu-item>
                </a-dropdown-menu>
              </template>
            </a-dropdown>
          </a-space>
        </div>
      </a-layout-header>

      <a-layout>
        <!-- 侧边栏菜单 -->
        <a-layout-sider collapsible breakpoint="xl">
          <a-menu
            :selected-keys="selectedMenuKeys"
            :default-selected-keys="['dashboard']"
            @menu-item-click="handleMenuSelect"
          >
            <a-menu-item key="dashboard">
              <template #icon>
                <a-icon type="icon-home" />
              </template>
              工作台
            </a-menu-item>

            <a-sub-menu key="customer">
              <template #icon>
                <a-icon type="icon-user-group" />
              </template>
              <template #title>客户管理</template>
              <a-menu-item key="customer-list">
                客户列表
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('customer.import')"
                key="customer-import"
              >
                批量导入
              </a-menu-item>
            </a-sub-menu>

            <a-sub-menu
              v-if="hasAnyPermission(['user.view', 'rbac.role', 'system.log.view'])"
              key="system"
            >
              <template #icon>
                <a-icon type="icon-settings" />
              </template>
              <template #title>系统管理</template>
              <a-menu-item
                v-if="hasPermission('user.view')"
                key="system-users"
              >
                用户管理
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('rbac.role')"
                key="system-roles"
              >
                角色管理
              </a-menu-item>
              <a-menu-item
                v-if="hasPermission('system.log.view')"
                key="system-logs"
              >
                操作日志
              </a-menu-item>
            </a-sub-menu>
          </a-menu>
        </a-layout-sider>

        <!-- 内容区域 -->
        <a-layout-content class="layout-content">
          <router-view />
        </a-layout-content>
      </a-layout>
    </a-layout>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
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
