"use client"

import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from "react"
import { useRouter } from "next/navigation"
import type { AuthState, UserPayload } from "@/types/auth"
import { login as apiLogin, signup as apiSignup } from "@/services/auth.service"
import type { LoginRequest, SignupRequest } from "@/types/auth"

interface AuthContextType extends AuthState {
  login: (req: LoginRequest) => Promise<void>
  signup: (req: SignupRequest) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    accessToken: null,
    refreshToken: null,
    isAuthenticated: false,
  })
  const [loading, setLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const accessToken = localStorage.getItem("access_token")
    const refreshToken = localStorage.getItem("refresh_token")
    const userStr = localStorage.getItem("user")
    if (accessToken && refreshToken && userStr) {
      try {
        setState({
          user: JSON.parse(userStr),
          accessToken,
          refreshToken,
          isAuthenticated: true,
        })
      } catch { /* ignore */ }
    }
    setLoading(false)
  }, [])

  const login = useCallback(async (req: LoginRequest) => {
    const res = await apiLogin(req)
    localStorage.setItem("access_token", res.access_token)
    localStorage.setItem("refresh_token", res.refresh_token)
    localStorage.setItem("user", JSON.stringify(res.user))
    setState({
      user: res.user,
      accessToken: res.access_token,
      refreshToken: res.refresh_token,
      isAuthenticated: true,
    })
  }, [])

  const signup = useCallback(async (req: SignupRequest) => {
    await apiSignup(req)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user")
    setState({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false })
    router.push("/login")
  }, [router])

  return (
    <AuthContext.Provider value={{ ...state, login, signup, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error("useAuth must be used within AuthProvider")
  return ctx
}
