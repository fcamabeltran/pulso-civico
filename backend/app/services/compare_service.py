import json
import re

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ai.providers import build_llm_provider
from app.core.config import get_settings
from app.models.candidate import Candidate
from app.models.proposal import Proposal
from app.schemas.compare import CompareInsights, CompareResponse
from app.services.candidate_enrichment_service import enrich_candidate

THEME_DEFINITIONS = {
    "seguridad": ["seguridad", "delincu", "polic", "extorsi", "crimen", "violencia"],
    "salud": ["salud", "hospital", "sis", "essalud", "medic", "sanitario"],
    "educacion": ["educa", "escuela", "coleg", "docent", "universi", "beca"],
    "economia": ["econom", "emple", "empresa", "inversion", "formal", "tribut"],
    "corrupcion": ["corrup", "transparen", "contralor", "integridad", "anticorr"],
    "gobernabilidad": ["institu", "estado", "justicia", "reforma", "gestion publica", "gobern"],
    "ambiente": ["ambient", "clima", "forest", "agua", "mineria", "contamina"],
    "infraestructura": ["infraestructura", "carretera", "puente", "transporte", "saneamiento", "vivienda"],
}


def _truncate(text: str, length: int = 260) -> str:
    text = " ".join(text.split())
    if len(text) <= length:
        return text
    return f"{text[:length].rstrip()}..."


def _clean_insight_text(text: str, max_length: int = 260) -> str:
    cleaned = " ".join(text.split())
    cleaned = cleaned.replace("  ", " ").strip()
    cleaned = cleaned.replace("Por otro lado,", "En cambio,")
    cleaned = cleaned.replace("Además,", "Además ")
    return _truncate(cleaned, max_length)


def _normalize(text: str) -> str:
    return " ".join(text.lower().split())


def _extract_theme_snippets(text: str, keywords: list[str], max_snippets: int = 2) -> list[str]:
    compact = " ".join(text.split())
    lower = compact.lower()
    snippets: list[str] = []

    for keyword in keywords:
        for match in re.finditer(re.escape(keyword), lower):
            start = max(0, match.start() - 170)
            end = min(len(compact), match.end() + 220)
            snippet = compact[start:end].strip(" .,;:\n")
            if snippet and snippet not in snippets:
                snippets.append(_truncate(snippet, 260))
            if len(snippets) >= max_snippets:
                return snippets
    return snippets


def _group_proposals(proposals: list[Proposal]) -> dict[str, list[Proposal]]:
    grouped: dict[str, list[Proposal]] = {}
    for proposal in proposals:
        grouped.setdefault(proposal.axis, []).append(proposal)
    return grouped


def _fallback_insights(left: Candidate, right: Candidate, left_proposals: list[Proposal], right_proposals: list[Proposal]) -> CompareInsights:
    left_axes = {proposal.axis for proposal in left_proposals}
    right_axes = {proposal.axis for proposal in right_proposals}
    shared_axes = sorted(left_axes & right_axes)
    left_only = sorted(left_axes - right_axes)
    right_only = sorted(right_axes - left_axes)

    differences = (
        f"La comparación muestra diferencias de cobertura temática: {left.name} desarrolla {', '.join(left_only[:3]) or 'temas similares'} "
        f"que no aparecen con el mismo peso en {right.name}, mientras que {right.name} enfatiza {', '.join(right_only[:3]) or 'temas similares'}."
    )
    coincidences = (
        f"Ambos candidatos sí presentan contenido comparable en {', '.join(shared_axes[:4]) or 'los temas disponibles del corpus'}."
    )
    detail = (
        f"El mayor nivel de lectura comparativa aparece donde existen más fragmentos documentados por ambos lados: "
        f"{', '.join(shared_axes[:3]) or 'aún no hay suficiente superposición temática'}."
    )
    evidence_gaps = (
        "La ausencia de evidencia sigue dependiendo del corpus cargado: cuando un tema no aparece en los fragmentos disponibles, "
        "la plataforma debe tratarlo como vacío documental y no como postura confirmada."
    )
    return CompareInsights(
        differences=differences,
        coincidences=coincidences,
        detail=detail,
        evidence_gaps=evidence_gaps,
    )


