import api from './index'

export interface PriceConfig {
  id: number
  code: string
  name: string
  description?: string
  base_price: number
  status: 'active' | 'disabled'
  created_at: string
  created_by: number
  updated_at?: string
  updated_by?: number
}

export interface PriceConfigCreate {
  code: string
  name: string
  description?: string
  base_price: number
  status?: 'active' | 'disabled'
}

export interface PriceConfigUpdate {
  name?: string
  description?: string
  base_price?: number
  status?: 'active' | 'disabled'
}

export interface PriceConfigQuery {
  page?: number
  size?: number
  code?: string
  name?: string
  status?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const priceConfigApi = {
  async list(query: PriceConfigQuery): Promise<PaginatedResponse<PriceConfig>> {
    const response = await api.get<PaginatedResponse<PriceConfig>>('/price-configs', {
      params: query
    })
    return response.data
  },

  async get(id: number): Promise<PriceConfig> {
    const response = await api.get<{ data: PriceConfig }>(`/price-configs/${id}`)
    return response.data.data
  },

  async create(data: PriceConfigCreate): Promise<PriceConfig> {
    const response = await api.post<{ data: PriceConfig }>('/price-configs', data)
    return response.data.data
  },

  async update(id: number, data: PriceConfigUpdate): Promise<PriceConfig> {
    const response = await api.put<{ data: PriceConfig }>(`/price-configs/${id}`, data)
    return response.data.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/price-configs/${id}`)
  }
}
