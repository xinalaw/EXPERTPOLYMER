from datetime import datetime, timedelta, timezone
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.director_invite import DirectorInvite
from app.models.invite_acceptance import InviteAcceptance
from app.models.user import User
from app.schemas.invite import DirectorInviteCreateSchema
from app.services.log_service import create_action_log


def create_invite(
    invite_data: DirectorInviteCreateSchema,
    db: Session,
    current_user: User,
):
    if current_user.role != "director":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Создавать приглашения может только director",
        )

    code = str(uuid.uuid4())

    invite = DirectorInvite(
        code=code,
        director_id=current_user.id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=invite_data.expires_in_days),
    )

    db.add(invite)
    db.commit()
    db.refresh(invite)

    create_action_log(
        db=db,
        actor_id=current_user.id,
        action="CREATE_INVITE",
        target_type="director_invite",
        target_id=invite.id,
        details={
            "code": code,
            "director_id": current_user.id,
            "expires_in_days": invite_data.expires_in_days,
        },
    )

    return invite


def check_invite(code: str, db: Session):
    invite = db.query(DirectorInvite).filter(DirectorInvite.code == code).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Приглашение не найдено",
        )

    if not invite.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Приглашение неактивно",
        )

    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия приглашения истек",
        )

    return {
        "code": invite.code,
        "director_id": invite.director_id,
        "director_username": invite.director.username,
        "is_active": invite.is_active,
        "expires_at": invite.expires_at,
    }


def accept_invite(code: str, db: Session, current_user: User):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if user.role != "researcher":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Приглашение может принять только researcher",
        )

    if user.director_id is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже прикреплен к директору",
        )

    invite = db.query(DirectorInvite).filter(DirectorInvite.code == code).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Приглашение не найдено",
        )

    if not invite.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Приглашение неактивно",
        )

    if invite.expires_at < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Срок действия приглашения истек",
        )

    existing_acceptance = (
        db.query(InviteAcceptance)
        .filter(
            InviteAcceptance.invite_id == invite.id,
            InviteAcceptance.user_id == user.id,
        )
        .first()
    )

    if existing_acceptance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь уже принимал это приглашение",
        )

    user.director_id = invite.director_id

    acceptance = InviteAcceptance(
        invite_id=invite.id,
        user_id=user.id,
    )

    db.add(acceptance)
    db.commit()
    db.refresh(user)
    db.refresh(acceptance)

    create_action_log(
        db=db,
        actor_id=user.id,
        action="ACCEPT_INVITE",
        target_type="director_invite",
        target_id=invite.id,
        details={
            "director_id": invite.director_id,
            "researcher_id": user.id,
            "acceptance_id": acceptance.id,
        },
    )

    return user
