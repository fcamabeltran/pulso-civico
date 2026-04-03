from pydantic import BaseModel, ConfigDict


class EducationRecord(BaseModel):
    institution: str
    degree: str
    completed: bool
    year: str | None = None
    comment: str | None = None


class WorkExperienceRecord(BaseModel):
    organization: str
    position: str
    year_from: str | None = None
    year_to: str | None = None
    country: str | None = None


class ElectedOfficeRecord(BaseModel):
    party: str
    office: str
    year_from: str | None = None
    year_to: str | None = None
    comment: str | None = None


class PartyRoleRecord(BaseModel):
    party: str
    role: str
    year_from: str | None = None
    year_to: str | None = None


class SentenceRecord(BaseModel):
    description: str
    year: str | None = None
    comment: str | None = None


class AssetRecord(BaseModel):
    description: str
    value: float | None = None
    location: str | None = None


class FormulaMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    organization_id: int
    party_name: str
    party_slug: str
    candidate_name: str
    office: str
    position: int
    photo_url: str | None = None
    party_logo_url: str | None = None
    hoja_vida_url: str | None = None

    # Summary metrics
    annual_income_total: float | None = None
    public_income_total: float | None = None
    private_income_total: float | None = None
    movable_assets_count: int = 0
    immovable_assets_count: int = 0
    assets_declared_value: float | None = None
    legal_entities_count: int = 0
    labor_records_count: int = 0
    renuncia_records_count: int = 0
    elected_offices_count: int = 0
    party_roles_count: int = 0
    university_education_count: int = 0
    postgraduate_records_count: int = 0
    academic_records_count: int = 0
    penal_sentences_count: int = 0
    civil_sentences_count: int = 0
    obligations_count: int = 0
    additional_notes_count: int = 0
    marginal_annotations_count: int = 0
    summary: str | None = None


class FormulaMemberDetail(FormulaMemberRead):
    university_education: list[EducationRecord] = []
    postgraduate_education: list[EducationRecord] = []
    work_experience: list[WorkExperienceRecord] = []
    elected_offices: list[ElectedOfficeRecord] = []
    party_roles: list[PartyRoleRecord] = []
    penal_sentences: list[SentenceRecord] = []
    civil_sentences: list[SentenceRecord] = []
    immovable_assets: list[AssetRecord] = []
    movable_assets: list[AssetRecord] = []


class FormulaProfileRead(BaseModel):
    organization_id: int
    party_name: str
    party_slug: str
    members: list[FormulaMemberRead]


# Keep backward-compat schema for existing endpoint
class FormulaMembersResponse(BaseModel):
    organization_id: int
    party_name: str
    party_logo_url: str | None = None
    total_declared_income: float | None = None
    total_members: int
    penal_sentences_count: int
    civil_sentences_count: int
    members: list[FormulaMemberRead]
