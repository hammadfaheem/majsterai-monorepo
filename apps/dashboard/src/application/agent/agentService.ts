import { apiClient } from '@/infrastructure/api'
import type { Agent, UpdateAgentRequest } from '@/domain/agent/types'

export class AgentService {
  /**
   * Get agent configuration for an organization
   */
  async getAgent(orgId: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(`/api/agents/${orgId}`)
    return response.data
  }

  /**
   * Get agent prompt (used by LiveKit agent)
   */
  async getAgentPrompt(orgId: string): Promise<Record<string, unknown>> {
    const response = await apiClient.get<Record<string, unknown>>(
      `/api/agents/${orgId}/prompt`
    )
    return response.data
  }

  /**
   * Update agent configuration
   */
  async updateAgent(
    orgId: string,
    data: UpdateAgentRequest
  ): Promise<Agent> {
    const response = await apiClient.put<Agent>(`/api/agents/${orgId}`, data)
    return response.data
  }
}

export const agentService = new AgentService()
