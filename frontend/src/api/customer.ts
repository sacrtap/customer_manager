import api from './index'

export interface Customer {
  id: number
  name: string
  code?: string
  industry?: string
  sales_rep_id: number
  tier_level: string
  annual_consumption: number
  status: string
  contact_person?: string
  contact_phone?: string
  contact_email?: string
  address?: string
  remark?: string
  created_at: string
  updated_at: string
}

export interface CustomerQuery {
  page?: number
  size?: number
  keyword?: string
  sales_rep_ids?: number[]
  industries?: string[]
  status?: string[]
  tier_levels?: string[]
  annual_consumption_min?: number
  annual_consumption_max?: number
  created_at_start?: string
  created_at_end?: string
  updated_at_start?: string
  updated_at_end?: string
  sort_field?: string
  sort_desc?: boolean
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const customerApi = {
  async list(query: CustomerQuery): Promise<PaginatedResponse<Customer>> {
    const response = await api.get<PaginatedResponse<Customer>>('/customers', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<Customer> {
    const response = await api.get<Customer>(`/customers/${id}`)
    return response.data
  },

  async create(data: Partial<Customer>): Promise<Customer> {
    const response = await api.post<Customer>('/customers', data)
    return response.data
  },

  async update(id: number, data: Partial<Customer>): Promise<Customer> {
    const response = await api.put<Customer>(`/customers/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/customers/${id}`)
  }
}
