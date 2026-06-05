from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from api.database import Base

if TYPE_CHECKING:
    from api.models.investigation import Investigation
    from api.models.job import Job

import enum


class TargetType(str, enum.Enum):
    username = "username"
    email = "email"
    phone = "phone"
    ip = "ip"
    domain = "domain"
    name = "name"


class Target(Base):
    __tablename__ = "targets"

    id: Mapped[int] = mapped_column(primary_key=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), nullable=False)
    type: Mapped[TargetType] = mapped_column(Enum(TargetType), nullable=False)
    value: Mapped[str] = mapped_column(String(256), nullable=False)

    investigation: Mapped[Investigation] = relationship("Investigation", back_populates="targets")
    jobs: Mapped[list[Job]] = relationship("Job", back_populates="target", cascade="all, delete-orphan")
