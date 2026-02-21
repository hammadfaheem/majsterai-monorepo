import { apiClient } from '@/infrastructure/api'

export interface Appointment {
  id: string
  org_id: string
  start: number
  end: number
  title: string | null
  status: string
  created_at: number
  updated_at: number
}

export const appointmentService = {
  async list(orgId: string, params?: { limit?: number }): Promise<Appointment[]> {
    const { data } = await apiClient.get<Appointment[]>('/api/appointments/', {
      params: { org_id: orgId, limit: params?.limit ?? 100 },
    })
    return data
  },
}
