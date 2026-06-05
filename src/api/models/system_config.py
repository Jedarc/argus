from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, Session, mapped_column

from api.database import Base


class SystemConfig(Base):
    __tablename__ = "system_config"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    @classmethod
    def get(cls, session: Session, key: str) -> str | None:
        row = session.get(cls, key)
        return row.value if row else None

    @classmethod
    def set(cls, session: Session, key: str, value: str) -> None:
        row = session.get(cls, key)
        if row:
            row.value = value
            row.updated_at = datetime.now(timezone.utc)
        else:
            session.add(cls(key=key, value=value))
        session.commit()
