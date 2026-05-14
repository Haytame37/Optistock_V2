export interface LoginRequest {
  email: string
  password: string
}

export interface SignupRequest {
  role: "admin" | "researcher" | "owner"
  first_name: string
  last_name: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: UserPayload
}

export interface UserPayload {
  user_id: number
  role: string
  first_name: string
  last_name: string
  email: string
}

export interface AuthState {
  user: UserPayload | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
}
