import api from './index'
import type {
  Transfer,
  TransferCreateRequest,
  TransferQuery,
  PaginatedResponse
} from '@/types/transfer'

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
