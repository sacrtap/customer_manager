import api from './index'
import type {
  PriceBand,
  PriceBandListResponse,
  PriceBandFilters,
  PriceBandCreateRequest,
  PriceBandUpdateRequest
} from '@/types/price-band'

export const priceBandApi = {
  async list(filters: PriceBandFilters): Promise<PriceBandListResponse> {
    const response = await api.get<PriceBandListResponse>('/price-bands', {
      params: filters
    })
    return response.data
  },

  async get(id: number): Promise<PriceBand> {
    const response = await api.get<PriceBand>(`/price-bands/${id}`)
    return response.data
  },

  async create(data: PriceBandCreateRequest): Promise<PriceBand> {
    const response = await api.post<PriceBand>('/price-bands', data)
    return response.data
  },

  async update(id: number, data: PriceBandUpdateRequest): Promise<PriceBand> {
    const response = await api.put<PriceBand>(`/price-bands/${id}`, data)
    return response.data
  },

  async delete(id: number): Promise<void> {
    await api.delete(`/price-bands/${id}`)
  },

  async getByPriceConfig(priceConfigId: number): Promise<PriceBand[]> {
    const response = await api.get<PriceBand[]>(`/price-bands/${priceConfigId}/bands`)
    return response.data
  }
}
