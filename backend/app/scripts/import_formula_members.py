from __future__ import annotations

import json
import unicodedata
from pathlib import Path

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import FormulaMember

DOWNLOAD_ROOT = Path("/app/data/downloads/jne_voto_informado")


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    compact = "".join(char if char.isalnum() else "-" for char in ascii_value.lower())
    compact = "-".join(part for part in compact.split("-") if part)
    return compact or "sin-nombre"


def as_list(value: object) -> list:
    return value if isinstance(value, list) else []


def as_dict(value: object) -> dict:
    return value if isinstance(value, dict) else {}


def income_metrics(payload: dict) -> tuple[float | None, float | None, float | None]:
    declaration = as_dict(payload.get("declaracionJurada"))
    incomes = as_list(declaration.get("ingreso"))
    if not incomes:
        return None, None, None
    latest = incomes[0]
    public_total = float((latest.get("remuBrutaPublico") or 0) + (latest.get("rentaIndividualPublico") or 0) + (latest.get("otroIngresoPublico") or 0))
    private_total = float((latest.get("remuBrutaPrivado") or 0) + (latest.get("rentaIndividualPrivado") or 0) + (latest.get("otroIngresoPrivado") or 0))
    total = latest.get("totalIngresos")
    return (float(total) if total is not None else public_total + private_total, public_total, private_total)


def asset_metrics(payload: dict) -> tuple[int, int, float | None, int]:
    declaration = as_dict(payload.get("declaracionJurada"))
    movable = as_list(declaration.get("bienMueble"))
    immovable = as_list(declaration.get("bienInmueble"))
    titularidad = as_list(declaration.get("titularidad"))
    movable_value = sum(float(item.get("valor") or 0) for item in movable)
    immovable_value = sum(float(item.get("autoavaluo") or item.get("valor") or 0) for item in immovable)
    titularidad_value = sum(float(item.get("flValor") or 0) for item in titularidad)
    total_value = movable_value + immovable_value + titularidad_value
    return len(movable), len(immovable), (total_value if total_value > 0 else None), len(titularidad)


def education_metrics(payload: dict) -> tuple[int, int, int, int]:
    education = as_dict(payload.get("formacionAcademica"))
    technical_total = len(as_list(education.get("educacionTecnico")))
    non_university_total = len(as_list(education.get("educacionNoUniversitaria")))
    university_total = len(as_list(education.get("educacionUniversitaria")))
    academic_total = university_total + technical_total + non_university_total
    postgraduate_total = len(as_list(education.get("educacionPosgrado")))
    return technical_total, non_university_total, university_total, postgraduate_total


def trajectory_metrics(payload: dict) -> tuple[int, int]:
    trajectory = as_dict(payload.get("trayectoria"))
    elected_total = len(as_list(trajectory.get("cargoEleccion")))
    party_roles_total = len(as_list(trajectory.get("cargoPartidario")))
    return elected_total, party_roles_total


def build_summary(candidate_name: str, office: str, annual_income_total: float | None, labor_records: int, penal_count: int, civil_count: int, elected_count: int) -> str:
    parts = [f"{candidate_name} postula como {office.lower()}."]
    if annual_income_total is not None:
        parts.append(f"Declara ingresos anuales por S/ {annual_income_total:,.0f}.")
    if labor_records:
        parts.append(f"Registra {labor_records} antecedentes laborales.")
    if elected_count:
        parts.append(f"Tiene {elected_count} cargos de elección declarados.")
    if penal_count or civil_count:
        parts.append(f"Consigna {penal_count} sentencias penales y {civil_count} civiles.")
    else:
        parts.append("No registra sentencias penales ni civiles en la hoja de vida cargada.")
    return " ".join(parts)


