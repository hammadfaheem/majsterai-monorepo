/** User service for API calls. */

import { apiClient } from '@/infrastructure/api'
import type { AuthResponse, User, UserLogin, UserRegister } from '@/domain/user/types'

export const userService = {
  async register(data: UserRegister): Promise<AuthResponse> {
    const response = await apiClient.post<AuthResponse>('/api/auth/register', data)
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
