import api from './index'

export interface Role {
  id: number
  name: string
  code: string
  description?: string
  permissions: string[] | Record<string, boolean>
  is_system: boolean
  created_at: string
  updated_at: string
}

export interface RoleCreate {
  name: string
  code: string
  description?: string
  permissions: string[] | Record<string, boolean>
}

export interface RoleUpdate {
  name?: string
  description?: string
  permissions?: string[] | Record<string, boolean>
}

export interface RoleQuery {
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

export const roleApi = {
  async list(query: RoleQuery): Promise<PaginatedResponse<Role>> {
    const response = await api.get<PaginatedResponse<Role>>('/roles', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<Role> {
    const response = await api.get<Role>(`/roles/${id}`)
    return response.data
  },

  async create(data: RoleCreate): Promise<Role> {
    const response = await api.post<Role>('/roles', data)
    return response.data
  },

  async update(id: number, data: RoleUpdate): Promise<Role> {
    const response = await api.put<Role>(`/roles/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/roles/${id}`)
  }
}
