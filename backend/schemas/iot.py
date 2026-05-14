from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class IoTReading(BaseModel):
    recorded_at: str
    temp_sensor_1: Optional[float] = None
    temp_sensor_2: Optional[float] = None
    temp_sensor_3: Optional[float] = None
    hum_sensor_1: Optional[float] = None
    hum_sensor_2: Optional[float] = None
    hum_sensor_3: Optional[float] = None


class IoTKPI(BaseModel):
    current_temp: float
    current_hum: float
    avg_temp: float
    avg_hum: float
    temp_status: str
    hum_status: str
    temp_color: str
    hum_color: str
    stability_score: int
    consecutive_t_bad: int
    consecutive_h_bad: int
    tolerance_t: float
    tolerance_h: float
    trigger_alert: bool


class IoTReadingResponse(BaseModel):
    readings: list[IoTReading]
    kpi: IoTKPI
    total: int
    index: int


class IoTImportResponse(BaseModel):
    success: bool
    message: str
    rows_imported: int = 0
