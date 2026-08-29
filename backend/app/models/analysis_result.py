from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.database import Base
from app.models.user import User


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    image_path: Mapped[str] = mapped_column(String, nullable=False)

    processed_image_path: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    original_filename: Mapped[str] = mapped_column(String, nullable=False)

    result: Mapped[str] = mapped_column(String, nullable=False)

    result_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    width: Mapped[Optional[int]] = mapped_column(nullable=True)

    height: Mapped[Optional[int]] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped[User] = relationship("User")
