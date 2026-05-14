export interface IoTReading {
  recorded_at: string
  temp_sensor_1?: number
  temp_sensor_2?: number
  temp_sensor_3?: number
  hum_sensor_1?: number
  hum_sensor_2?: number
  hum_sensor_3?: number
}

export interface IoTKPI {
  current_temp: number
  current_hum: number
  avg_temp: number
  avg_hum: number
  temp_status: string
  hum_status: string
  temp_color: string
  hum_color: string
  stability_score: number
  consecutive_t_bad: number
  consecutive_h_bad: number
  tolerance_t: number
  tolerance_h: number
  trigger_alert: boolean
}

export interface IoTReadingResponse {
  readings: IoTReading[]
  kpi: IoTKPI
  total: number
  index: number
}
