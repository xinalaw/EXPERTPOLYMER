from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ActionLogResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    action: str
    target_type: str
    target_id: int | None
    details: dict[str, Any] | None
    created_at: datetime
