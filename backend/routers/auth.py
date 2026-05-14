from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, status

from schemas.auth import LoginRequest, SignupRequest, TokenResponse, RefreshRequest
from dependencies.auth import create_access_token, create_refresh_token, decode_token, get_current_user
from utils.db import load_sql_to_dataframe

from core.auth import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["Authentification"])


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    result = authenticate_user(req.email, req.password)
    if result is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email ou mot de passe incorrect")
    if isinstance(result, list):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Multiples comptes trouvés. Veuillez préciser votre rôle.")
    user = result
    if user.get("is_active") == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Compte désactivé")
    payload = {"sub": str(user["user_id"]), "role": user["role"], "first_name": user["first_name"]}
    return TokenResponse(
        access_token=create_access_token(payload),
        refresh_token=create_refresh_token(payload),
        user={
            "user_id": user["user_id"],
            "role": user["role"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": req.email,
        },
    )


@router.post("/signup")
def signup(req: SignupRequest):
    ok, err = create_user(req.role, req.first_name, req.last_name, req.email, req.password)
    if not ok:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
    return {"message": "Compte créé avec succès", "email": req.email}


@router.post("/refresh", response_model=TokenResponse)
def refresh(req: RefreshRequest):
    payload = decode_token(req.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token invalide")
    df = load_sql_to_dataframe(
        "SELECT user_id, role, first_name, last_name, email FROM users WHERE user_id = ? AND is_active = 1",
        (int(payload["sub"]),),
    )
    if df.empty:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Utilisateur introuvable")
    user = df.iloc[0]
    new_payload = {"sub": str(user["user_id"]), "role": user["role"], "first_name": user["first_name"]}
    return TokenResponse(
        access_token=create_access_token(new_payload),
        refresh_token=create_refresh_token(new_payload),
        user={
            "user_id": int(user["user_id"]),
            "role": user["role"],
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
        },
    )


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "role": current_user["role"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "email": current_user["email"],
    }
