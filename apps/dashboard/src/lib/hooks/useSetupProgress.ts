import { useQueries } from '@tanstack/react-query'
import { useOrganization } from '@/application/organization/organizationContext'
import { agentService } from '@/application/agent/agentService'
import { membershipService } from '@/application/membership/membershipService'
import { apiClient } from '@/infrastructure/api'

const TOTAL_REQUIRED = 6

export function useSetupProgress() {
  const { currentOrganization } = useOrganization()
  const orgId = currentOrganization?.id ?? ''

  const results = useQueries({
    queries: [
      {
        queryKey: ['agent', orgId],
        queryFn: () => agentService.getAgent(orgId),
        enabled: !!orgId,
      },
      {
        queryKey: ['trade-services', orgId],
        queryFn: async () => {
          const { data } = await apiClient.get<unknown[]>(
            `/api/trade-services/org/${orgId}`
          )
          return data
        },
        enabled: !!orgId,
      },
      {
        queryKey: ['scenarios', orgId],
        queryFn: async () => {
          const { data } = await apiClient.get<unknown[]>(
            `/api/scenarios/org/${orgId}`
          )
          return data
        },
        enabled: !!orgId,
      },
      {
        queryKey: ['memberships', orgId],
        queryFn: () => membershipService.listMembers(orgId),
        enabled: !!orgId,
      },
      {
        queryKey: ['departments', orgId],
        queryFn: async () => {
          const { data } = await apiClient.get<unknown[]>(
            `/api/departments/org/${orgId}`
          )
          return data
        },
        enabled: !!orgId,
      },
      {
        queryKey: ['transfers', orgId],
        queryFn: async () => {
          const { data } = await apiClient.get<unknown[]>(
            `/api/transfers/org/${orgId}`
          )
          return data
        },
        enabled: !!orgId,
      },
    ],
  })

  const [agent, services, scenarios, team, departments, transfers] = results

  const agentComplete =
    agent.data &&
    Boolean(
      (agent.data as { prompt?: string; name?: string }).prompt?.trim() ||
        (agent.data as { prompt?: string; name?: string }).name?.trim()
    )
  const servicesComplete =
    services.data && Array.isArray(services.data) && services.data.length > 0
  const scenariosComplete =
    scenarios.data && Array.isArray(scenarios.data) && scenarios.data.length > 0
  const teamComplete =
    team.data && Array.isArray(team.data) && team.data.length > 0
  const departmentsComplete =
    departments.data &&
    Array.isArray(departments.data) &&
    departments.data.length > 0
  const transfersComplete =
    transfers.data && Array.isArray(transfers.data) && transfers.data.length > 0

  const completedCards = [
    agentComplete,
    servicesComplete,
    scenariosComplete,
    teamComplete,
    departmentsComplete,
    transfersComplete,
  ].filter(Boolean).length

  const progress =
    TOTAL_REQUIRED > 0 ? (completedCards / TOTAL_REQUIRED) * 100 : 0
  const isPending = results.some((r) => r.isPending)

  return {
    completedCards,
    totalCards: TOTAL_REQUIRED,
    progress,
    isPending,
  }
}
