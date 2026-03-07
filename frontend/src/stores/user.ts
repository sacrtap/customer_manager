import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { UserInfo } from '@/types/user'

export const useUserStore = defineStore('user', () => {
  const userInfo = ref<UserInfo | null>(null)
  const token = ref('')
  const permissions = ref<string[]>([])

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

  const login = async (credentials: { username: string; password: string }) => {
    const response = await fetch('/api/v1/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(credentials)
    })

    if (!response.ok) {
      throw new Error('登录失败')
    }

    const data = await response.json()

    token.value = data.data.token
    userInfo.value = data.data.user
    permissions.value = data.data.permissions || []

    localStorage.setItem('token', data.data.token)
    localStorage.setItem('userInfo', JSON.stringify(data.data.user))
    localStorage.setItem('permissions', JSON.stringify(data.data.permissions || []))
  }

  const logout = async () => {
    try {
      await fetch('/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })
    } finally {
      token.value = ''
      userInfo.value = null
      permissions.value = []
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
      localStorage.removeItem('permissions')
    }
  }

  const hasPermission = (permission: string) => {
    if (!userInfo.value) return false

    if (userInfo.value.role === 'admin') {
      return true
    }

    return permissions.value.includes(permission) || permissions.value.includes('*')
  }

  const hasAnyPermission = (perms: string[]) => {
    if (!userInfo.value) return false
    if (userInfo.value.role === 'admin') return true

    return perms.some(perm => hasPermission(perm))
  }

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
