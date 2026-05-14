from __future__ import annotations

import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import APIRouter, Depends, HTTPException, status
import secrets, string
from datetime import timedelta

from schemas.auth import LoginRequest, SignupRequest, TokenResponse, RefreshRequest, ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
from dependencies.auth import create_access_token, create_refresh_token, decode_token, get_current_user
from utils.db import load_sql_to_dataframe, execute_query
from utils.helpers import get_current_time

from core.auth import authenticate_user, create_user, hash_password
from core.email_service import send_otp_email

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

@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest):
    df = load_sql_to_dataframe("SELECT user_id, first_name FROM users WHERE email = ? AND is_active = 1", (req.email,))
    if df.empty:
        return {"message": "Si le compte existe, un code a été envoyé."}
    
    user = df.iloc[0]
    otp_code = "".join(secrets.choice(string.digits) for _ in range(6))
    expiry_time = (get_current_time() + timedelta(minutes=10)).strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        execute_query("UPDATE users SET otp_code = ?, otp_expiry = ? WHERE email = ?", (otp_code, expiry_time, req.email))
        print(f"DEBUG: OTP {otp_code} généré pour {req.email}")
        
        success = send_otp_email(req.email, user["first_name"], otp_code)
        if not success:
            print("DEBUG: L'envoi de l'email a échoué (send_otp_email a retourné False)")
            raise HTTPException(status_code=500, detail="Le serveur SMTP a refusé l'envoi. Vérifiez que support.optistock@gmail.com accepte les connexions.")
            
        print("DEBUG: Email envoyé avec succès !")
        return {"message": "Si le compte existe, un code a été envoyé."}
    except Exception as e:
        print(f"DEBUG ERROR: {str(e)}")
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

@router.post("/verify-otp")
def verify_otp(req: VerifyOTPRequest):
    now = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
    df = load_sql_to_dataframe(
        "SELECT user_id FROM users WHERE email = ? AND otp_code = ? AND otp_expiry > ?",
        (req.email, req.otp_code, now)
    )
    if df.empty:
        raise HTTPException(status_code=400, detail="Code invalide ou expiré")
    return {"message": "Code valide"}

@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest):
    now = get_current_time().strftime('%Y-%m-%d %H:%M:%S')
    df = load_sql_to_dataframe(
        "SELECT user_id FROM users WHERE email = ? AND otp_code = ? AND otp_expiry > ?",
        (req.email, req.otp_code, now)
    )
    if df.empty:
        raise HTTPException(status_code=400, detail="Code invalide ou expiré")
    
    new_hash = hash_password(req.new_password)
    execute_query(
        "UPDATE users SET password_hash = ?, otp_code = NULL, otp_expiry = NULL WHERE email = ?",
        (new_hash, req.email)
    )
    return {"message": "Mot de passe mis à jour avec succès"}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    return {
        "user_id": current_user["user_id"],
        "role": current_user["role"],
        "first_name": current_user["first_name"],
        "last_name": current_user["last_name"],
        "email": current_user["email"],
    }
