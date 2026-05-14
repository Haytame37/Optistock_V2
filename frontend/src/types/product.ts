export interface ProductCondition {
  min: number
  max: number
  marge_bas: number
  marge_haut: number
  temps_resistance_bas_min_h?: number
  temps_resistance_haut_min_h?: number
}

export interface ProductDetail {
  type_stockage_logistique: string
  ignore_environment: boolean
  temperature: ProductCondition
  humidite: ProductCondition
}

export interface ProductListItem {
  name: string
  type_stockage: string
}
