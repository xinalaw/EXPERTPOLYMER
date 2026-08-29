"""Create the first administrator account.

Run from ``backend/``:
    python -m app.commands.create_admin --email admin@example.com
"""

from __future__ import annotations

import argparse
import getpass

from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.utils.security import hash_password


class BootstrapAdminError(ValueError):
    pass


def create_first_admin(
    db: Session,
    *,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
) -> User:
    if db.query(User).filter(User.role == "admin").first():
        raise BootstrapAdminError(
            "Администратор уже существует. Меняйте роли через админ-панель."
        )

    if db.query(User).filter(User.email == email).first():
        raise BootstrapAdminError("Пользователь с таким email уже существует.")

    if len(password) < 8 or len(password.encode("utf-8")) > 72:
        raise BootstrapAdminError("Пароль должен содержать от 8 до 72 байт.")

    user = User(
        username=f"{first_name} {last_name}",
        first_name=first_name,
        last_name=last_name,
        email=email,
        password_hash=hash_password(password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def main() -> None:
    parser = argparse.ArgumentParser(description="Создать первого администратора")
    parser.add_argument("--email", required=True)
    parser.add_argument("--first-name", default="System")
    parser.add_argument("--last-name", default="Administrator")
    args = parser.parse_args()

    password = getpass.getpass("Пароль администратора: ")
    confirmation = getpass.getpass("Повторите пароль: ")
    if password != confirmation:
        parser.error("Пароли не совпадают")

    db = SessionLocal()
    try:
        user = create_first_admin(
            db,
            email=args.email,
            password=password,
            first_name=args.first_name,
            last_name=args.last_name,
        )
    except BootstrapAdminError as error:
        parser.error(str(error))
    finally:
        db.close()

    print(f"Администратор {user.email} создан (id={user.id}).")


if __name__ == "__main__":
    main()
