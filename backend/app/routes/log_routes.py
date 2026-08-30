from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.controllers.log_controller import get_action_logs
from app.middleware.auth_middleware import get_admin_user
from app.models.user import User
from app.schemas.log import ActionLogResponseSchema


router = APIRouter(
    prefix="/api/logs",
    tags=["Audit Logs"],
)


@router.get(
    "",
    response_model=list[ActionLogResponseSchema],
    summary="Получение audit logs",
)
def get_logs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    action: str | None = Query(default=None),
    actor_id: int | None = Query(default=None),
    log_date: date | None = Query(default=None, alias="date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return get_action_logs(
        db=db,
        limit=limit,
        offset=offset,
        action=action,
        actor_id=actor_id,
        log_date=log_date,
    )
