import api from "./api"
import type { LoginRequest, SignupRequest, TokenResponse } from "@/types/auth"

export async function login(req: LoginRequest): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/login", req)
  return data
}

export async function signup(req: SignupRequest): Promise<{ message: string }> {
  const { data } = await api.post("/auth/signup", req)
  return data
}

export async function refreshToken(token: string): Promise<TokenResponse> {
  const { data } = await api.post<TokenResponse>("/auth/refresh", { refresh_token: token })
  return data
}

export async function getMe() {
  const { data } = await api.get("/auth/me")
  return data
}
