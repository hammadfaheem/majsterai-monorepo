import axios, { type AxiosError, type InternalAxiosRequestConfig } from 'axios'
import { clearAuth, getStoredToken } from './auth'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getStoredToken()
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error),
)

api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      clearAuth()
      window.location.href = '/'
    }
    const message =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      'An error occurred'
    return Promise.reject(new Error(message))
  },
)
