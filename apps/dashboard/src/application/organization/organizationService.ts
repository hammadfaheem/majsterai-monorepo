import { apiClient } from '@/infrastructure/api'
import type {
  Organization,
  CreateOrganizationRequest,
  UpdateOrganizationRequest,
} from '@/domain/organization/types'

export class OrganizationService {
  async listOrganizations(): Promise<Organization[]> {
    const response = await apiClient.get<Organization[]>('/api/organizations/')
    return response.data
  }

  async getOrganization(orgId: string): Promise<Organization> {
    const response = await apiClient.get<Organization>(`/api/organizations/${orgId}`)
    return response.data
  }

  async createOrganization(
    data: CreateOrganizationRequest
  ): Promise<Organization> {
    const response = await apiClient.post<Organization>('/api/organizations/', data)
    return response.data
  }

  async updateOrganization(
    orgId: string,
    data: UpdateOrganizationRequest
  ): Promise<Organization> {
    const response = await apiClient.put<Organization>(`/api/organizations/${orgId}`, data)
    return response.data
  }
}

export const organizationService = new OrganizationService()
