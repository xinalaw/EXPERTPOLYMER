from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.user import User


class AnalysisTask(Base):
    __tablename__ = "analysis_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    task_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )

    status: Mapped[str] = mapped_column(String, nullable=False, default="PENDING")

    image_path: Mapped[str] = mapped_column(String, nullable=False)

    original_filename: Mapped[str] = mapped_column(String, nullable=False)

    result_id: Mapped[int | None] = mapped_column(
        ForeignKey("analysis_results.id"),
        nullable=True,
    )

    error_message: Mapped[str | None] = mapped_column(String, nullable=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    user: Mapped[User] = relationship("User")
