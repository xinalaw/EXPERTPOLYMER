from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.analysis_task import AnalysisTask
from app.models.director_invite import DirectorInvite
from app.models.user import User


def get_dashboard(db: Session) -> dict[str, int]:
    role_counts = dict(
        db.query(User.role, func.count(User.id)).group_by(User.role).all()
    )
    task_counts = dict(
        db.query(AnalysisTask.status, func.count(AnalysisTask.id))
        .group_by(AnalysisTask.status)
        .all()
    )
    return {
        "users_total": db.query(User).count(),
        "admins": role_counts.get("admin", 0),
        "directors": role_counts.get("director", 0),
        "researchers": role_counts.get("researcher", 0),
        "analyses_total": db.query(AnalysisResult).count(),
        "tasks_total": db.query(AnalysisTask).count(),
        "tasks_pending": task_counts.get("PENDING", 0),
        "tasks_processing": task_counts.get("PROCESSING", 0),
        "tasks_success": task_counts.get("SUCCESS", 0),
        "tasks_failure": task_counts.get("FAILURE", 0),
        "active_invites": db.query(DirectorInvite)
        .filter(
            DirectorInvite.is_active.is_(True),
            DirectorInvite.expires_at > datetime.now(timezone.utc),
        )
        .count(),
    }


def get_analysis_tasks(
    db: Session,
    *,
    task_status: str | None,
    limit: int,
    offset: int,
):
    query = db.query(AnalysisTask)
    if task_status:
        query = query.filter(AnalysisTask.status == task_status)
    return query.order_by(AnalysisTask.created_at.desc()).offset(offset).limit(limit).all()


def get_invites(db: Session, *, limit: int, offset: int):
    return (
        db.query(DirectorInvite)
        .order_by(DirectorInvite.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
from datetime import datetime, timezone
