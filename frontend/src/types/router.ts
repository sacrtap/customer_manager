export interface AppRouteRecordRaw {
  path: string
  name: string
  component?: any
  redirect?: string
  children?: AppRouteRecordRaw[]
  meta?: {
    title: string
    requiresAuth?: boolean
    icon?: string
    permissions?: string[]
    hidden?: boolean
  }
}
