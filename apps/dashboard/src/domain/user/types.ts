/** User domain types. */

export interface User {
  id: string
  email: string
  name: string
  created_at: number
  role?: string | null
}

export interface AuthResponse {
  access_token: string
  user: User
}

export interface UserRegister {
  email: string
  name: string
  password: string
}

export interface UserLogin {
  email: string
  password: string
}
