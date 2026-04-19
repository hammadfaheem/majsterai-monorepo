import { queryOptions } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { AdminOrganization } from '@/types/api'

export const adminOrgsQueryOptions = () =>
  queryOptions({
    queryKey: ['admin', 'organizations'],
    queryFn: () =>
      api.get<AdminOrganization[]>('/api/admin/organizations').then((r) => r.data),
  })

export const adminOrgQueryOptions = (orgId: string) =>
  queryOptions({
    queryKey: ['admin', 'organizations', orgId],
    queryFn: () =>
      api.get<AdminOrganization>(`/api/admin/organizations/${orgId}`).then((r) => r.data),
  })
