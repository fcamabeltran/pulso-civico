from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from app.models.candidate import Candidate

JNE_DOWNLOAD_ROOT = Path("/app/data/downloads/jne_voto_informado")
GENERIC_BIO_PREFIXES = (
    "Importado desde el corpus local",
    "Importado desde la fuente oficial",
    "Importado desde recopilación documental",
)

TOPIC_KEYWORDS = {
    "seguridad": (
        "seguridad",
        "delincuencia",
        "crimen",
        "extorsion",
        "extorsiones",
        "policia",
        "policial",
    ),
    "salud": (
        "salud",
        "hospital",
        "hospitales",
        "sis",
        "essalud",
        "medico",
        "medicos",
    ),
    "educación": (
        "educacion",
        "escuela",
        "escuelas",
        "colegio",
        "colegios",
        "universidad",
        "universidades",
        "docente",
        "docentes",
    ),
    "economía": (
        "economia",
        "empleo",
        "empresa",
        "empresas",
        "formalizacion",
        "inversion",
        "produccion",
        "tribut",
    ),
    "infraestructura": (
        "infraestructura",
        "carretera",
        "carreteras",
        "puente",
        "puentes",
        "agua",
        "saneamiento",
        "transporte",
    ),
    "gobernanza": (
        "corrupcion",
        "transparencia",
        "estado",
        "institucional",
        "justicia",
        "reforma",
        "gestion publica",
    ),
    "ambiente": (
        "ambient",
        "agua",
        "forest",
        "clima",
        "mineria",
        "contaminacion",
        "sostenible",
    ),
}


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.lower()
    ascii_value = re.sub(r"[^a-z0-9]+", " ", ascii_value)
    return re.sub(r"\s+", " ", ascii_value).strip()


