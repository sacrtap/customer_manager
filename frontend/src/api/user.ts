import api from './index'
import type { UserInfo } from '@/types/user'

export const userApi = {
  async list(): Promise<UserInfo[]> {
    const response = await api.get<UserInfo[]>('/users')
    return response.data
  },

  async listSales(): Promise<UserInfo[]> {
    const response = await api.get<UserInfo[]>('/users?role=sales')
    return response.data
  }
}
