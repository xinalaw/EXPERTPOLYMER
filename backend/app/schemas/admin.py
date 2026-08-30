from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AdminDashboardSchema(BaseModel):
    users_total: int
    admins: int
    directors: int
    researchers: int
    analyses_total: int
    tasks_total: int
    tasks_pending: int
    tasks_processing: int
    tasks_success: int
    tasks_failure: int
    active_invites: int


class AnalysisTaskResponseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: str
    status: str
    image_path: str
    original_filename: str
    result_id: int | None
    error_message: str | None
    user_id: int
    created_at: datetime
    updated_at: datetime
