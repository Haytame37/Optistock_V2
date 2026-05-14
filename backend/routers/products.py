from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends
from typing import List

from schemas.product import ProductListItem, ProductDetail
from dependencies.auth import get_current_user

from utils.product_conditions import PRODUCT_CONDITIONS

router = APIRouter(prefix="/products", tags=["Produits"])


@router.get("", response_model=List[ProductListItem])
def list_products(_current_user: dict = Depends(get_current_user)):
    return [
        ProductListItem(name=name, type_stockage=props.get("type_stockage_logistique", "mixte"))
        for name, props in PRODUCT_CONDITIONS.items()
    ]


@router.get("/{product_name}", response_model=ProductDetail)
def get_product_conditions(product_name: str, _current_user: dict = Depends(get_current_user)):
    props = PRODUCT_CONDITIONS.get(product_name)
    if not props:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Produit introuvable")
    return ProductDetail(
        type_stockage_logistique=props.get("type_stockage_logistique", "mixte"),
        ignore_environment=props.get("ignore_environment", False),
        temperature=props["temperature"],
        humidite=props["humidite"],
    )
