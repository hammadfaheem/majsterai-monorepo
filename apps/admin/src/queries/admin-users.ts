import { queryOptions } from '@tanstack/react-query'
import { api } from '@/utils/api'
import type { AdminUser } from '@/types/api'

export const adminUsersQueryOptions = () =>
  queryOptions({
    queryKey: ['admin', 'users'],
    queryFn: () => api.get<AdminUser[]>('/api/admin/users').then((r) => r.data),
  })
