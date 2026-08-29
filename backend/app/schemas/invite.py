from datetime import datetime

from pydantic import BaseModel, Field


class DirectorInviteCreateSchema(BaseModel):
    expires_in_days: int = Field(default=7, ge=1, le=30)


class DirectorInviteResponseSchema(BaseModel):
    id: int
    code: str
    director_id: int
    is_active: bool
    created_at: datetime
    expires_at: datetime

    class Config:
        from_attributes = True


class DirectorInviteCheckSchema(BaseModel):
    code: str
    director_id: int
    director_username: str
    is_active: bool
    expires_at: datetime


class InviteAcceptanceResponseSchema(BaseModel):
    id: int
    invite_id: int
    user_id: int
    accepted_at: datetime

    class Config:
        from_attributes = True
