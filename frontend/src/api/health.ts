import api from './index'

export interface HealthDashboard {
  total_customers: number
  active_count: number
  risk_count: number
  zombie_count: number
  health_score_avg: number
  tier_distribution: Record<string, number>
  health_trend: Array<{ date: string; score: number }>
  value_distribution: Array<{ tier_level: string; count: number }>
}

export interface RiskCustomer {
  id: number
  name: string
  code: string
  health_score: number
  risk_factors: string[]
  last_active_at: string
  tier_level: string
  annual_consumption: number
  contact_person: string
  contact_phone: string
}

export interface ZombieCustomer {
  id: number
  name: string
  code: string
  health_score: number
  last_active_at: string
  inactive_days: number
  tier_level: string
  annual_consumption: number
  contact_person: string
  contact_phone: string
}

export interface HealthQuery {
  page?: number
  size?: number
  keyword?: string
  tier_levels?: string[]
  min_health_score?: number
  max_health_score?: number
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export const healthApi = {
  async getDashboard(): Promise<HealthDashboard> {
    const response = await api.get<HealthDashboard>('/health/dashboard')
    return response.data
  },

  async getRisks(query: HealthQuery): Promise<PaginatedResponse<RiskCustomer>> {
    const response = await api.get<PaginatedResponse<RiskCustomer>>('/health/risks', {
      params: query
    })
    return response.data
  },

  async getZombies(query: HealthQuery): Promise<PaginatedResponse<ZombieCustomer>> {
    const response = await api.get<PaginatedResponse<ZombieCustomer>>('/health/zombies', {
      params: query
    })
    return response.data
  },

  async sendAlerts(customerIds: number[], message: string): Promise<void> {
    await api.post('/health/alerts', { customer_ids: customerIds, message })
  }
}
