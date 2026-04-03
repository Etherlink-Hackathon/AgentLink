from __future__ import annotations

from pydantic import BaseModel


class RoleGrantedPayload(BaseModel):
    role: bytes
    account: str
    sender: str
