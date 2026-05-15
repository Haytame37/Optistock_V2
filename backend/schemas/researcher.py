from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ClientPoint(BaseModel):
    name: str
    latitude: float
    longitude: float
    demand: float = 1.0


class MyWarehouse(BaseModel):
    id_entrepot: str
    nom: str
    adresse: str
    latitude: float
    longitude: float
    volume_m3: float = 0.0


class SearchRequest(BaseModel):
    product: str
    volume: float = 0.0
    duration_days: int = 7
    cost_weight: float = 0.5
    dist_weight: float = 0.5
    warehouses: list[MyWarehouse] = []
    clients: list[ClientPoint] = []
    quick_search: bool = False


class SearchResultItem(BaseModel):
    id: str
    owner_id: Optional[int] = None
    nom: str
    adresse: str
    avg_temp: float
    avg_hum: float
    latitude: float
    longitude: float
    distance_km: Optional[float] = None
    score_logistique: float
    status: str


class SearchResponse(BaseModel):
    results: list[SearchResultItem]
    product: str
    volume: float
    duration_days: int
    saved_points: int = 0
    saved_warehouses: int = 0


class WeberResponse(BaseModel):
    lat_opt: float
    lon_opt: float
    avg_distance_km: float


class SearchHistoryItem(BaseModel):
    id: int
    product_name: str
    volume: float
    duration_days: int
    cost_weight: Optional[float] = None
    dist_weight: Optional[float] = None
    results_json: str
    created_at: str


class ContactRequestCreate(BaseModel):
    warehouse_id: str
    owner_id: int
    product_name: str
    message: str


class ChatMessageSend(BaseModel):
    message: str
