export interface ClientPoint {
  name: string
  latitude: number
  longitude: number
  demand: number
}

export interface MyWarehouse {
  id_entrepot: string
  nom: string
  adresse: string
  latitude: number
  longitude: number
  volume_m3: number
}

export interface SearchRequest {
  product: string
  volume: number
  duration_days: number
  warehouses: MyWarehouse[]
  clients: ClientPoint[]
  quick_search: boolean
  cost_weight?: number
  dist_weight?: number
}

export interface SearchResultItem {
  id: string
  owner_id?: number
  nom: string
  adresse: string
  avg_temp: number
  avg_hum: number
  latitude: number
  longitude: number
  distance_km?: number
  score_logistique: number
  status: string
}

export interface SearchResponse {
  id?: number
  results: SearchResultItem[]
  product: string
  volume: number
  duration_days: number
  saved_points: number
  saved_warehouses: number
}

export interface WeberResponse {
  lat_opt: number
  lon_opt: number
  avg_distance_km: number
}

export interface SearchHistoryItem {
  id: number
  product_name: string
  volume: number
  duration_days: number
  results_json: string
  created_at: string
}