def _party_key(value: str) -> str:
    normalized = _normalize_text(value)
    normalized = re.sub(r"\bpartido politico\b", " ", normalized)
    normalized = re.sub(r"\bpartido democratico\b", " ", normalized)
    normalized = re.sub(r"\bpartido democrata\b", " ", normalized)
    normalized = re.sub(r"\bpartido\b", " ", normalized)
    normalized = re.sub(r"\balianza electoral\b", " ", normalized)
    normalized = re.sub(r"\balianza\b", " ", normalized)
    normalized = re.sub(r"\bde integracion social\b", " ", normalized)
    normalized = re.sub(r"\ban\b", " ", normalized)
    normalized = re.sub(r"\b2021\b", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()

    synonyms = {
        "partido si creo": "sicreo",
        "si creo": "sicreo",
        "venceremos": "venceremos",
        "partido alianza venceremos": "venceremos",
        "frente de la esperanza": "frente esperanza",
        "somos peru": "somos peru",
        "unido peru": "unido peru",
        "peru moderno": "peru moderno",
        "avanza pais": "avanza pais",
        "ahora nacion": "ahora nacion",
        "fuerza y libertad": "fuerza y libertad",
        "unidad nacional": "unidad nacional",
    }
    return synonyms.get(normalized, normalized)


@lru_cache(maxsize=1)
def _load_presidential_jne_index() -> dict[str, dict]:
    index: dict[str, dict] = {}
    for metadata_path in JNE_DOWNLOAD_ROOT.rglob("metadata.json"):
        payload = json.loads(metadata_path.read_text(encoding="utf-8"))
        metadata = payload.get("metadata") or {}
        if metadata.get("formula_role") != "PRESIDENTE DE LA REPÚBLICA":
            continue
        party_name = payload.get("party")
        if not party_name:
            continue
        key = _party_key(party_name)
        index[key] = {
            "candidate_name": payload.get("candidate"),
            "party_name": party_name,
            "photo_url": metadata.get("photo_url"),
            "party_logo_url": metadata.get("party_logo_url"),
            "summary_pdf_url": metadata.get("summary_pdf_url"),
            "full_plan_pdf_url": metadata.get("full_plan_pdf_url"),
            "hoja_vida_url": metadata.get("hoja_vida_url"),
            "hoja_vida_summary": metadata.get("hoja_vida_summary"),
            "source_catalog_url": metadata.get("source_catalog_url"),
            "organization_id": metadata.get("organization_id"),
        }
    return index


def _topic_priority(text: str) -> list[str]:
    normalized = _normalize_text(text)
    scores: list[tuple[int, str]] = []
    for topic, keywords in TOPIC_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            score += normalized.count(keyword)
        if score:
            scores.append((score, topic))
    scores.sort(key=lambda item: (-item[0], item[1]))
    return [topic for _, topic in scores[:3]]


def _plan_scale(text: str) -> str:
    size = len(text)
    if size > 80000:
        return "extenso"
    if size > 35000:
        return "amplio"
    return "acotado"


def _chunk_count(text: str, chunk_size: int = 450, overlap: int = 75) -> int:
    if not text:
        return 0
    count = 0
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        count += 1
        if end == len(text):
            break
        start = end - overlap
    return count


def _build_biography(candidate: Candidate) -> str:
    proposals = getattr(candidate, "proposals", None) or []
    plan_text = " ".join(proposal.content for proposal in proposals if proposal.content).strip()
    if not plan_text:
        return (
            "Ficha orientada a voto informado con base en documentos públicos. "
            "Todavía no hay suficiente texto procesado para resumir prioridades programáticas con utilidad ciudadana."
        )

    topics = _topic_priority(plan_text)
    if topics:
        if len(topics) == 1:
            topic_text = topics[0]
        elif len(topics) == 2:
            topic_text = f"{topics[0]} y {topics[1]}"
        else:
            topic_text = f"{topics[0]}, {topics[1]} y {topics[2]}"
    else:
        topic_text = "temas de gestión pública"

    plan_scale = _plan_scale(plan_text)
    chunk_count = _chunk_count(plan_text)
    return (
        f"Resumen de lectura cívica del plan presidencial de {candidate.party}: prioriza {topic_text}. "
        f"El documento cargado es {plan_scale} y esta ficha lo organiza en {chunk_count} fragmento"
        f"{'' if chunk_count == 1 else 's'} consultables para comparar propuestas, revisar fuentes y detectar vacíos."
    )


def enrich_candidate(candidate: Candidate) -> Candidate:
    current_metadata = dict(candidate.metadata_json or {})
    jne_metadata = _load_presidential_jne_index().get(_party_key(candidate.party), {})

    if jne_metadata.get("candidate_name"):
        imported_name = (candidate.name or "").strip()
        official_name = str(jne_metadata["candidate_name"]).strip()
        if imported_name and imported_name != official_name:
            current_metadata.setdefault("imported_candidate_name", imported_name)
        candidate.name = official_name

    if jne_metadata.get("party_name"):
        imported_party = (candidate.party or "").strip()
        official_party = str(jne_metadata["party_name"]).strip()
        if imported_party and imported_party != official_party:
            current_metadata.setdefault("imported_party_name", imported_party)
        candidate.party = official_party

    for key in (
        "photo_url",
        "party_logo_url",
        "summary_pdf_url",
        "full_plan_pdf_url",
        "hoja_vida_url",
        "source_catalog_url",
        "organization_id",
    ):
        if not current_metadata.get(key) and jne_metadata.get(key):
            current_metadata[key] = jne_metadata[key]

    if not current_metadata.get("hoja_vida_summary") and jne_metadata.get("hoja_vida_summary"):
        current_metadata["hoja_vida_summary"] = jne_metadata["hoja_vida_summary"]

    if jne_metadata.get("candidate_name"):
        current_metadata.setdefault("official_candidate_name", jne_metadata["candidate_name"])
    if jne_metadata.get("party_name"):
        current_metadata.setdefault("official_party_name", jne_metadata["party_name"])

    biography = (candidate.biography or "").strip()
    if not biography or biography.startswith(GENERIC_BIO_PREFIXES):
        candidate.biography = _build_biography(candidate)

    candidate.metadata_json = current_metadata
    return candidate
