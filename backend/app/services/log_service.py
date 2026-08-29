from sqlalchemy.orm import Session

from app.models.action_log import ActionLog


def create_action_log(
    db: Session,
    actor_id: int | None,
    action: str,
    target_type: str,
    target_id: int | None = None,
    details: dict | None = None,
):
    log = ActionLog(
        actor_id=actor_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        details=details,
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log
