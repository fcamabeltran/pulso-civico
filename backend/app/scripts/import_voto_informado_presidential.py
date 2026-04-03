from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sqlalchemy import delete

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Candidate, PromiseTracking, Proposal

API_CANDIDATES = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/listarCanditatos"
API_ADVANCED_SEARCH = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/avanzada-voto"
API_PLAN = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/plangobierno"
API_PLAN_DETAIL = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/detalle-plangobierno"
API_HOJA_VIDA = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/hojavida"
IMAGE_BASE_URL = "https://mpesije.jne.gob.pe/apidocs/"
PARTY_LOGO_URL = "https://votoinformado.jne.gob.pe/LogoOp/"
DOWNLOAD_ROOT = Path("/app/data/downloads/jne_voto_informado")
SNAPSHOT_PATH = DOWNLOAD_ROOT / "presidential_catalog.json"

PROCESS_ID = 124
PRESIDENTIAL_ELECTION_TYPE = 1

AXIS_LABELS = {
    "dimensionSocial": "Dimensión social",
    "dimensionEconomica": "Dimensión económica",
    "dimensionAmbiental": "Dimensión ambiental",
    "dimensionInstitucional": "Dimensión institucional",
}


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    compact = re.sub(r"[^a-zA-Z0-9]+", "-", ascii_value.lower()).strip("-")
    return compact or "sin-nombre"


