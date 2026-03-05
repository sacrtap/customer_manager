import api from './index'

export interface PricingStrategy {
  id: number
  name: string
  code: string
  description?: string
  applicable_customer_type?: string
  applicable_tier_levels: string[]
  discount_type: 'percentage' | 'fixed'
  discount_value: number
  priority: number
  status: 'active' | 'inactive'
  valid_from?: string
  valid_to?: string
  created_by: number
  created_at: string
  updated_at: string
}

export interface PricingStrategyCreate {
  name: string
  code: string
  description?: string
  applicable_customer_type?: string
  applicable_tier_levels: string[]
  discount_type: 'percentage' | 'fixed'
  discount_value: number
  priority: number
  status?: 'active' | 'inactive'
  valid_from?: string
  valid_to?: string
}

export interface PricingStrategyUpdate {
  name?: string
  description?: string
  applicable_customer_type?: string
  applicable_tier_levels?: string[]
  discount_type?: 'percentage' | 'fixed'
  discount_value?: number
  priority?: number
  status?: 'active' | 'inactive'
  valid_from?: string
  valid_to?: string
}

export interface PricingStrategyQuery {
  page?: number
  size?: number
  keyword?: string
  status?: string
  discount_type?: string
  applicable_tier_levels?: string[]
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const pricingStrategyApi = {
  async list(query: PricingStrategyQuery): Promise<PaginatedResponse<PricingStrategy>> {
    const response = await api.get<PaginatedResponse<PricingStrategy>>('/pricing-strategies', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<PricingStrategy> {
    const response = await api.get<PricingStrategy>(`/pricing-strategies/${id}`)
    return response.data
  },

  async create(data: PricingStrategyCreate): Promise<PricingStrategy> {
    const response = await api.post<PricingStrategy>('/pricing-strategies', data)
    return response.data
  },

  async update(id: number, data: PricingStrategyUpdate): Promise<PricingStrategy> {
    const response = await api.put<PricingStrategy>(`/pricing-strategies/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/pricing-strategies/${id}`)
  }
}
