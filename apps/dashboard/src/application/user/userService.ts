/** User service for API calls. */

import { apiClient } from '@/infrastructure/api'
import type { AuthResponse, User, UserLogin, UserRegister } from '@/domain/user/types'

export const userService = {
  async register(data: UserRegister): Promise<AuthResponse> {
    const payload = {
      email: data.email,
      name: data.name,
      password: data.password,
      ...(data.org_name && { org_name: data.org_name }),
      ...(data.time_zone && { time_zone: data.time_zone }),
      ...(data.country && { country: data.country }),
      ...(data.currency && { currency: data.currency }),
    }
    const response = await apiClient.post<AuthResponse>('/api/auth/register', payload)
    return response.data
  },

  async login(data: UserLogin): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/login', data)
    return response.data
  },

  async getCurrentUser(): Promise<User> {
    const response = await apiClient.get<User>('/api/auth/me')
    return response.data
  },

  async logout(): Promise<void> {
    await apiClient.post('/api/auth/logout')
  },
}
