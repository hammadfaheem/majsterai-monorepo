/** Call history service for API calls. */

import { apiClient } from '@/infrastructure/api'
import type {
  CallAnalytics,
  CallDetails,
  CallHistory,
} from '@/domain/call_history/types'

export const callHistoryService = {
  async listCalls(
    orgId: string,
    params?: { limit?: number; offset?: number }
  ): Promise<CallHistory[]> {
    const response = await apiClient.get<CallHistory[]>('/api/call-history', {
      params: { org_id: orgId, ...params },
    })
    return response.data
  },

  async getCallDetails(roomName: string): Promise<CallDetails> {
    const response = await apiClient.get<CallDetails>(`/api/call-history/${roomName}`)
    return response.data
  },

  async getAnalytics(orgId: string): Promise<CallAnalytics> {
    const response = await apiClient.get<CallAnalytics>('/api/call-history/analytics/summary', {
      params: { org_id: orgId },
    })
    return response.data
  },

  async updateCallStatus(roomName: string, status: string): Promise<CallHistory> {
    const response = await apiClient.put<CallHistory>(
      `/api/call-history/${roomName}/status`,
      null,
      {
        params: { status },
      }
    )
    return response.data
  },
}