def run() -> None:
    FormulaMember.__table__.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    imported = 0
    for metadata_path in DOWNLOAD_ROOT.rglob("metadata.json"):
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata = as_dict(payload.get("metadata"))
        office = str(metadata.get("formula_role") or "").strip()
        if office not in {
            "PRESIDENTE DE LA REPÚBLICA",
            "PRIMER VICEPRESIDENTE DE LA REPÚBLICA",
            "SEGUNDO VICEPRESIDENTE DE LA REPÚBLICA",
        }:
            continue

        hoja_path = metadata_path.parent / "hoja_vida.json"
        if not hoja_path.exists():
            hoja_payload = {}
        else:
            hoja_payload = json.loads(hoja_path.read_text(encoding="utf-8"))

        source_row = as_dict(payload.get("source_row"))
        annual_income_total, public_income_total, private_income_total = income_metrics(hoja_payload)
        movable_count, immovable_count, assets_value, legal_entities_count = asset_metrics(hoja_payload)
        technical_education_count, non_university_education_count, university_education_count, postgraduate_records_count = education_metrics(hoja_payload)
        elected_count, party_roles_count = trajectory_metrics(hoja_payload)
        labor_records_count = len(as_list(hoja_payload.get("experienciaLaboral")))
        renuncia_records_count = len(as_list(hoja_payload.get("renunciaEfectuada")))
        penal_count = len(as_list(hoja_payload.get("sentenciaPenal")))
        civil_count = len(as_list(hoja_payload.get("sentenciaCivil")))
        obligations_count = len(as_list(hoja_payload.get("sentenciaObliga")))
        additional_notes_count = len(as_list(hoja_payload.get("informacionAdicional")))
        marginal_annotations_count = len(as_list(hoja_payload.get("anotacionMarginal")))

        candidate_name = str(payload.get("candidate") or "").strip()
        party_name = str(payload.get("party") or "").strip()
        member = FormulaMember(
            organization_id=int(metadata.get("organization_id") or source_row.get("idOrganizacionPolitica") or 0),
            party_name=party_name,
            party_slug=slugify(party_name),
            candidate_name=candidate_name,
            office=office,
            position=int(metadata.get("position") or source_row.get("intPosicion") or 0),
            document_number=source_row.get("strDocumentoIdentidad"),
            photo_url=metadata.get("photo_url"),
            party_logo_url=metadata.get("party_logo_url"),
            hoja_vida_id=metadata.get("hoja_vida_id"),
            hoja_vida_url=metadata.get("hoja_vida_url"),
            local_hoja_vida_path=metadata.get("local_hoja_vida_path"),
            annual_income_total=annual_income_total,
            public_income_total=public_income_total,
            private_income_total=private_income_total,
            movable_assets_count=movable_count,
            immovable_assets_count=immovable_count,
            assets_declared_value=assets_value,
            legal_entities_count=legal_entities_count,
            labor_records_count=labor_records_count,
            renuncia_records_count=renuncia_records_count,
            elected_offices_count=elected_count,
            party_roles_count=party_roles_count,
            technical_education_count=technical_education_count,
            non_university_education_count=non_university_education_count,
            university_education_count=university_education_count,
            academic_records_count=technical_education_count + non_university_education_count + university_education_count,
            postgraduate_records_count=postgraduate_records_count,
            penal_sentences_count=penal_count,
            civil_sentences_count=civil_count,
            obligations_count=obligations_count,
            additional_notes_count=additional_notes_count,
            marginal_annotations_count=marginal_annotations_count,
            summary=build_summary(
                candidate_name=candidate_name,
                office=office,
                annual_income_total=annual_income_total,
                labor_records=labor_records_count,
                penal_count=penal_count,
                civil_count=civil_count,
                elected_count=elected_count,
            ),
            metrics_json={
                "dato_general": as_dict(hoja_payload.get("datoGeneral")),
                "education": as_dict(hoja_payload.get("formacionAcademica")),
                "trajectory": as_dict(hoja_payload.get("trayectoria")),
                "declaration": as_dict(hoja_payload.get("declaracionJurada")),
                "work_experience": as_list(hoja_payload.get("experienciaLaboral")),
                "renuncias": as_list(hoja_payload.get("renunciaEfectuada")),
                "additional_information": as_list(hoja_payload.get("informacionAdicional")),
                "penal_sentences": as_list(hoja_payload.get("sentenciaPenal")),
                "civil_sentences": as_list(hoja_payload.get("sentenciaCivil")),
                "obligations": as_list(hoja_payload.get("sentenciaObliga")),
                "marginal_annotations": as_list(hoja_payload.get("anotacionMarginal")),
            },
            raw_json=hoja_payload or None,
        )
        db.add(member)
        imported += 1

    db.commit()
    db.close()
    print(f"Importación de fórmulas y hojas de vida completada: {imported} miembros.")


if __name__ == "__main__":
    run()
