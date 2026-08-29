from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.schemas.user import UserRegisterSchema, UserLoginSchema
from app.utils.security import hash_password, verify_password, create_access_token


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def register_user(user_data: UserRegisterSchema, db: Session):
    existing_user = db.query(User).filter(User.email == user_data.email).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует",
        )

    username = f"{user_data.first_name} {user_data.last_name}"

    new_user = User(
        username=username,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        organization=user_data.organization,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role="researcher",
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


def login_user(user_data: UserLoginSchema, db: Session):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if not verify_password(user_data.password, str(user.password_hash)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
