from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.controllers.admin_controller import (
    get_analysis_tasks,
    get_dashboard,
    get_invites,
)
from app.database.dependencies import get_db
from app.middleware.auth_middleware import get_admin_user
from app.models.user import User
from app.schemas.admin import AdminDashboardSchema, AnalysisTaskResponseSchema
from app.schemas.invite import DirectorInviteResponseSchema


router = APIRouter(prefix="/api/admin", tags=["Admin Panel"])


@router.get("/dashboard", response_model=AdminDashboardSchema)
def dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return get_dashboard(db)


@router.get("/tasks", response_model=list[AnalysisTaskResponseSchema])
def analysis_tasks(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return get_analysis_tasks(
        db,
        task_status=status,
        limit=limit,
        offset=offset,
    )


@router.get("/invites", response_model=list[DirectorInviteResponseSchema])
def invites(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return get_invites(db, limit=limit, offset=offset)
