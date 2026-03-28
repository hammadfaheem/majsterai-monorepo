import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

import { store } from '@/store'
import { logout } from '@/store/authSlice'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor: Add auth token if available
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('auth_token')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor: Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized – clear Redux auth state (also clears localStorage via authSlice)
      // ProtectedRoute will redirect to /login once token is cleared
      store.dispatch(logout())
    }

    const errorMessage =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'An error occurred'

    return Promise.reject(new Error(errorMessage))
  }
)
