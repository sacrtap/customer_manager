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
