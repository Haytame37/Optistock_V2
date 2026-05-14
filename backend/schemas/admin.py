from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional

class AdminStats(BaseModel):
    total_users: int
    total_warehouses: int
    total_reservations: int
    system_score: float
    user_distribution: dict # role -> count
    warehouse_distribution: dict # status -> count
    activity_history: List[dict] # {date, count}

class UserSummary(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    created_at: str

class UserProfileDetails(BaseModel):
    user_id: int
    first_name: str
    last_name: str
    email: str
    role: str
    is_active: bool
    created_at: str
    warehouses: List[dict]
    reservations: List[dict]
    contact_requests: List[dict]
    recent_messages: List[dict]
    last_activity: Optional[str]

class MaintenanceReport(BaseModel):
    count: int
    details: List[str]
    success: bool
