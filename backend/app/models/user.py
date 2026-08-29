from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    username: Mapped[str] = mapped_column(String, nullable=False)

    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    organization: Mapped[str | None] = mapped_column(String, nullable=True)

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    role: Mapped[str] = mapped_column(String, default="researcher")

    avatar: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    director_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    director: Mapped[Optional["User"]] = relationship(
        "User",
        remote_side=[id],
        back_populates="researchers",
    )

    researchers: Mapped[list["User"]] = relationship(
        "User",
        back_populates="director",
    )
