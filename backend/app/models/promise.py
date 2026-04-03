import enum

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PromiseStatus(str, enum.Enum):
    fulfilled = "cumplida"
    pending = "pendiente"
    unmet = "incumplida"
    partial = "parcial"


class PromiseTracking(Base):
    __tablename__ = "promises"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PromiseStatus] = mapped_column(Enum(PromiseStatus), nullable=False, default=PromiseStatus.pending)
    source_name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    evidence_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    candidate = relationship("Candidate", back_populates="promises")

