export interface OperationLog {
  id: string
  user_id: string
  operation_type: string
  target_type: string
  target_id: string
  old_value: any
  new_value: any
  ip_address: string
  created_at: string
}
