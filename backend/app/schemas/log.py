from datetime import datetime
from typing import Any

from pydantic import BaseModel


class ActionLogResponseSchema(BaseModel):
    id: int
    actor_id: int | None
    action: str
    target_type: str
    target_id: int | None
    details: dict[str, Any] | None
    created_at: datetime

    class Config:
        from_attributes = True
