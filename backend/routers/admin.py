from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from dependencies.auth import get_current_user
from schemas.admin import AdminStats, UserSummary, UserProfileDetails, MaintenanceReport
from utils.db import load_sql_to_dataframe, execute_query, get_db_connection
from core.maintenance import process_inactive_users

router = APIRouter(prefix="/admin", tags=["Admin"])

def check_admin(current_user: dict):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Accès réservé aux administrateurs"
        )

@router.get("/stats", response_model=AdminStats)
def get_admin_stats(current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    
    # User stats
    df_u = load_sql_to_dataframe("SELECT role, COUNT(*) as count FROM users GROUP BY role")
    user_dist = {row["role"]: row["count"] for _, row in df_u.iterrows()}
    total_users = sum(user_dist.values())
    
    # Warehouse stats
    df_w = load_sql_to_dataframe("SELECT status, COUNT(*) as count FROM warehouses GROUP BY status")
    wh_dist = {row["status"]: row["count"] for _, row in df_w.iterrows()}
    total_wh = sum(wh_dist.values())
    
    # Reservation stats
    df_r = load_sql_to_dataframe("SELECT status, COUNT(*) as count FROM reservations GROUP BY status")
    res_dist = {row["status"]: row["count"] for _, row in df_r.iterrows()}
    total_res = sum(res_dist.values())
    
    # Activity history
    df_hist = load_sql_to_dataframe("""
        SELECT DATE(created_at) as date, COUNT(*) as count 
        FROM reservations 
        GROUP BY DATE(created_at) 
        ORDER BY date DESC LIMIT 30
    """)
    activity_history = df_hist.to_dict(orient="records")
    
    return AdminStats(
        total_users=total_users,
        total_warehouses=total_wh,
        total_reservations=total_res,
        user_distribution=user_dist,
        warehouse_distribution=wh_dist,
        activity_history=activity_history,
        all_warehouses=load_sql_to_dataframe("""
            SELECT w.warehouse_id as id, w.name, w.iot_token, u.first_name || ' ' || u.last_name as owner_name 
            FROM warehouses w 
            JOIN users u ON w.owner_id = u.user_id
        """).to_dict(orient="records")
    )

@router.get("/users", response_model=List[UserSummary])
def list_users(role: Optional[str] = None, q: Optional[str] = None, current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    
    query = "SELECT user_id, first_name, last_name, email, role, is_active, created_at FROM users"
    conditions = []
    params = []
    
    if role:
        conditions.append("role = ?")
        params.append(role)
    if q:
        conditions.append("(email LIKE ? OR first_name LIKE ? OR last_name LIKE ?)")
        search = f"%{q}%"
        params.extend([search, search, search])
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    df = load_sql_to_dataframe(query, tuple(params))
    return df.to_dict(orient="records")

@router.get("/users/{user_id}", response_model=UserProfileDetails)
def get_user_profile(user_id: int, current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    
    # Basic info
    df_user = load_sql_to_dataframe("SELECT * FROM users WHERE user_id = ?", (user_id,))
    if df_user.empty:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    u = df_user.iloc[0]
    
    # Warehouses
    df_wh = load_sql_to_dataframe("SELECT * FROM warehouses WHERE owner_id = ?", (user_id,))
    
    # Reservations
    df_res = load_sql_to_dataframe("""
        SELECT r.*, w.name as warehouse_name 
        FROM reservations r 
        JOIN warehouses w ON r.warehouse_id = w.warehouse_id 
        WHERE r.researcher_id = ? OR w.owner_id = ?
    """, (user_id, user_id))
    
    # Contact requests
    df_req = load_sql_to_dataframe("""
        SELECT * FROM contact_requests 
        WHERE researcher_id = ? OR owner_id = ?
    """, (user_id, user_id))
    
    # Messages
    df_msg = load_sql_to_dataframe("""
        SELECT * FROM chat_messages 
        WHERE sender_id = ? 
        ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    
    return UserProfileDetails(
        user_id=u["user_id"],
        first_name=u["first_name"],
        last_name=u["last_name"],
        email=u["email"],
        role=u["role"],
        is_active=bool(u["is_active"]),
        created_at=str(u["created_at"]),
        warehouses=df_wh.to_dict(orient="records"),
        reservations=df_res.to_dict(orient="records"),
        contact_requests=df_req.to_dict(orient="records"),
        recent_messages=df_msg.to_dict(orient="records"),
        last_activity=None # Could be computed
    )

@router.patch("/users/{user_id}/status")
def toggle_user_status(user_id: int, current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    if user_id == int(current_user["user_id"]):
        raise HTTPException(status_code=400, detail="Action impossible sur soi-même")
        
    df = load_sql_to_dataframe("SELECT is_active FROM users WHERE user_id = ?", (user_id,))
    if df.empty:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    
    new_status = 0 if df.iloc[0]["is_active"] == 1 else 1
    execute_query("UPDATE users SET is_active = ? WHERE user_id = ?", (new_status, user_id))
    return {"success": True, "is_active": bool(new_status)}

@router.delete("/users/{user_id}")
def delete_user(user_id: int, current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    if user_id == int(current_user["user_id"]):
        raise HTTPException(status_code=400, detail="Action impossible sur soi-même")
        
    execute_query("DELETE FROM users WHERE user_id = ?", (user_id,))
    return {"success": True}

@router.post("/maintenance/cleanup", response_model=MaintenanceReport)
def run_maintenance_cleanup(current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    count, emails = process_inactive_users(current_user_id=int(current_user["user_id"]))
    return MaintenanceReport(count=count, details=emails, success=True)

@router.post("/maintenance/purge-locks")
def purge_locks(current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    execute_query("UPDATE warehouses SET status = 'available' WHERE status = 'locked'")
    execute_query("DELETE FROM reservations WHERE status = 'locked'")
    return {"success": True}
@router.patch("/warehouses/{warehouse_id}/iot-token")
def update_iot_token(warehouse_id: str, token_data: dict, current_user: dict = Depends(get_current_user)):
    check_admin(current_user)
    token = token_data.get("token")
    execute_query("UPDATE warehouses SET iot_token = ? WHERE warehouse_id = ?", (token, warehouse_id))
    return {"success": True}
