import { createSlice } from '@reduxjs/toolkit'
import type { User } from '@/domain/user/types'

const AUTH_TOKEN_KEY = 'auth_token'

function getStoredToken(): string | null {
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

export interface AuthState {
  token: string | null
  user: User | null
}

const initialState: AuthState = {
  token: getStoredToken(),
  user: null,
}

export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    setCredentials: (state, action: { payload: { token: string; user: User } }) => {
      state.token = action.payload.token
      state.user = action.payload.user
      localStorage.setItem(AUTH_TOKEN_KEY, action.payload.token)
    },
    setUser: (state, action: { payload: User }) => {
      state.user = action.payload
    },
    logout: (state) => {
      state.token = null
      state.user = null
      localStorage.removeItem(AUTH_TOKEN_KEY)
    },
  },
})

export const { setCredentials, setUser, logout } = authSlice.actions
export const authReducer = authSlice.reducer
