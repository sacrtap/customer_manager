import api from './index'

export interface CustomerTransfer {
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

export interface TransferCreate {
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
  async list(query: TransferQuery): Promise<PaginatedResponse<CustomerTransfer>> {
    const response = await api.get<PaginatedResponse<CustomerTransfer>>('/transfers', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<CustomerTransfer> {
    const response = await api.get<CustomerTransfer>(`/transfers/${id}`)
    return response.data
  },

  async create(data: TransferCreate): Promise<CustomerTransfer> {
    const response = await api.post<CustomerTransfer>('/transfers', data)
    return response.data
  },

  async approve(id: number): Promise<void> {
    await api.post(`/transfers/${id}/approve`)
  },

  async reject(id: number, reason: string): Promise<void> {
    await api.post(`/transfers/${id}/reject`, { reason })
  },

  async complete(id: number): Promise<void> {
    await api.post(`/transfers/${id}/complete`)
  }
}
