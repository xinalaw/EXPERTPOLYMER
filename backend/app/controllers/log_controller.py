from datetime import date, datetime, time, timedelta, timezone

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
        day_start = datetime.combine(log_date, time.min, tzinfo=timezone.utc)
        query = query.filter(
            ActionLog.created_at >= day_start,
            ActionLog.created_at < day_start + timedelta(days=1),
        )

    return query.order_by(ActionLog.created_at.desc()).offset(offset).limit(limit).all()
