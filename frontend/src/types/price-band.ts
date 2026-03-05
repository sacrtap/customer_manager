/** 价格区间类型定义 */

/** 价值等级 */
export enum TierLevel {
  S = 'S',
  A = 'A',
  B = 'B',
  C = 'C',
  D = 'D',
}

/** 健康度 */
export enum HealthStatus {
  ACTIVE = 'active',
  AT_RISK = 'at_risk',
  ZOMBIE = 'zombie',
}

/** 价格区间 */
export interface PriceBand {
  id: number
  name: string
  code: string
  description?: string
  price_config_id?: number
  min_quantity?: number
  max_quantity?: number
  min_amount?: number
  max_amount?: number
  unit_price?: number
  discount_rate?: number
  final_price?: number
  priority: number
  is_active: boolean
  valid_from?: string
  valid_until?: string
  created_at: string
  updated_at?: string
}

/** 价格区间列表响应 */
export interface PriceBandListResponse {
  items: PriceBand[]
  total: number
  page: number
  page_size: number
}

/** 价格区间筛选条件 */
export interface PriceBandFilters {
  code?: string
  name?: string
  price_config_id?: number
  is_active?: boolean
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

/** 价格区间创建请求 */
export interface PriceBandCreateRequest {
  name: string
  code: string
  description?: string
  price_config_id?: number
  min_quantity?: number
  max_quantity?: number
  min_amount?: number
  max_amount?: number
  unit_price?: number
  discount_rate?: number
  final_price?: number
  priority?: number
  is_active?: boolean
  valid_from?: string
  valid_until?: string
}

/** 价格区间更新请求 */
export interface PriceBandUpdateRequest {
  name?: string
  code?: string
  description?: string
  price_config_id?: number
  min_quantity?: number
  max_quantity?: number
  min_amount?: number
  max_amount?: number
  unit_price?: number
  discount_rate?: number
  final_price?: number
  priority?: number
  is_active?: boolean
  valid_from?: string
  valid_until?: string
}