def post_json(url: str, payload: dict[str, Any]) -> dict[str, Any]:
    request = Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    with urlopen(request, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def get_json(url: str) -> dict[str, Any]:
    with urlopen(url, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


def download_file(url: str | None, destination: Path) -> str | None:
    if not url:
        return None
    destination.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urlopen(url, timeout=120) as response:
            destination.write_bytes(response.read())
    except (HTTPError, URLError, TimeoutError):
        return None
    return str(destination)


def candidate_name_from_row(row: dict[str, Any]) -> str:
    parts = [
        row.get("strNombres", "").strip(),
        row.get("strApellidoPaterno", "").strip(),
        row.get("strApellidoMaterno", "").strip(),
    ]
    return " ".join(part for part in parts if part).strip()


def candidate_payload() -> dict[str, Any]:
    return {
        "idProcesoElectoral": PROCESS_ID,
        "strUbiDepartamento": "",
        "idTipoEleccion": PRESIDENTIAL_ELECTION_TYPE,
    }


def plan_payload(organization_id: int) -> dict[str, Any]:
    return {
        "pageSize": 10,
        "skip": 1,
        "filter": {
            "idProcesoElectoral": PROCESS_ID,
            "idTipoEleccion": str(PRESIDENTIAL_ELECTION_TYPE),
            "idOrganizacionPolitica": str(organization_id),
            "txDatoCandidato": "",
            "idJuradoElectoral": "0",
        },
    }


def advanced_payload(organization_id: int) -> dict[str, Any]:
    return {
        "pageSize": 10,
        "skip": 1,
        "filter": {
            "IdTipoEleccion": str(PRESIDENTIAL_ELECTION_TYPE),
            "IdOrganizacionPolitica": organization_id,
            "ubigeo": "0",
            "IdAnioExperiencia": 0,
            "cargoOcupado": [0],
            "IdSentenciaDeclarada": 0,
            "IdGradoAcademico": 0,
            "IdExpedienteDadiva": 0,
            "IdProcesoElectoral": PROCESS_ID,
            "IdEstado": 0,
        },
    }


def build_proposal(axis_key: str, item: dict[str, Any], source_url: str) -> dict[str, str]:
    problem = item.get("txPgProblema", "").strip()
    objective = item.get("txPgObjetivo", "").strip()
    indicator = item.get("txPgIndicador", "").strip()
    goal = item.get("txPgMeta", "").strip()

    title = objective or problem or "Medida programática"
    content_parts = []
    if problem:
        content_parts.append(f"Problema identificado: {problem}.")
    if objective:
        content_parts.append(f"Objetivo: {objective}.")
    if indicator:
        content_parts.append(f"Indicador: {indicator}.")
    if goal:
        content_parts.append(f"Meta: {goal}.")

    return {
        "axis": AXIS_LABELS.get(axis_key, axis_key),
        "title": title[:255],
        "content": " ".join(content_parts).strip() or title,
        "source_name": "Voto Informado JNE",
        "source_url": source_url,
    }


def extract_records(container: Any, key: str) -> list[Any]:
    if isinstance(container, list):
        return container
    if isinstance(container, dict):
        value = container.get(key, [])
        return value if isinstance(value, list) else []
    return []


def get_hoja_vida_record(
    organization_id: int,
    document_number: str | None,
    office: str | None,
) -> dict[str, Any] | None:
    if not document_number:
        return None
    advanced = post_json(API_ADVANCED_SEARCH, advanced_payload(organization_id))
    for item in advanced.get("data", []):
        if item.get("numeroDocumento") == document_number and item.get("cargo") == office:
            hoja_vida_id = item.get("idHojaVida")
            if not hoja_vida_id:
                return None
            detail = get_json(f"{API_HOJA_VIDA}?idHojaVida={hoja_vida_id}")
            detail["idHojaVida"] = hoja_vida_id
            return detail
    return None


def run() -> None:
    Base.metadata.create_all(bind=engine)
    DOWNLOAD_ROOT.mkdir(parents=True, exist_ok=True)

    raw_candidates = post_json(API_CANDIDATES, candidate_payload())
    SNAPSHOT_PATH.write_text(json.dumps(raw_candidates, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = raw_candidates.get("data", [])
    presidential_rows = [
        row
        for row in rows
        if row.get("strEstadoCandidato") not in {"IMPROCEDENTE", "RENUNCIA", "FALLECIDO"}
    ]

    db = SessionLocal()
    db.execute(delete(PromiseTracking))
    db.execute(delete(Proposal))
    db.execute(delete(Candidate))
    db.commit()

    imported = 0
    proposal_count = 0
    plan_cache: dict[int, dict[str, Any] | None] = {}
    plan_detail_cache: dict[int, dict[str, Any]] = {}
    advanced_cache: dict[int, list[dict[str, Any]]] = {}

    for row in sorted(presidential_rows, key=lambda item: candidate_name_from_row(item)):
        organization_id = int(row["idOrganizacionPolitica"])
        party_name = row["strOrganizacionPolitica"].strip()
        candidate_name = candidate_name_from_row(row)
        base_folder = DOWNLOAD_ROOT / slugify(party_name) / slugify(candidate_name)

        photo_name = row.get("strNombre", "").strip()
        photo_url = f"{IMAGE_BASE_URL}{photo_name}" if photo_name else None
        logo_url = f"{PARTY_LOGO_URL}{organization_id}.jpg"
        document_number = row.get("strDocumentoIdentidad")
        office = row.get("strCargo") or "Cargo no especificado"

        if organization_id not in plan_cache:
            plan_response = post_json(API_PLAN, plan_payload(organization_id))
            plan_cache[organization_id] = (plan_response.get("data") or [None])[0]
        plan_item = plan_cache[organization_id]
        plan_id = plan_item.get("idPlanGobierno") if plan_item else None
        summary_url = plan_item.get("txRutaResumen") if plan_item else None
        full_plan_url = plan_item.get("txRutaCompleto") if plan_item else None

        summary_local = download_file(summary_url, base_folder / "summary.pdf")
        full_plan_local = download_file(full_plan_url, base_folder / "full_plan.pdf")
        if organization_id not in advanced_cache:
            advanced_cache[organization_id] = post_json(API_ADVANCED_SEARCH, advanced_payload(organization_id)).get("data", [])
        hoja_vida_payload = None
        if document_number:
            for item in advanced_cache[organization_id]:
                if item.get("numeroDocumento") == document_number and item.get("cargo") == office:
                    hoja_vida_id = item.get("idHojaVida")
                    if hoja_vida_id:
                        hoja_vida_payload = get_json(f"{API_HOJA_VIDA}?idHojaVida={hoja_vida_id}")
                        hoja_vida_payload["idHojaVida"] = hoja_vida_id
                    break
        hoja_vida_id = hoja_vida_payload.get("idHojaVida") if hoja_vida_payload else None
        hoja_vida_url = f"{API_HOJA_VIDA}?idHojaVida={hoja_vida_id}" if hoja_vida_id else None
        hoja_vida_local = None
        hoja_vida_summary: dict[str, Any] | None = None
        if hoja_vida_payload:
            hoja_vida_path = base_folder / "hoja_vida.json"
            hoja_vida_path.parent.mkdir(parents=True, exist_ok=True)
            hoja_vida_path.write_text(json.dumps(hoja_vida_payload, ensure_ascii=False, indent=2), encoding="utf-8")
            hoja_vida_local = str(hoja_vida_path)
            hoja_vida_summary = {
                "experiencia_laboral_registros": len(hoja_vida_payload.get("experienciaLaboral") or []),
                "sentencias_penales_registros": len(extract_records(hoja_vida_payload.get("sentenciaPenal"), "sentenciaPenal")),
                "sentencias_civiles_registros": len(extract_records(hoja_vida_payload.get("sentenciaCivil"), "sentenciaCivil")),
                "declaracion_bienes_registros": len(extract_records(hoja_vida_payload.get("declaracionPatrimonial"), "bienMueble"))
                + len(extract_records(hoja_vida_payload.get("declaracionPatrimonial"), "bienInmueble")),
            }

        metadata = {
            "imported_from": "Voto Informado JNE",
            "source_name": "Voto Informado JNE",
            "source_catalog_url": "https://votoinformado.jne.gob.pe/presidente-vicepresidentes",
            "party_logo_url": logo_url,
            "photo_url": photo_url,
            "summary_pdf_url": summary_url,
            "full_plan_pdf_url": full_plan_url,
            "local_summary_path": summary_local,
            "local_full_plan_path": full_plan_local,
            "organization_id": organization_id,
            "plan_id": plan_id,
            "document_number": document_number,
            "candidate_status": row.get("strEstadoCandidato"),
            "position": row.get("intPosicion"),
            "formula_role": office,
            "hoja_vida_id": hoja_vida_id,
            "hoja_vida_url": hoja_vida_url,
            "local_hoja_vida_path": hoja_vida_local,
            "hoja_vida_summary": hoja_vida_summary,
        }

        candidate = Candidate(
            name=candidate_name,
            party=party_name,
            region="Perú",
            office=office,
            biography=(
                "Ficha importada desde la fuente oficial del JNE. "
                "Incluye foto, logo partidario y enlaces al resumen y plan de gobierno."
            ),
            metadata_json=metadata,
        )
        db.add(candidate)
        db.flush()

        detail_payload: dict[str, Any] = {}
        if plan_id:
            if plan_id not in plan_detail_cache:
                plan_detail_cache[plan_id] = get_json(f"{API_PLAN_DETAIL}?IdPlanGobierno={plan_id}")
            detail_payload = plan_detail_cache[plan_id]

        proposals_for_candidate: list[Proposal] = []
        for axis_key in AXIS_LABELS:
            for item in detail_payload.get(axis_key, []):
                proposal = build_proposal(axis_key, item, full_plan_url or summary_url or metadata["source_catalog_url"])
                proposals_for_candidate.append(Proposal(candidate_id=candidate.id, **proposal))

        if proposals_for_candidate:
            db.add_all(proposals_for_candidate)
            proposal_count += len(proposals_for_candidate)

        metadata_path = base_folder / "metadata.json"
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        metadata_path.write_text(
            json.dumps(
                {
                    "candidate": candidate_name,
                    "party": party_name,
                    "source_row": row,
                    "plan": plan_item,
                    "hoja_vida": hoja_vida_summary,
                    "metadata": metadata,
                    "detail_keys": [key for key in detail_payload.keys() if key != "datoGeneral"],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        imported += 1
        db.commit()

    db.close()
    print(f"Importación oficial completada: {imported} candidatos y {proposal_count} propuestas.")


if __name__ == "__main__":
    run()
