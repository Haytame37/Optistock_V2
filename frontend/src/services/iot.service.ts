import api from "./api"
import type { IoTReadingResponse } from "@/types/iot"

export async function getIoTReadings(warehouseId: string, product?: string, index?: number): Promise<IoTReadingResponse> {
  const params = new URLSearchParams()
  if (product) params.set("product", product)
  if (index !== undefined) params.set("index", String(index))
  const { data } = await api.get(`/iot/readings/${warehouseId}?${params}`)
  return data
}

export async function getIoTKPI(warehouseId: string, product?: string) {
  const params = product ? `?product=${product}` : ""
  const { data } = await api.get(`/iot/kpi/${warehouseId}${params}`)
  return data
}

export async function importIoTData(warehouseId: string, file: File) {
  const formData = new FormData()
  formData.append("file", file)
  const { data } = await api.post(`/iot/import/${warehouseId}`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  })
  return data
}
