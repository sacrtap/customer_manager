import api from './index'

export interface Transfer {
  id: number
  customer_id: number
  customer_name: string
  customer_code: string
  from_sales_rep_id: number
  from_sales_rep_name: string
  to_sales_rep_id: number
  to_sales_rep_name: string
  reason: string
  status: 'pending' | 'approved' | 'rejected' | 'completed'
  approved_by?: number
  approved_at?: string
  created_by: number
  created_at: string
  updated_at: string
}

export interface TransferCreateRequest {
  customer_id: number
  to_sales_rep_id: number
  reason: string
}

export interface TransferQuery {
  page?: number
  size?: number
  customer_id?: number
  from_sales_rep_id?: number
  to_sales_rep_id?: number
  status?: string
  created_at_start?: string
  created_at_end?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const transferApi = {
  async list(query: TransferQuery): Promise<PaginatedResponse<Transfer>> {
    const response = await api.get<PaginatedResponse<Transfer>>('/transfers', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<Transfer> {
    const response = await api.get<Transfer>(`/transfers/${id}`)
    return response.data
  },

  async create(data: TransferCreateRequest): Promise<Transfer> {
    const response = await api.post<Transfer>('/transfers', data)
    return response.data
  },

  async approve(id: number): Promise<Transfer> {
    const response = await api.post<Transfer>(`/transfers/${id}/approve`)
    return response.data
  },

  async reject(id: number): Promise<Transfer> {
    const response = await api.post<Transfer>(`/transfers/${id}/reject`)
    return response.data
  },

  async complete(id: number): Promise<Transfer> {
    const response = await api.post<Transfer>(`/transfers/${id}/complete`)
    return response.data
  }
}
