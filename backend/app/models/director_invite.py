from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.user import User


class DirectorInvite(Base):
    __tablename__ = "director_invites"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    director_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    director: Mapped[User] = relationship(
        "User",
        foreign_keys=[director_id],
    )
