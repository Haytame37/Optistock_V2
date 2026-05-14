import api from "./api"
import type { SearchRequest, SearchResponse, WeberResponse, SearchHistoryItem, ClientPoint } from "@/types/researcher"

export async function searchWarehouses(req: SearchRequest): Promise<SearchResponse> {
  const { data } = await api.post<SearchResponse>("/researcher/search", req)
  return data
}

export async function calculateWeber(clients: ClientPoint[]): Promise<WeberResponse> {
  const { data } = await api.post<WeberResponse>("/researcher/weber", clients)
  return data
}

export async function getSearchHistory(): Promise<SearchHistoryItem[]> {
  const { data } = await api.get("/researcher/history")
  return data
}

export async function getHistoryDetail(id: number): Promise<SearchResponse> {
  const { data } = await api.get(`/researcher/history/${id}`)
  return data
}

export async function contactOwner(warehouseId: string, ownerId: number, productName: string, message: string) {
  const { data } = await api.post(`/researcher/contact?warehouse_id=${warehouseId}&owner_id=${ownerId}&product_name=${productName}&message=${encodeURIComponent(message)}`)
  return data
}

export async function getMessages() {
  const { data } = await api.get("/researcher/messages")
  return data
}

export async function getChat(requestId: string) {
  const { data } = await api.get(`/researcher/chat/${requestId}`)
  return data
}

export async function sendChat(requestId: string, message: string) {
  const { data } = await api.post(`/researcher/chat/${requestId}?msg=${encodeURIComponent(message)}`)
  return data
}
