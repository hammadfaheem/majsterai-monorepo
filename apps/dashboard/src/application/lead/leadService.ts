/** Lead service for API calls. */

import { apiClient } from '@/infrastructure/api'
import type {
  Activity,
  ActivityCreate,
  Lead,
  LeadCreate,
  LeadUpdate,
  Note,
  NoteCreate,
} from '@/domain/lead/types'

export const leadService = {
  async listLeads(
    orgId: string,
    params?: { status?: string; limit?: number; offset?: number }
  ): Promise<Lead[]> {
    const response = await apiClient.get<Lead[]>('/api/leads', {
      params: { org_id: orgId, ...params },
    })
    return response.data
  },

  async createLead(orgId: string, data: LeadCreate): Promise<Lead> {
    const response = await apiClient.post<Lead>('/api/leads', data, {
      params: { org_id: orgId },
    })
    return response.data
  },

  async getLead(leadId: string): Promise<Lead> {
    const response = await apiClient.get<Lead>(`/api/leads/${leadId}`)
    return response.data
  },

  async updateLead(leadId: string, data: LeadUpdate): Promise<Lead> {
    const response = await apiClient.put<Lead>(`/api/leads/${leadId}`, data)
    return response.data
  },

  async addNote(leadId: string, data: NoteCreate): Promise<Note> {
    const response = await apiClient.post<Note>(`/api/leads/${leadId}/notes`, data)
    return response.data
  },

  async addActivity(leadId: string, data: ActivityCreate): Promise<Activity> {
    const response = await apiClient.post<Activity>(`/api/leads/${leadId}/activities`, data)
    return response.data
  },

  async listNotes(leadId: string): Promise<Note[]> {
    const response = await apiClient.get<Note[]>(`/api/leads/${leadId}/notes`)
    return response.data
  },

  async listActivities(leadId: string): Promise<Activity[]> {
    const response = await apiClient.get<Activity[]>(`/api/leads/${leadId}/activities`)
    return response.data
  },
}
