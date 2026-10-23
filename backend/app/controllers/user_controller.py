from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserRoleUpdateSchema, UserDirectorUpdateSchema
from app.services.log_service import create_action_log
from app.services.access_service import can_search_users, is_admin, is_director


def get_all_users(
    db: Session,
    limit: int = 20,
    offset: int = 0,
):
    return db.query(User).order_by(User.id.asc()).offset(offset).limit(limit).all()


def search_users(
    query: str,
    db: Session,
    current_user: User,
    limit: int = 20,
    offset: int = 0,
):
    if not can_search_users(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )

    search_pattern = f"%{query}%"

    users_query = db.query(User).filter(
        (User.username.ilike(search_pattern)) | (User.email.ilike(search_pattern))
    )

    if is_director(current_user):
        users_query = users_query.filter(
            User.director_id == current_user.id,
            User.role == "researcher",
        )

    return users_query.order_by(User.id.asc()).offset(offset).limit(limit).all()


def update_user_director(
    user_id: int,
    director_data: UserDirectorUpdateSchema,
    db: Session,
    current_admin: User,
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    if str(user.role) != "researcher":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Директора можно назначать только researcher",
        )

    director = None

    if director_data.director_id is not None:
        director = db.query(User).filter(User.id == director_data.director_id).first()

        if not director:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Директор не найден",
            )

        if str(director.role) != "director":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Указанный пользователь не является director",
            )

    old_director_id = user.director_id

    user.director_id = director_data.director_id

    db.commit()
    db.refresh(user)

    create_action_log(
        db=db,
        actor_id=int(current_admin.id),
        action="ASSIGN_DIRECTOR",
        target_type="user",
        target_id=user.id,
        details={
            "old_director_id": old_director_id,
            "new_director_id": director_data.director_id,
        },
    )

    return user


def update_user_role(
    user_id: int,
    role_data: UserRoleUpdateSchema,
    db: Session,
    current_admin: User,
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    old_role = str(user.role)
    new_role = role_data.role

    if user.id == current_admin.id and old_role == "admin" and new_role != "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя снять роль администратора с самого себя",
        )

    user.role = new_role

    if new_role != "researcher":
        user.director_id = None

    db.commit()
    db.refresh(user)

    create_action_log(
        db=db,
        actor_id=int(current_admin.id),
        action="CHANGE_USER_ROLE",
        target_type="user",
        target_id=user.id,
        details={"old_role": old_role, "new_role": new_role},
    )

    return user


def delete_user(user_id: int, db: Session):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    db.delete(user)
    db.commit()

    return {"message": "Пользователь удален"}
