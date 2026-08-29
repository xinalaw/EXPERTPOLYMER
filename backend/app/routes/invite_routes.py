from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.auth_controller import get_db
from app.controllers.invite_controller import (
    create_invite,
    check_invite,
    accept_invite,
)
from app.middleware.auth_middleware import get_current_user
from app.models.user import User
from app.schemas.invite import (
    DirectorInviteResponseSchema,
    DirectorInviteCheckSchema,
    DirectorInviteCreateSchema,
)
from app.schemas.user import UserResponseSchema

router = APIRouter(
    prefix="/api/invites",
    tags=["Invites"],
)


@router.post(
    "",
    response_model=DirectorInviteResponseSchema,
    summary="Создание invite-кода",
)
def create_director_invite(
    invite_data: DirectorInviteCreateSchema = DirectorInviteCreateSchema(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_invite(invite_data, db, current_user)


@router.get(
    "/{code}",
    response_model=DirectorInviteCheckSchema,
    summary="Проверка invite-кода",
)
def get_director_invite(
    code: str,
    db: Session = Depends(get_db),
):
    return check_invite(code, db)


@router.post(
    "/{code}/accept",
    response_model=UserResponseSchema,
    summary="Принятие invite-кода",
)
def accept_director_invite(
    code: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return accept_invite(code, db, current_user)
