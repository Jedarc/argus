from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

if TYPE_CHECKING:
    from api.models.job import Job


class Result(Base):
    __tablename__ = "results"

    id: Mapped[int] = mapped_column(primary_key=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"), nullable=False)
    module: Mapped[str] = mapped_column(String(64), nullable=False)
    target_type: Mapped[str] = mapped_column(String(32), nullable=False)
    target_value: Mapped[str] = mapped_column(String(256), nullable=False)
    raw_json: Mapped[str | None] = mapped_column(Text)
    found: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    cached: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    job: Mapped[Job] = relationship("Job", back_populates="result")

    __table_args__ = (
        # Cache lookup index — same key used across investigations
        Index("ix_results_cache_key", "module", "target_type", "target_value"),
    )
