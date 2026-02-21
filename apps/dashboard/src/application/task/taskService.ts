/** Task service for API calls. */

import { apiClient } from '@/infrastructure/api'

export interface Task {
  id: string
  org_id: string
  title: string
  is_completed: boolean
  type: string | null
  inquiry_id: string | null
  lead_id: string | null
  assigned_member_id: string | null
  is_created_by_sophiie: boolean
  created_at: number
  updated_at: number
}

export interface TaskCreate {
  org_id: string
  title: string
  is_completed?: boolean
  type?: string | null
  inquiry_id?: string | null
  lead_id?: string | null
  assigned_member_id?: string | null
}

export const taskService = {
  async listTasks(
    orgId: string,
    params?: { lead_id?: string }
  ): Promise<Task[]> {
    const response = await apiClient.get<Task[]>('/api/tasks/', {
      params: { org_id: orgId, ...params },
    })
    return response.data
  },

  async createTask(data: TaskCreate): Promise<Task> {
    const response = await apiClient.post<Task>('/api/tasks/', {
      ...data,
      is_completed: data.is_completed ?? false,
    })
    return response.data
  },

  async updateTask(taskId: string, data: { title?: string; is_completed?: boolean }): Promise<Task> {
    const response = await apiClient.put<Task>(`/api/tasks/${taskId}`, data)
    return response.data
  },

  async deleteTask(taskId: string): Promise<void> {
    await apiClient.delete(`/api/tasks/${taskId}`)
  },
}
