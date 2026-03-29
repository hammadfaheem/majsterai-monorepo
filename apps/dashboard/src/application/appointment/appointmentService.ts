import { apiClient } from '@/infrastructure/api'

export interface Appointment {
  id: string
  org_id: string
  serial_id: number | null
  start: number
  end: number
  title: string | null
  description: string | null
  status: string
  lead_id: string | null
  inquiry_id: string | null
  trade_service_id: number | null
  lead_address_id: number | null
  selected_calendar_id: number | null
  attendees: unknown[] | null
  is_rescheduled: boolean
  is_created_by_sophiie: boolean
  notes: string | null
  customer_notes: string | null
  customer_cancellation_reason: string | null
  summary: string | null
  photos: unknown[] | null
  created_at: number
  updated_at: number
}

export interface AppointmentUpdate {
  start?: number
  end?: number
  title?: string
  description?: string
  status?: string
  lead_id?: string
  notes?: string
  reference_id?: string
  is_rescheduled?: boolean
}

export const appointmentService = {
  async list(orgId: string, params?: { limit?: number }): Promise<Appointment[]> {
    const { data } = await apiClient.get<Appointment[]>('/api/appointments/', {
      params: { org_id: orgId, limit: params?.limit ?? 100 },
    })
    return data
  },

  async listByRange(orgId: string, startMs: number, endMs: number): Promise<Appointment[]> {
    const { data } = await apiClient.get<Appointment[]>('/api/appointments/', {
      params: { org_id: orgId, start_from: startMs, end_before: endMs, limit: 500 },
    })
    return data
  },

  async update(id: string, payload: AppointmentUpdate): Promise<Appointment> {
    const { data } = await apiClient.put<Appointment>(`/api/appointments/${id}`, payload)
    return data
  },
}
