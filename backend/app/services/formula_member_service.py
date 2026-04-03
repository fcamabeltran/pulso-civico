from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import FormulaMember
from app.schemas.formula_member import (
    AssetRecord,
    EducationRecord,
    ElectedOfficeRecord,
    FormulaMemberDetail,
    FormulaMemberRead,
    FormulaMembersResponse,
    FormulaProfileRead,
    PartyRoleRecord,
    SentenceRecord,
    WorkExperienceRecord,
)


# ── JSON parsers ──────────────────────────────────────────────────────────────

def _str(val: object) -> str | None:
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _parse_university_education(metrics: dict) -> list[EducationRecord]:
    records: list[EducationRecord] = []
    edu = metrics.get("education") or {}
    items = edu.get("educacionUniversitaria") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        institution = _str(item.get("universidad")) or "Sin institución"
        degree = _str(item.get("carreraUni")) or "Sin carrera"
        completed_raw = str(item.get("concluidoEduUni", "")).upper().strip()
        completed = completed_raw == "SI" or completed_raw == "S"
        year = _str(item.get("anioTitulo"))
        comment = _str(item.get("txComentario"))
        records.append(EducationRecord(
            institution=institution,
            degree=degree,
            completed=completed,
            year=year,
            comment=comment,
        ))
    return records


def _parse_postgraduate_education(metrics: dict) -> list[EducationRecord]:
    records: list[EducationRecord] = []
    edu = metrics.get("education") or {}
    items = edu.get("educacionPosgrado") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        institution = (
            _str(item.get("institucion"))
            or _str(item.get("strInstitucion"))
            or "Sin institución"
        )
        degree = (
            _str(item.get("grado"))
            or _str(item.get("strGrado"))
            or "Sin grado"
        )
        year = _str(item.get("anioGrado"))
        comment = _str(item.get("txComentario"))
        records.append(EducationRecord(
            institution=institution,
            degree=degree,
            completed=True,
            year=year,
            comment=comment,
        ))
    return records


def _parse_work_experience(metrics: dict) -> list[WorkExperienceRecord]:
    records: list[WorkExperienceRecord] = []
    items = metrics.get("work_experience") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        organization = _str(item.get("centroTrabajo")) or "Sin organización"
        position = _str(item.get("ocupacionProfesion")) or "Sin cargo"
        year_from = _str(item.get("anioTrabajoDesde"))
        year_to = _str(item.get("anioTrabajoHasta"))
        country = _str(item.get("trabajoPais"))
        records.append(WorkExperienceRecord(
            organization=organization,
            position=position,
            year_from=year_from,
            year_to=year_to,
            country=country,
        ))
    return records


def _parse_elected_offices(metrics: dict) -> list[ElectedOfficeRecord]:
    records: list[ElectedOfficeRecord] = []
    trajectory = metrics.get("trajectory") or {}
    items = trajectory.get("cargoEleccion") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        party = _str(item.get("orgPolCargoElec")) or "Sin partido"
        office = _str(item.get("cargoEleccion")) or "Sin cargo"
        year_from = _str(item.get("anioCargoElecDesde"))
        year_to = _str(item.get("anioCargoElecHasta"))
        comment = _str(item.get("txComentario"))
        records.append(ElectedOfficeRecord(
            party=party,
            office=office,
            year_from=year_from,
            year_to=year_to,
            comment=comment,
        ))
    return records


def _parse_party_roles(metrics: dict) -> list[PartyRoleRecord]:
    records: list[PartyRoleRecord] = []
    trajectory = metrics.get("trajectory") or {}
    items = trajectory.get("cargoPartidario") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        # Try multiple key names for party
        party = (
            _str(item.get("orgPolitica"))
            or _str(item.get("organismoPartidario"))
            or _str(item.get("partido"))
            or _str(item.get("orgPolCargoElec"))
            or "Sin partido"
        )
        role = (
            _str(item.get("cargoPartidario"))
            or _str(item.get("cargo"))
            or "Sin cargo"
        )
        year_from = _str(item.get("anioDesde")) or _str(item.get("anioCargoDesde"))
        year_to = _str(item.get("anioHasta")) or _str(item.get("anioCargoHasta"))
        records.append(PartyRoleRecord(
            party=party,
            role=role,
            year_from=year_from,
            year_to=year_to,
        ))
    return records


def _parse_sentences(metrics: dict, key: str) -> list[SentenceRecord]:
    records: list[SentenceRecord] = []
    items = metrics.get(key) or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        description = (
            _str(item.get("txDescripcion"))
            or _str(item.get("descripcion"))
            or _str(item.get("descripcionSentencia"))
            or "Sin descripción"
        )
        year = (
            _str(item.get("txAno"))
            or _str(item.get("anio"))
            or _str(item.get("anioSentencia"))
        )
        comment = _str(item.get("txComentario"))
        records.append(SentenceRecord(description=description, year=year, comment=comment))
    return records


def _parse_immovable_assets(metrics: dict) -> list[AssetRecord]:
    records: list[AssetRecord] = []
    declaration = metrics.get("declaration") or {}
    items = declaration.get("bienInmueble") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        description = (
            _str(item.get("direccion"))
            or _str(item.get("descripcion"))
            or _str(item.get("tipoBienInmueble"))
            or "Bien inmueble"
        )
        value_raw = item.get("autoavaluo") or item.get("valor") or item.get("autoavalúo")
        try:
            value = float(value_raw) if value_raw is not None else None
        except (ValueError, TypeError):
            value = None
        location = _str(item.get("distrito")) or _str(item.get("departamento"))
        records.append(AssetRecord(description=description, value=value, location=location))
    return records


