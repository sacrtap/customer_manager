import api from './index'

export interface User {
  id: number
  username: string
  real_name: string
  email?: string
  phone?: string
  status: 'active' | 'inactive'
  roles: string[]
  role_ids: number[]
  created_at: string
  updated_at: string
}

export interface UserCreate {
  username: string
  password: string
  real_name: string
  email?: string
  phone?: string
  status?: 'active' | 'inactive'
  role_ids?: number[]
}

export interface UserUpdate {
  real_name?: string
  email?: string
  phone?: string
  status?: 'active' | 'inactive'
  role_ids?: number[]
}

export interface UserQuery {
  page?: number
  size?: number
  keyword?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const userApi = {
  async list(query: UserQuery): Promise<PaginatedResponse<User>> {
    const response = await api.get<PaginatedResponse<User>>('/users', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<User> {
    const response = await api.get<User>(`/users/${id}`)
    return response.data
  },

  async create(data: UserCreate): Promise<User> {
    const response = await api.post<User>('/users', data)
    return response.data
  },

  async update(id: number, data: UserUpdate): Promise<User> {
    const response = await api.put<User>(`/users/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/users/${id}`)
  },

  async updatePassword(id: number, newPassword: string): Promise<void> {
    await api.post(`/users/${id}/password`, { new_password: newPassword })
  },

  async listSales(): Promise<User[]> {
    const response = await api.get<User[]>('/users?role=sales')
    return response.data
  }
}
