from __future__ import annotations

from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from api.database import Base


class ModuleConfig(Base):
    __tablename__ = "module_configs"

    module: Mapped[str] = mapped_column(String(64), primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # API key stored AES-encrypted via Fernet. Never returned to the frontend.
    api_key_encrypted: Mapped[str | None] = mapped_column(Text)
    cache_ttl_seconds: Mapped[int] = mapped_column(Integer, default=86400, nullable=False)
