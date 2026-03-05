export interface Transfer {
  id: number
  customer_id: number
  from_sales_rep_id: number
  to_sales_rep_id: number
  reason: string
  status: 'pending' | 'approved' | 'rejected' | 'completed'
  approved_by: number | null
  approved_at: string | null
  created_by: number
  created_at: string
  updated_at: string
}

export interface TransferWithRelations extends Transfer {
  customer_name?: string
  from_sales_rep_name?: string
  to_sales_rep_name?: string
  approver_name?: string
}

export interface TransferCreateRequest {
  customer_id: number
  to_sales_rep_id: number
  reason: string
}

export interface TransferQuery {
  page?: number
  size?: number
  status?: string
  customer_id?: number
  from_sales_rep_id?: number
  to_sales_rep_id?: number
  created_at_start?: string
  created_at_end?: string
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
