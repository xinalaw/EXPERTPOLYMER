from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.controllers.user_controller import (
    get_all_users,
    update_user_role,
    delete_user,
    update_user_director,
    search_users,
)
from app.middleware.auth_middleware import get_admin_user, get_current_user
from app.models.user import User
from app.schemas.user import (
    UserRoleUpdateSchema,
    UserResponseSchema,
    UserDirectorUpdateSchema,
)


router = APIRouter(
    prefix="/api/users",
    tags=["Users"],
)


@router.get("", response_model=list[UserResponseSchema])
def get_users(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return get_all_users(db, limit, offset)


@router.patch("/{user_id}/role", response_model=UserResponseSchema)
def change_user_role(
    user_id: int,
    role_data: UserRoleUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return update_user_role(user_id, role_data, db, current_user)


@router.patch("/{user_id}/director", response_model=UserResponseSchema)
def change_user_director(
    user_id: int,
    director_data: UserDirectorUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return update_user_director(user_id, director_data, db, current_user)


@router.get("/search", response_model=list[UserResponseSchema])
def search_users_route(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return search_users(
        query=query,
        db=db,
        current_user=current_user,
        limit=limit,
        offset=offset,
    )


@router.delete("/{user_id}")
def remove_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    return delete_user(user_id, db)
