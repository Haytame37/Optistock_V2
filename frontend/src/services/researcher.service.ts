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
