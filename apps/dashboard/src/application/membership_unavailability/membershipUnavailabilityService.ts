/** Membership unavailability (time off) service. */

import { apiClient } from '@/infrastructure/api'

export interface MembershipUnavailability {
  id: string
  member_id: string
  start_date: number | null
  end_date: number | null
  start_time: number | null
  end_time: number | null
  recurrence_type: string | null
  days_of_week: string[] | null
  created_at: number
  updated_at: number
}

export interface MembershipUnavailabilityCreate {
  member_id: string
  start_date?: number | null
  end_date?: number | null
  start_time?: number | null
  end_time?: number | null
  recurrence_type?: string | null
  days_of_week?: string[] | null
}

export const membershipUnavailabilityService = {
  async listByOrg(orgId: string): Promise<MembershipUnavailability[]> {
    const { data } = await apiClient.get<MembershipUnavailability[]>(
      `/api/membership-unavailability/org/${orgId}`
    )
    return data
  },

  async listByMember(memberId: string): Promise<MembershipUnavailability[]> {
    const { data } = await apiClient.get<MembershipUnavailability[]>(
      `/api/membership-unavailability/member/${memberId}`
    )
    return data
  },

  async create(payload: MembershipUnavailabilityCreate): Promise<MembershipUnavailability> {
    const { data } = await apiClient.post<MembershipUnavailability>(
      '/api/membership-unavailability/',
      payload
    )
    return data
  },

  async update(
    id: string,
    payload: Partial<MembershipUnavailabilityCreate>
  ): Promise<MembershipUnavailability> {
    const { data } = await apiClient.put<MembershipUnavailability>(
      `/api/membership-unavailability/${id}`,
      payload
    )
    return data
  },

  async delete(id: string): Promise<void> {
    await apiClient.delete(`/api/membership-unavailability/${id}`)
  },
}
