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
