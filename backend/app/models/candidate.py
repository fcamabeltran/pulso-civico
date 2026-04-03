from sqlalchemy import JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    party: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    region: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    office: Mapped[str | None] = mapped_column(String(255), nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column("metadata", JSON, nullable=True)

    proposals = relationship(
        "Proposal",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )
    promises = relationship(
        "PromiseTracking",
        back_populates="candidate",
        cascade="all, delete-orphan",
    )

