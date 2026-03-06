import api from './index'

export interface Billing {
  id: string
  customer_id: number
  customer_name: string
  customer_code?: string
  amount: number
  status: 'pending' | 'sent' | 'paid' | 'exception'
  billing_date: string
  due_date?: string
  paid_date?: string
  remark?: string
  created_at: string
  updated_at: string
}

export interface BillingCreate {
  customer_id: number
  customer_name: string
  customer_code?: string
  amount: number
  billing_date?: string
  due_date?: string
  remark?: string
}

export interface BillingQuery {
  page?: number
  size?: number
  customer_id?: number
  status?: string
  billing_date_start?: string
  billing_date_end?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const billingApi = {
  async list(query: BillingQuery): Promise<PaginatedResponse<Billing>> {
    const response = await api.get<PaginatedResponse<Billing>>('/billing', {
      params: query
    })
    return response.data
  },

  async get(id: string): Promise<Billing> {
    const response = await api.get<{ data: Billing }>(`/billing/${id}`)
    return response.data.data
  },

  async create(data: BillingCreate): Promise<Billing> {
    const response = await api.post<{ data: Billing }>('/billing', data)
    return response.data.data
  },

  async update(id: string, data: Partial<BillingCreate>): Promise<Billing> {
    const response = await api.put<{ data: Billing }>(`/billing/${id}`, data)
    return response.data.data
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/billing/${id}`)
  },

  async markAsSent(id: string): Promise<Billing> {
    const response = await api.post<{ data: Billing }>(`/billing/${id}/send`)
    return response.data.data
  },

  async markAsPaid(id: string): Promise<Billing> {
    const response = await api.post<{ data: Billing }>(`/billing/${id}/pay`)
    return response.data.data
  },

  async markException(id: string, reason: string): Promise<Billing> {
    const response = await api.post<{ data: Billing }>(`/billing/${id}/exception`, { reason })
    return response.data.data
  }
}
