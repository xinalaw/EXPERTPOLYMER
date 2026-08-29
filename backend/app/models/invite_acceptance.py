from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.director_invite import DirectorInvite
from app.models.user import User


class InviteAcceptance(Base):
    __tablename__ = "invite_acceptances"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    invite_id: Mapped[int] = mapped_column(
        ForeignKey("director_invites.id"),
        nullable=False,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    invite: Mapped[DirectorInvite] = relationship("DirectorInvite")
    user: Mapped[User] = relationship("User")

    __table_args__ = (UniqueConstraint("invite_id", "user_id", name="uq_invite_user"),)