def _parse_movable_assets(metrics: dict) -> list[AssetRecord]:
    records: list[AssetRecord] = []
    declaration = metrics.get("declaration") or {}
    items = declaration.get("bienMueble") or []
    if not isinstance(items, list):
        return records
    for item in items:
        if not isinstance(item, dict):
            continue
        description = (
            _str(item.get("marca"))
            or _str(item.get("descripcion"))
            or _str(item.get("tipoBienMueble"))
            or "Bien mueble"
        )
        value_raw = item.get("valor") or item.get("valorEstimado")
        try:
            value = float(value_raw) if value_raw is not None else None
        except (ValueError, TypeError):
            value = None
        records.append(AssetRecord(description=description, value=value, location=None))
    return records


# ── Member → schema converters ────────────────────────────────────────────────

def _member_to_read(member: FormulaMember) -> FormulaMemberRead:
    return FormulaMemberRead.model_validate(member)


def _member_to_detail(member: FormulaMember) -> FormulaMemberDetail:
    metrics: dict = member.metrics_json or {}
    return FormulaMemberDetail(
        id=member.id,
        organization_id=member.organization_id,
        party_name=member.party_name,
        party_slug=member.party_slug,
        candidate_name=member.candidate_name,
        office=member.office,
        position=member.position,
        photo_url=member.photo_url,
        party_logo_url=member.party_logo_url,
        hoja_vida_url=member.hoja_vida_url,
        annual_income_total=member.annual_income_total,
        public_income_total=member.public_income_total,
        private_income_total=member.private_income_total,
        movable_assets_count=member.movable_assets_count,
        immovable_assets_count=member.immovable_assets_count,
        assets_declared_value=member.assets_declared_value,
        legal_entities_count=member.legal_entities_count,
        labor_records_count=member.labor_records_count,
        renuncia_records_count=member.renuncia_records_count,
        elected_offices_count=member.elected_offices_count,
        party_roles_count=member.party_roles_count,
        university_education_count=member.university_education_count,
        postgraduate_records_count=member.postgraduate_records_count,
        academic_records_count=member.academic_records_count,
        penal_sentences_count=member.penal_sentences_count,
        civil_sentences_count=member.civil_sentences_count,
        obligations_count=member.obligations_count,
        additional_notes_count=member.additional_notes_count,
        marginal_annotations_count=member.marginal_annotations_count,
        summary=member.summary,
        university_education=_parse_university_education(metrics),
        postgraduate_education=_parse_postgraduate_education(metrics),
        work_experience=_parse_work_experience(metrics),
        elected_offices=_parse_elected_offices(metrics),
        party_roles=_parse_party_roles(metrics),
        penal_sentences=_parse_sentences(metrics, "penal_sentences"),
        civil_sentences=_parse_sentences(metrics, "civil_sentences"),
        immovable_assets=_parse_immovable_assets(metrics),
        movable_assets=_parse_movable_assets(metrics),
    )


# ── Public service functions ──────────────────────────────────────────────────

def list_formula_profiles(db: Session) -> list[FormulaProfileRead]:
    members = list(
        db.scalars(
            select(FormulaMember).order_by(
                FormulaMember.party_name.asc(),
                FormulaMember.position.asc(),
            )
        ).all()
    )

    # Group by organization_id
    groups: dict[int, list[FormulaMember]] = {}
    for m in members:
        groups.setdefault(m.organization_id, []).append(m)

    profiles: list[FormulaProfileRead] = []
    for org_id, org_members in groups.items():
        first = org_members[0]
        profiles.append(FormulaProfileRead(
            organization_id=org_id,
            party_name=first.party_name,
            party_slug=first.party_slug,
            members=[_member_to_read(m) for m in org_members],
        ))
    return profiles


def get_member_detail(db: Session, member_id: int) -> FormulaMemberDetail | None:
    member = db.get(FormulaMember, member_id)
    if not member:
        return None
    return _member_to_detail(member)


def get_member_by_name(db: Session, name: str) -> FormulaMemberDetail | None:
    from sqlalchemy import func
    normalized = name.upper().strip()

    # 1. SQL exact match — fast, single row lookup
    member = db.scalars(
        select(FormulaMember).where(
            func.upper(func.trim(FormulaMember.candidate_name)) == normalized
        )
    ).first()
    if member:
        return _member_to_detail(member)

    # 2. Token fallback — only if exact fails (rare: name format differences)
    tokens = normalized.split()
    all_members = db.scalars(select(FormulaMember)).all()
    for m in all_members:
        if all(tok in m.candidate_name.upper() for tok in tokens):
            return _member_to_detail(m)

    return None


# ── Legacy function kept for existing endpoint ────────────────────────────────

def get_formula_members(db: Session, organization_id: int) -> FormulaMembersResponse | None:
    members = list(
        db.scalars(
            select(FormulaMember)
            .where(FormulaMember.organization_id == organization_id)
            .order_by(FormulaMember.position.asc(), FormulaMember.office.asc())
        ).all()
    )
    if not members:
        return None

    party_name = members[0].party_name
    party_logo_url = members[0].party_logo_url
    total_declared_income = sum(member.annual_income_total or 0 for member in members)
    return FormulaMembersResponse(
        organization_id=organization_id,
        party_name=party_name,
        party_logo_url=party_logo_url,
        total_declared_income=total_declared_income if total_declared_income > 0 else None,
        total_members=len(members),
        penal_sentences_count=sum(member.penal_sentences_count for member in members),
        civil_sentences_count=sum(member.civil_sentences_count for member in members),
        members=[_member_to_read(m) for m in members],
    )
