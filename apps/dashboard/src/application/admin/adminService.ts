/** Admin (superadmin) API service. */

import { apiClient } from '@/infrastructure/api'

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

export const adminService = {
  async listOrganizations(): Promise<AdminOrganization[]> {
    const { data } = await apiClient.get<AdminOrganization[]>('/api/admin/organizations')
    return data
  },

  async getOrganization(orgId: string): Promise<AdminOrganization> {
    const { data } = await apiClient.get<AdminOrganization>(`/api/admin/organizations/${orgId}`)
    return data
  },

  async updateOrganization(orgId: string, payload: AdminOrganizationUpdate): Promise<AdminOrganization> {
    const { data } = await apiClient.put<AdminOrganization>(`/api/admin/organizations/${orgId}`, payload)
    return data
  },

  async listUsers(): Promise<AdminUser[]> {
    const { data } = await apiClient.get<AdminUser[]>('/api/admin/users')
    return data
  },

  async getUser(userId: string): Promise<AdminUser> {
    const { data } = await apiClient.get<AdminUser>(`/api/admin/users/${userId}`)
    return data
  },

  async updateUser(userId: string, payload: AdminUserUpdate): Promise<AdminUser> {
    const { data } = await apiClient.patch<AdminUser>(`/api/admin/users/${userId}`, payload)
    return data
  },
}
