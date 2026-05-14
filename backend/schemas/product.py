from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class ProductCondition(BaseModel):
    min: float
    max: float
    marge_bas: float
    marge_haut: float
    temps_resistance_bas_min_h: Optional[float] = None
    temps_resistance_haut_min_h: Optional[float] = None


class ProductDetail(BaseModel):
    type_stockage_logistique: str
    ignore_environment: bool = False
    temperature: ProductCondition
    humidite: ProductCondition


class ProductListItem(BaseModel):
    name: str
    type_stockage: str
