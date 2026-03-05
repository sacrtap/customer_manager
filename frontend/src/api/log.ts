import api from './index'

export interface OperationLog {
  id: number
  user_id: number
  username?: string
  operation_type: string
  target_type?: string
  target_id?: number
  old_value?: any
  new_value?: any
  ip_address?: string
  created_at: string
}

export interface LogQuery {
  page?: number
  size?: number
  user_id?: number
  operation_type?: string
  target_type?: string
  start_time?: string
  end_time?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const logApi = {
  async list(query: LogQuery): Promise<PaginatedResponse<OperationLog>> {
    const response = await api.get<PaginatedResponse<OperationLog>>('/system/logs', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<OperationLog> {
    const response = await api.get<OperationLog>(`/system/logs/${id}`)
    return response.data
  }
}