def _build_compare_context(left: Candidate, right: Candidate, left_proposals: list[Proposal], right_proposals: list[Proposal]) -> str:
    left_text = " ".join(proposal.content for proposal in left_proposals)
    right_text = " ".join(proposal.content for proposal in right_proposals)

    blocks: list[str] = []
    for theme, keywords in THEME_DEFINITIONS.items():
        left_lines = [f"- {snippet}" for snippet in _extract_theme_snippets(left_text, keywords)] or [
            "- [AUSENCIA DE EVIDENCIA] Sin fragmentos relevantes en este tema."
        ]
        right_lines = [f"- {snippet}" for snippet in _extract_theme_snippets(right_text, keywords)] or [
            "- [AUSENCIA DE EVIDENCIA] Sin fragmentos relevantes en este tema."
        ]
        blocks.append(
            "\n".join(
                [
                    f"Tema: {theme}",
                    f"{left.name}:",
                    *left_lines,
                    f"{right.name}:",
                    *right_lines,
                ]
            )
        )
    return "\n\n".join(blocks)


def _generate_insights(left: Candidate, right: Candidate, left_proposals: list[Proposal], right_proposals: list[Proposal]) -> CompareInsights:
    settings = get_settings()
    provider = build_llm_provider(settings)
    context = _build_compare_context(left, right, left_proposals, right_proposals)
    question = f"""
Compara a {left.name} y {right.name} usando solo el contexto documental dado.

Responde SOLO en JSON válido con esta forma exacta:
{{
  "differences": "texto",
  "coincidences": "texto",
  "detail": "texto",
  "evidence_gaps": "texto"
}}

Reglas:
- No recomiendes por quién votar.
- No uses puntajes.
- No digas que son similares si el contexto muestra enfoques distintos.
- Describe diferencias reales de enfoque, cobertura o nivel de concreción.
- Si falta evidencia, dilo explícitamente.
- Cada campo debe tener 1 o 2 oraciones útiles, específicas y breves.
- No inventes cifras, número de ejes, capítulos, metas ni porcentajes si no aparecen literalmente en el contexto.
- Evita frases genéricas como "patrones similares" salvo que el contexto realmente no muestre diferencias claras.
- Evita repetir el nombre completo de cada candidato más de una vez por campo.
- Escribe como resumen editorial neutral para una plataforma cívica: claro, sobrio y escaneable.
""".strip()

    try:
        raw = provider.generate(question=question, context=context).strip()
        start = raw.find("{")
        end = raw.rfind("}")
        if start == -1 or end == -1:
            raise ValueError("No JSON object found in LLM response")
        payload = json.loads(raw[start : end + 1])
        return CompareInsights(
            differences=_clean_insight_text(str(payload["differences"]).strip()),
            coincidences=_clean_insight_text(str(payload["coincidences"]).strip()),
            detail=_clean_insight_text(str(payload["detail"]).strip(), max_length=320),
            evidence_gaps=_clean_insight_text(str(payload["evidence_gaps"]).strip()),
        )
    except Exception:
        return _fallback_insights(left, right, left_proposals, right_proposals)


def compare_candidates(db: Session, left_id: int, right_id: int) -> CompareResponse:
    left = db.get(Candidate, left_id)
    right = db.get(Candidate, right_id)
    if not left or not right:
        raise HTTPException(status_code=404, detail="Uno o ambos candidatos no existen.")

    left_proposals = list(
        db.scalars(select(Proposal).where(Proposal.candidate_id == left_id).order_by(Proposal.axis, Proposal.title)).all()
    )
    right_proposals = list(
        db.scalars(select(Proposal).where(Proposal.candidate_id == right_id).order_by(Proposal.axis, Proposal.title)).all()
    )

    left.proposals = left_proposals
    right.proposals = right_proposals
    left = enrich_candidate(left)
    right = enrich_candidate(right)

    insights = _generate_insights(left, right, left_proposals, right_proposals)

    return CompareResponse(
        left_candidate=left,
        right_candidate=right,
        left_proposals=left_proposals,
        right_proposals=right_proposals,
        insights=insights,
    )
