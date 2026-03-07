import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useUserStore } from '@/stores/user'

// happy-dom localStorage mock
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = String(value)
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key]
    }),
    clear: vi.fn(() => {
      store = {}
    }),
  }
})()

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
  writable: true,
})

describe('User Store', () => {
  beforeEach(() => {
    localStorageMock.clear()
    setActivePinia(createPinia())
  })

  it('initializes with empty state', () => {
    const store = useUserStore()
    expect(store.token).toBe('')
    expect(store.userInfo).toBeNull()
    expect(store.permissions).toEqual([])
  })

  it('has false isLoggedIn when no token', () => {
    const store = useUserStore()
    expect(store.isLoggedIn).toBe(false)
  })

  it('has false isAdmin when no user', () => {
    const store = useUserStore()
    expect(store.isAdmin).toBe(false)
  })

  it('restores token from localStorage on init', () => {
    localStorageMock.setItem('token', 'test-token-123')
    localStorageMock.setItem('userInfo', JSON.stringify({ 
      id: 'user-123', 
      username: 'testuser', 
      role: 'admin' 
    }))
    localStorageMock.setItem('permissions', JSON.stringify(['customer:read']))
    
    const store = useUserStore()
    store.init()
    
    expect(store.token).toBe('test-token-123')
    expect(store.userInfo?.username).toBe('testuser')
    expect(store.permissions).toContain('customer:read')
  })

  it('hasPermission returns true for admin role', () => {
    const store = useUserStore()
    store.userInfo = { id: '1', username: 'admin', role: 'admin' }
    
    expect(store.hasPermission('customer:read')).toBe(true)
    expect(store.hasPermission('any:perm')).toBe(true)
  })

  it('hasPermission checks permissions array', () => {
    const store = useUserStore()
    store.userInfo = { id: '1', username: 'user', role: 'manager' }
    store.permissions = ['customer:read', 'customer:write']
    
    expect(store.hasPermission('customer:read')).toBe(true)
    expect(store.hasPermission('customer:delete')).toBe(false)
  })

  it('roleText returns correct Chinese label', () => {
    const store = useUserStore()
    store.userInfo = { id: '1', username: 'user', role: 'manager' }
    
    expect(store.roleText).toBe('运营经理')
  })
})
