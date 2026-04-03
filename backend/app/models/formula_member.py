from sqlalchemy import Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class FormulaMember(Base):
    __tablename__ = "formula_members"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(Integer, index=True)
    party_name: Mapped[str] = mapped_column(String(255), index=True)
    party_slug: Mapped[str] = mapped_column(String(255), index=True)
    candidate_name: Mapped[str] = mapped_column(String(255), index=True)
    office: Mapped[str] = mapped_column(String(255), index=True)
    position: Mapped[int] = mapped_column(Integer, index=True)
    document_number: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    photo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    party_logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    hoja_vida_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    hoja_vida_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    local_hoja_vida_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    annual_income_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    public_income_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    private_income_total: Mapped[float | None] = mapped_column(Float, nullable=True)
    movable_assets_count: Mapped[int] = mapped_column(Integer, default=0)
    immovable_assets_count: Mapped[int] = mapped_column(Integer, default=0)
    assets_declared_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    legal_entities_count: Mapped[int] = mapped_column(Integer, default=0)
    labor_records_count: Mapped[int] = mapped_column(Integer, default=0)
    renuncia_records_count: Mapped[int] = mapped_column(Integer, default=0)
    elected_offices_count: Mapped[int] = mapped_column(Integer, default=0)
    party_roles_count: Mapped[int] = mapped_column(Integer, default=0)
    technical_education_count: Mapped[int] = mapped_column(Integer, default=0)
    non_university_education_count: Mapped[int] = mapped_column(Integer, default=0)
    university_education_count: Mapped[int] = mapped_column(Integer, default=0)
    academic_records_count: Mapped[int] = mapped_column(Integer, default=0)
    postgraduate_records_count: Mapped[int] = mapped_column(Integer, default=0)
    penal_sentences_count: Mapped[int] = mapped_column(Integer, default=0)
    civil_sentences_count: Mapped[int] = mapped_column(Integer, default=0)
    obligations_count: Mapped[int] = mapped_column(Integer, default=0)
    additional_notes_count: Mapped[int] = mapped_column(Integer, default=0)
    marginal_annotations_count: Mapped[int] = mapped_column(Integer, default=0)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metrics_json: Mapped[dict | None] = mapped_column("metrics", JSON, nullable=True)
    raw_json: Mapped[dict | None] = mapped_column("raw_payload", JSON, nullable=True)
