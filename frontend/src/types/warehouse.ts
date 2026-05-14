export interface WarehouseData {
  warehouse_id: string
  name: string
  address: string
  volume_m3: number
  latitude: number
  longitude: number
  status?: string
  is_rented?: boolean
}

export interface WarehouseCreate {
  name: string
  address: string
  volume_m3: number
  latitude: number
  longitude: number
}
