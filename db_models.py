from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class VolunteerRecord(Base):
    __tablename__ = "volunteers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    telefone: Mapped[str] = mapped_column(String(11), nullable=False)
    cargo_pretendido: Mapped[str] = mapped_column(String(100), nullable=False)
    disponibilidade: Mapped[str] = mapped_column(String(10), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=False,
        default=datetime.now,
    )


Index(
    "uq_volunteers_active_email_ci",
    func.lower(VolunteerRecord.email),
    unique=True,
    postgresql_where=text("active = true"),
    sqlite_where=text("active = 1"),
)
