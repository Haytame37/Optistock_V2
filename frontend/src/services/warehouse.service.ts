import api from "./api"
import type { WarehouseCreate, WarehouseData } from "@/types/warehouse"

export async function getMyWarehouses() {
  const { data } = await api.get("/warehouses/my")
  return data
}

export async function getOwnerWarehouses() {
  const { data } = await api.get("/warehouses/owner")
  return data
}

export async function createWarehouse(wh: WarehouseCreate) {
  const { data } = await api.post("/warehouses", wh)
  return data
}

export async function getWarehouse(id: string) {
  const { data } = await api.get(`/warehouses/${id}`)
  return data
}

export async function updateWarehouse(id: string, wh: WarehouseCreate) {
  const { data } = await api.put(`/warehouses/${id}`, wh)
  return data
}

export async function deleteWarehouse(id: string) {
  const { data } = await api.delete(`/warehouses/${id}`)
  return data
}
