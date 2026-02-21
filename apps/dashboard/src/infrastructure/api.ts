import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios'

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
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor: Handle errors globally
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('auth_token')
      // Could redirect to login page here if needed
      window.location.href = '/login'
    }
    
    // Extract error message
    const errorMessage =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'An error occurred'
    
    return Promise.reject(new Error(errorMessage))
  }
)
