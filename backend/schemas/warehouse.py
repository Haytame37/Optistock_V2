from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class WarehouseBase(BaseModel):
    name: str
    address: str
    volume_m3: float
    latitude: float
    longitude: float


class WarehouseCreate(WarehouseBase):
    pass


class WarehouseUpdate(WarehouseBase):
    pass


class WarehouseResponse(WarehouseBase):
    warehouse_id: str
    owner_id: Optional[int] = None
    status: str
    is_rented: bool = False


class WarehouseListItem(BaseModel):
    id: str
    name: str
    address: str
    volume: float
    lat: float
    lon: float
    gps: str
    status: str
    is_rented: bool
