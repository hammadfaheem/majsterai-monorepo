export interface AdminOrganization {
  id: string
  name: string
  slug: string
  time_zone: string
  country: string | null
  currency: string
  created_at: number
  stripe_plan?: string | null
  stripe_customer_id?: string | null
  default_schedule_id?: number | null
  public_scheduler_configurations?: Record<string, unknown> | null
  tag?: string | null
  seats?: number | null
  addons?: Record<string, unknown> | null
}

export interface AdminOrganizationUpdate {
  name?: string | null
  time_zone?: string | null
  country?: string | null
  currency?: string | null
  default_schedule_id?: number | null
  tag?: string | null
  seats?: number | null
}

export interface AdminUser {
  id: string
  email: string
  name: string
  role: string | null
  created_at: number
}

export interface AdminUserUpdate {
  role?: string | null
}

export interface AuthUser {
  id: string
  email: string
  name: string
  role: string
  created_at: number
}

export interface LoginResponse {
  access_token: string
  user: AuthUser
}

export interface AnalyticsSummary {
  total_calls: number
  completed_calls: number
  average_duration_seconds: number
  total_duration_seconds: number
}
