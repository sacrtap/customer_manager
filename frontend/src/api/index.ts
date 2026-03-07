import axios from 'axios'
import type { AxiosInstance, AxiosError } from 'axios'
import { useUserStore } from '@/stores/user'

const apiClient: AxiosInstance = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

const getUserStore = () => {
  try {
    return useUserStore()
  } catch {
    return null
  }
}

apiClient.interceptors.request.use(
  (config) => {
    const store = getUserStore()
    const token = store?.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

apiClient.interceptors.response.use(
  (response) => {
    // 后端统一返回格式：{ data: {...}, timestamp: "..." }
    // 前端统一解包，直接返回 data 内容
    if (response.data && response.data.data !== undefined) {
      return response.data.data
    }
    return response.data
  },
  (error: AxiosError) => {
    const errorMessage = (error.response?.data as any)?.error?.message || '请求失败'
    console.error('API Error:', errorMessage)
    return Promise.reject(new Error(errorMessage))
  }
)

export default apiClient
