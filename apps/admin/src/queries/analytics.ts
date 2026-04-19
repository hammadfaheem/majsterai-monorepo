import { queryOptions } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { AnalyticsSummary } from '@/types/api'

export const analyticsQueryOptions = (orgId: string) =>
  queryOptions({
    queryKey: ['admin', 'analytics', orgId],
    queryFn: () =>
      api
        .get<AnalyticsSummary>('/api/call-history/analytics/summary', {
          params: { org_id: orgId },
        })
        .then((r) => r.data),
    enabled: !!orgId,
  })
