from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


class ContactRequestResponse(BaseModel):
    request_id: str
    warehouse_id: str
    warehouse_name: Optional[str] = None
    warehouse_address: Optional[str] = None
    owner_id: Optional[int] = None
    owner_first_name: Optional[str] = None
    product_name: Optional[str] = None
    message: Optional[str] = None
    status: str
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ChatMessageResponse(BaseModel):
    message_id: str
    request_id: str
    sender_id: int
    sender_role: str
    message: str
    created_at: Optional[str] = None


class ChatSendResponse(BaseModel):
    ok: bool
    feedback: str = ""
