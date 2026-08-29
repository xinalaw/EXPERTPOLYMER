from datetime import date

from sqlalchemy import Date, cast
from sqlalchemy.orm import Session

from app.models.action_log import ActionLog


def get_action_logs(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    action: str | None = None,
    actor_id: int | None = None,
    log_date: date | None = None,
):

    query = db.query(ActionLog)

    if action is not None:
        query = query.filter(ActionLog.action == action)

    if actor_id is not None:
        query = query.filter(ActionLog.actor_id == actor_id)

    if log_date is not None:
        query = query.filter(cast(ActionLog.created_at, Date) == log_date)

    return query.order_by(ActionLog.created_at.desc()).offset(offset).limit(limit).all()
