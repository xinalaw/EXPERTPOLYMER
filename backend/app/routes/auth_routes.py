from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.auth_controller import register_user, login_user
from app.database.dependencies import get_db
from app.schemas.user import UserRegisterSchema, UserLoginSchema, UserResponseSchema
from app.schemas.token import TokenSchema

from app.middleware.auth_middleware import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponseSchema,
    summary="Регистрация пользователя",
    description="""
        Регистрирует пользователя в системе, добавляя его в БД,
        проверяется уникальность email и длина password
        """,
)
def register(user_data: UserRegisterSchema, db: Session = Depends(get_db)):
    return register_user(user_data, db)


@router.post(
    "/login",
    response_model=TokenSchema,
    summary="Авторизация пользователя",
    description="""
        Проверяет email и password пользователя
        и возвращает JWT access token
        """,
)
def login(user_data: UserLoginSchema, db: Session = Depends(get_db)):
    return login_user(user_data, db)


@router.get(
    "/me",
    response_model=UserResponseSchema,
    summary="Получение текущего пользователя",
    description="Возвращает данные о текущем пользователе",
)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
