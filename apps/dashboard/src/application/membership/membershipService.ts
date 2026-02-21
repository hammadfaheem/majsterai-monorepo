/** Membership service for API calls. */

import { apiClient } from '@/infrastructure/api'
import type {
  AddMemberRequest,
  Membership,
  UpdateMemberRoleRequest,
} from '@/domain/membership/types'

export const membershipService = {
  async listMembers(orgId: string): Promise<Membership[]> {
    const response = await apiClient.get<Membership[]>(`/api/memberships/${orgId}`)
    return response.data
  },

  async addMember(orgId: string, data: AddMemberRequest): Promise<Membership> {
    const response = await apiClient.post<Membership>(`/api/memberships/${orgId}`, data)
    return response.data
  },

  async updateMemberRole(
    orgId: string,
    userId: string,
    data: UpdateMemberRoleRequest
  ): Promise<Membership> {
    const response = await apiClient.put<Membership>(
      `/api/memberships/${orgId}/${userId}`,
      data
    )
    return response.data
  },

  async removeMember(orgId: string, userId: string): Promise<void> {
    await apiClient.delete(`/api/memberships/${orgId}/${userId}`)
  },
}
