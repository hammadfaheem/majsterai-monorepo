export interface Organization {
  id: string
  name: string
  slug: string
  time_zone: string
  country: string | null
  currency: string
  created_at: number
  settings?: Record<string, unknown> | null
  tag?: string | null
  seats?: number | null
  default_schedule_id?: number | null
}

export interface CreateOrganizationRequest {
  name: string
  time_zone?: string
  country?: string | null
  currency?: string
}

export interface UpdateOrganizationRequest {
  name?: string | null
  time_zone?: string | null
  country?: string | null
  currency?: string | null
  settings?: Record<string, unknown> | null
  default_schedule_id?: number | null
  tag?: string | null
  seats?: number | null
}
