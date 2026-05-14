import api from "./api"

export async function getAdminStats() {
  const { data } = await api.get("/admin/stats")
  return data
}

export async function getUsers(role?: string, q?: string) {
  const params = new URLSearchParams()
  if (role) params.set("role", role)
  if (q) params.set("q", q)
  const { data } = await api.get(`/admin/users?${params}`)
  return data
}

export async function getUserProfile(userId: number) {
  const { data } = await api.get(`/admin/users/${userId}`)
  return data
}

export async function toggleUserStatus(userId: number) {
  const { data } = await api.patch(`/admin/users/${userId}/status`)
  return data
}

export async function deleteUser(userId: number) {
  const { data } = await api.delete(`/admin/users/${userId}`)
  return data
}

export async function runCleanup() {
  const { data } = await api.post("/admin/maintenance/cleanup")
  return data
}

export async function purgeLocks() {
  const { data } = await api.post("/admin/maintenance/purge-locks")
  return data
}
