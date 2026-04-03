import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from app.ai.providers import build_llm_provider
from app.ai.vector_store import RetrievedChunk, VectorStore
from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models import Candidate, Proposal
from app.schemas.chat import ChatResponse, ChatSource, ChatStructuredResponse, SimplifyResponse
from app.services.candidate_enrichment_service import enrich_candidate
from app.utils.document_chunks import build_chunks_from_pdf

_NO_EVIDENCE_MSG = (
    "[AUSENCIA DE EVIDENCIA] No se encontraron fragmentos relevantes en los documentos "
    "disponibles para responder esta consulta. Es posible que el tema no esté cubierto en "
    "los planes de gobierno indexados, o que los documentos del candidato consultado no "
    "hayan sido procesados aún. Verifica directamente en el portal Voto Informado del JNE."
)

_TAG_PATTERN = re.compile(r"\[(EVIDENCIA DOCUMENTAL|AUSENCIA DE EVIDENCIA|INFERENCIA)\]\s*", re.IGNORECASE)
_ALIAS_STOPWORDS = {
    "partido",
    "politico",
    "democratico",
    "democrata",
    "alianza",
    "electoral",
    "peru",
    "del",
    "de",
    "la",
    "el",
    "los",
    "las",
}
_OPINION_PATTERNS = (
    "que piensa",
    "que opina",
    "cual es su opinion",
    "como ve",
    "que cree",
    "que postura tiene",
)
_TOPIC_HINTS = {
    "econom": "economía y empleo",
    "segur": "seguridad ciudadana",
    "extorsi": "crimen organizado y extorsiones",
    "crimen": "crimen organizado y extorsiones",
    "salud": "salud pública",
    "educ": "educación",
    "corrup": "lucha contra la corrupción",
    "agua": "agua y saneamiento",
    "trabaj": "empleo y trabajo formal",
    "empleo": "economía y empleo",
}
_TOPIC_KEYWORDS = {
    "economía y empleo": (
        "econom",
        "empleo",
        "trabajo",
        "empresa",
        "empresas",
        "inversion",
        "inversión",
        "tribut",
        "formal",
        "productiv",
        "emprend",
        "mercado",
        "competit",
    ),
    "seguridad ciudadana": (
        "seguridad",
        "delito",
        "crimen",
        "extors",
        "policia",
        "polic",
        "violencia",
        "homic",
    ),
    "crimen organizado y extorsiones": (
        "crimen",
        "organizado",
        "extors",
        "maf",
        "delito",
        "sicari",
        "banda",
    ),
    "salud pública": (
        "salud",
        "hospital",
        "sis",
        "essalud",
        "medic",
        "atencion",
        "sanitario",
    ),
    "educación": (
        "educ",
        "escuela",
        "colegio",
        "docente",
        "univers",
        "estudiante",
        "tecnica",
    ),
    "lucha contra la corrupción": (
        "corrup",
        "transpar",
        "control",
        "fiscal",
        "contral",
        "rendicion",
        "integridad",
    ),
    "agua y saneamiento": (
        "agua",
        "saneamiento",
        "desague",
        "alcantar",
        "potable",
        "reservorio",
    ),
}
_COMPARISON_PATTERNS = (
    "diferencias",
    "diferencia",
    "compar",
    "versus",
    " vs ",
    "frente a",
    "entre ",
)


def _normalize_text(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_value = ascii_value.lower()
    ascii_value = re.sub(r"[^a-z0-9]+", " ", ascii_value)
    return re.sub(r"\s+", " ", ascii_value).strip()


def _candidate_tokens(*values: str) -> set[str]:
    tokens: set[str] = set()
    for value in values:
        for token in _normalize_text(value).split():
            if len(token) >= 4 and token not in _ALIAS_STOPWORDS:
                tokens.add(token)
    return tokens


@lru_cache(maxsize=1)
def _candidate_aliases() -> list[dict[str, object]]:
    db = SessionLocal()
    try:
        aliases: list[dict[str, object]] = []
        for candidate in db.query(Candidate).all():
            enriched = enrich_candidate(candidate)
            metadata = dict(enriched.metadata_json or {})
            official_name = str(enriched.name or "").strip()
            imported_name = str(metadata.get("imported_candidate_name") or official_name).strip()
            official_party = str(enriched.party or "").strip()
            imported_party = str(metadata.get("imported_party_name") or official_party).strip()
            aliases.append(
                {
                    "candidate_id": candidate.id,
                    "official_name": official_name,
                    "imported_name": imported_name,
                    "official_party": official_party,
                    "imported_party": imported_party,
                    "tokens": _candidate_tokens(official_name, imported_name, official_party, imported_party),
                    "phrases": {
                        _normalize_text(official_name),
                        _normalize_text(imported_name),
                        _normalize_text(official_party),
                        _normalize_text(imported_party),
                    },
                }
            )
        return aliases
    finally:
        db.close()


def _expand_question_with_aliases(question: str) -> str:
    normalized_question = _normalize_text(question)
    query_tokens = set(normalized_question.split())
    expansions: list[str] = []

    for alias in _candidate_aliases():
        phrases = {phrase for phrase in alias["phrases"] if phrase}
        alias_tokens = set(alias["tokens"])
        token_overlap = len(query_tokens.intersection(alias_tokens))
        phrase_hit = any(phrase and phrase in normalized_question for phrase in phrases)

        if not phrase_hit and token_overlap < 1:
            continue

        official_name = str(alias["official_name"])
        imported_name = str(alias["imported_name"])
        official_party = str(alias["official_party"])
        imported_party = str(alias["imported_party"])
        expansions.extend([official_name, imported_name, official_party, imported_party])

    unique_expansions = [value for value in dict.fromkeys(expansions) if value]
    if not unique_expansions:
        return question
    return f"{question}\n\nAlias relevantes: {' | '.join(unique_expansions[:8])}"


def _match_aliases(question: str) -> list[dict[str, object]]:
    normalized_question = _normalize_text(question)
    query_tokens = set(normalized_question.split())
    matches: list[tuple[int, dict[str, object]]] = []

    for alias in _candidate_aliases():
        phrases = {phrase for phrase in alias["phrases"] if phrase}
        alias_tokens = set(alias["tokens"])
        token_overlap = len(query_tokens.intersection(alias_tokens))
        phrase_hit = any(phrase and phrase in normalized_question for phrase in phrases)
        score = token_overlap + (4 if phrase_hit else 0)
        if score > 0:
            matches.append((score, alias))

    matches.sort(key=lambda item: (-item[0], str(item[1]["official_name"])))
    return [alias for _, alias in matches[:3]]


def _primary_candidate_scope(question: str) -> dict[str, object] | None:
    matches = _match_aliases(question)
    if not matches:
        return None
    return matches[0]


def _comparison_candidate_scopes(question: str) -> list[dict[str, object]]:
    if not any(pattern in _normalize_text(question) for pattern in _COMPARISON_PATTERNS):
        return []
    return _match_aliases(question)[:2]


def _is_comparison_question(question: str) -> bool:
    return any(pattern in _normalize_text(question) for pattern in _COMPARISON_PATTERNS)


def _resolve_source_identity(candidate_name: str, party: str | None) -> tuple[str, str | None]:
    normalized_candidate = _normalize_text(candidate_name)
    normalized_party = _normalize_text(party or "")
    for alias in _candidate_aliases():
        phrases = {phrase for phrase in alias["phrases"] if phrase}
        if normalized_candidate in phrases or (normalized_party and normalized_party in phrases):
            return str(alias["official_name"]), str(alias["official_party"])
    return candidate_name, party


def _chunk_matches_alias(chunk_metadata: dict, alias: dict[str, object]) -> bool:
    candidate_name = _normalize_text(str(chunk_metadata.get("candidate_name", "")))
    party = _normalize_text(str(chunk_metadata.get("party", "")))
    phrases = {phrase for phrase in alias["phrases"] if phrase}
    tokens = set(alias["tokens"])
    chunk_terms = set((candidate_name + " " + party).split())
    return bool(candidate_name in phrases or party in phrases or chunk_terms.intersection(tokens))


def _question_keywords(question: str) -> list[str]:
    keywords: list[str] = []
    for token in _normalize_text(question).split():
        if len(token) >= 4 and token not in _ALIAS_STOPWORDS:
            keywords.append(token)
    return list(dict.fromkeys(keywords))


def _infer_topic_label(question: str) -> str | None:
    normalized_question = _normalize_text(question)
    for hint, label in _TOPIC_HINTS.items():
        if hint in normalized_question:
            return label
    return None


def _topic_keywords(question: str) -> tuple[str | None, tuple[str, ...]]:
    label = _infer_topic_label(question)
    if not label:
        return None, ()
    return label, _TOPIC_KEYWORDS.get(label, ())


def _rewrite_question_for_retrieval(question: str, alias: dict[str, object] | None) -> str:
    normalized_question = _normalize_text(question)
    has_opinion_pattern = any(pattern in normalized_question for pattern in _OPINION_PATTERNS)
    topic_label = _infer_topic_label(question)

    if not has_opinion_pattern and topic_label is None:
        return question

    subject = "el candidato"
    if alias:
        subject = str(alias["official_name"])

    topic_part = f"sobre {topic_label}" if topic_label else "sobre este tema"
    return (
        f"{question}\n\n"
        f"Reformula esta consulta como búsqueda documental de propuestas del plan de gobierno de {subject} "
        f"{topic_part}. Prioriza medidas, acciones, metas, mecanismos o ausencia de evidencia, "
        "no opiniones personales."
    )


def _extract_candidate_chunks(question: str, alias: dict[str, object], limit: int) -> list[dict[str, object]]:
    candidate_id = alias.get("candidate_id")
    if not candidate_id:
        return []

    db = SessionLocal()
    try:
        candidate = db.query(Candidate).filter(Candidate.id == int(candidate_id)).one_or_none()
        proposals = (
            db.query(Proposal)
            .filter(Proposal.candidate_id == int(candidate_id))
            .order_by(Proposal.id.asc())
            .all()
        )
    finally:
        db.close()

    keywords = _question_keywords(question)
    topic_label, topic_keywords = _topic_keywords(question)
    ranked: list[tuple[int, dict[str, object]]] = []
    candidate_metadata = dict(candidate.metadata_json or {}) if candidate else {}
    local_plan_path = candidate_metadata.get("local_full_plan_path")

    if isinstance(local_plan_path, str) and local_plan_path:
        try:
            _, pdf_chunks = build_chunks_from_pdf(Path(local_plan_path))
            for index, chunk in enumerate(pdf_chunks):
                normalized_segment = _normalize_text(chunk.text)
                score = 0
                for keyword in keywords:
                    if keyword in normalized_segment:
                        score += normalized_segment.count(keyword) + 2
                topic_hits = sum(normalized_segment.count(keyword) for keyword in topic_keywords)
                if topic_hits:
                    score += topic_hits * 5
                elif topic_keywords:
                    score -= 3
                if score <= 0:
                    continue
                ranked.append(
                    (
                        score,
                        {
                            "text": chunk.text[:700],
                            "metadata": {
                                "candidate_name": alias["official_name"],
                                "party": alias["official_party"],
                                "axis": "Plan de gobierno",
                                "title": f"Plan de gobierno completo - {alias['official_party']}",
                                "source_name": "LP Derecho",
                                "source_url": str(candidate_metadata.get("full_plan_pdf_url") or ""),
                                "page_number": chunk.page_number,
                                "segment_index": index,
                            },
                        },
                    )
                )
        except Exception:
            pass

    if ranked:
        ranked.sort(key=lambda item: (-item[0], item[1]["metadata"]["page_number"] or 0, item[1]["metadata"]["segment_index"]))
        return [payload for _, payload in ranked[:limit]]

    for proposal in proposals:
        segments = [segment.strip() for segment in re.split(r"\n{2,}", proposal.content) if segment.strip()]
        if not segments and proposal.content.strip():
            segments = [proposal.content.strip()]

        for index, segment in enumerate(segments):
            normalized_segment = _normalize_text(segment)
            score = 0
            for keyword in keywords:
                if keyword in normalized_segment:
                    score += normalized_segment.count(keyword) + 2
            topic_hits = sum(normalized_segment.count(keyword) for keyword in topic_keywords)
            if topic_hits:
                score += topic_hits * 5
            elif topic_keywords:
                score -= 3
            if proposal.axis and _normalize_text(proposal.axis) in _normalize_text(question):
                score += 2
            if topic_label and topic_label in _normalize_text(proposal.title):
                score += 3
            if proposal.title and _normalize_text(proposal.title) in _normalize_text(question):
                score += 1
            if score <= 0:
                continue
            ranked.append(
                (
                    score,
                    {
                        "text": segment[:700],
                        "metadata": {
                            "candidate_name": alias["official_name"],
                            "party": alias["official_party"],
                            "axis": proposal.axis,
                            "title": proposal.title,
                            "source_name": proposal.source_name,
                            "source_url": proposal.source_url,
                            "segment_index": index,
                        },
                    },
                )
            )

    ranked.sort(key=lambda item: (-item[0], item[1]["metadata"]["title"], item[1]["metadata"]["segment_index"]))
    return [payload for _, payload in ranked[:limit]]


def _candidate_absence_message(alias: dict[str, object], question: str) -> str:
    official_name = str(alias["official_name"])
    official_party = str(alias["official_party"])
    return (
        f"[AUSENCIA DE EVIDENCIA] No se encontraron fragmentos relevantes de {official_name} "
        f"({official_party}) para responder esta consulta en el corpus indexado. "
        "Es posible que ese tema no esté cubierto explícitamente en su plan disponible o que la "
        "evidencia relevante no haya quedado bien capturada en los documentos procesados."
    )


def _candidate_scope_prefix(alias: dict[str, object]) -> str:
    official_name = str(alias["official_name"])
    official_party = str(alias["official_party"])
    imported_name = str(alias["imported_name"])
    return (
        "ALCANCE OBLIGATORIO:\n"
        f"- Responde solo sobre {official_name} ({official_party}).\n"
        f"- Trata el plan de gobierno del partido {official_party} como el plan presidencial asociado a {official_name}.\n"
        f"- Si aparece el nombre importado {imported_name}, entiéndelo como alias técnico del mismo registro documental.\n"
        "- No exijas que el nombre del candidato aparezca literalmente dentro del PDF para reconocer la autoría política del plan.\n"
        "- Si la evidencia disponible no alcanza para responder, di ausencia de evidencia.\n"
        "- No cambies a otro candidato ni uses fragmentos de otras candidaturas como sustituto.\n"
    )


def _comparison_scope_prefix(aliases: list[dict[str, object]]) -> str:
    if len(aliases) < 2:
        return ""
    left = aliases[0]
    right = aliases[1]
    return (
        "ALCANCE OBLIGATORIO DE COMPARACIÓN:\n"
        f"- Compara solo a {left['official_name']} ({left['official_party']}) y "
        f"{right['official_name']} ({right['official_party']}).\n"
        "- Usa criterios simétricos y el mismo nivel de detalle para ambos.\n"
        "- Señala diferencias concretas en propuestas, enfoque, metas, mecanismos o vacíos.\n"
        "- Si uno de los dos no tiene evidencia suficiente en el tema, dilo explícitamente.\n"
        "- No cambies a otros candidatos ni generalices fuera de estos dos planes.\n"
        "- Estructura la respuesta EXACTAMENTE así:\n"
        "Diferencia principal: [1 frase]\n"
        f"{left['official_name']}: [2 o 3 puntos breves con evidencia]\n"
        f"{right['official_name']}: [2 o 3 puntos breves con evidencia]\n"
        "Vacíos de evidencia: [solo si aplica]\n"
        "Cierre: [1 frase breve ofreciendo profundizar]\n"
        "- Evita títulos decorativos, markdown innecesario o introducciones largas.\n"
        "- Prioriza contraste útil para el lector y no repitas el nombre del partido en cada línea si no hace falta.\n"
    )


def _clean_line(value: str) -> str:
    cleaned = re.sub(r"^\s*[-*•\d\.\)\(]+\s*", "", value.strip())
    cleaned = _TAG_PATTERN.sub("", cleaned).strip(" :.-")
    return " ".join(cleaned.split())


def _split_segments(answer: str) -> list[str]:
    raw_segments = re.split(r"\n{2,}|\n(?=[-*•\d])", answer)
    segments: list[str] = []
    for raw in raw_segments:
        cleaned = raw.strip()
        if cleaned:
            segments.append(cleaned)
    return segments


def _extract_tagged_items(answer: str, label: str) -> list[str]:
    items: list[str] = []
    for segment in _split_segments(answer):
        if f"[{label}]".lower() in segment.lower():
            cleaned = _clean_line(segment)
            if cleaned:
                items.append(cleaned)
    return items


def _build_follow_ups(question: str, sources: list[ChatSource]) -> list[str]:
    axes = [source.axis for source in sources if source.axis]
    candidates = [source.candidate_name for source in sources if source.candidate_name]
    unique_axes = list(dict.fromkeys(axes))
    unique_candidates = list(dict.fromkeys(candidates))
    topic_label = _infer_topic_label(question)
    human_topic = topic_label or (unique_axes[0] if unique_axes and unique_axes[0] != "Plan de gobierno" else "este tema")
    is_comparison = _is_comparison_question(question)

    follow_ups: list[str] = []
    if is_comparison and len(unique_candidates) >= 2:
        follow_ups.append(f"¿Quién tiene propuestas más concretas en {human_topic}: {unique_candidates[0]} o {unique_candidates[1]}?")
        follow_ups.append(f"¿Qué vacíos de evidencia tiene cada uno en {human_topic}?")
        follow_ups.append(f"¿Quieres comparar a {unique_candidates[0]} y {unique_candidates[1]} en seguridad o salud?")
    elif unique_candidates:
        follow_ups.append(f"¿Qué más propone {unique_candidates[0]} en {human_topic}?")
        follow_ups.append(f"¿Quieres comparar a {unique_candidates[0]} con otro candidato en {human_topic}?")
        follow_ups.append(f"¿Qué vacíos de evidencia hay en el plan de {unique_candidates[0]} sobre {human_topic}?")
    else:
        follow_ups.append(f"¿Qué otros candidatos hablan de {human_topic}?")
        follow_ups.append(f"¿Qué diferencias hay entre candidatos en {human_topic}?")

    follow_ups.append(f"¿Qué evidencia documental exacta sustenta esta respuesta sobre {human_topic}?")
    return list(dict.fromkeys(follow_ups))[:4]


def _build_structured_response(
    question: str,
    answer: str,
    sources: list[ChatSource],
    evidence_found: bool,
) -> ChatStructuredResponse:
    segments = _split_segments(answer)
    tagged_evidence = _extract_tagged_items(answer, "EVIDENCIA DOCUMENTAL")
    tagged_gaps = _extract_tagged_items(answer, "AUSENCIA DE EVIDENCIA")
    tagged_inferences = _extract_tagged_items(answer, "INFERENCIA")

    summary = ""
    for segment in segments:
        if "[" not in segment:
            summary = _clean_line(segment)
            break

    if not summary:
        if tagged_evidence:
            summary = tagged_evidence[0]
        elif evidence_found:
            summary = "Se encontraron fragmentos documentales relevantes para responder esta consulta."
        else:
            summary = "No se encontró evidencia documental suficiente en el corpus disponible."

    findings = tagged_evidence[:4]
    if not findings and evidence_found:
        findings = [
            _clean_line(segment)
            for segment in segments
            if "[ausencia de evidencia]" not in segment.lower() and "[inferencia]" not in segment.lower()
        ][:4]

    evidence_gaps = tagged_gaps[:3]
    if not evidence_gaps and not evidence_found:
        evidence_gaps = [
            "No se encontraron fragmentos relevantes en los documentos indexados para responder con precisión.",
            "El tema consultado podría no estar cubierto por los documentos disponibles en la base actual.",
        ]

    inferences = tagged_inferences[:3]
    return ChatStructuredResponse(
        summary=summary,
        findings=findings,
        evidence_gaps=evidence_gaps,
        inferences=inferences,
        follow_ups=_build_follow_ups(question, sources),
    )


def answer_question(question: str, top_k: int | None = None) -> ChatResponse:
    settings = get_settings()
    vector_store = VectorStore()
    provider = build_llm_provider(settings)
    limit = top_k or settings.rag_top_k
    comparison_aliases = _comparison_candidate_scopes(question)
    primary_alias = comparison_aliases[0] if comparison_aliases else _primary_candidate_scope(question)
    effective_question = _rewrite_question_for_retrieval(question, primary_alias)
    matched_aliases = comparison_aliases if comparison_aliases else ([primary_alias] if primary_alias else [])
    targeted_chunks: list[dict[str, object]] = []
    if matched_aliases:
        for alias in matched_aliases:
            targeted_chunks.extend(_extract_candidate_chunks(effective_question, alias, max(limit, 4)))

    retrieval_question = _expand_question_with_aliases(effective_question)
    retrieval_limit = limit * 6 if matched_aliases else limit
    chunks = vector_store.query(retrieval_question, top_k=retrieval_limit)

    if matched_aliases:
        alias_filtered = [
            chunk
            for chunk in chunks
            if any(_chunk_matches_alias(chunk.metadata, alias) for alias in matched_aliases)
        ]
        if targeted_chunks:
            chunks = [
                RetrievedChunk(text=str(item["text"]), metadata=dict(item["metadata"]), distance=0.0)
                for item in targeted_chunks
            ]
        elif alias_filtered:
            chunks = alias_filtered[: max(limit, 8)]
        else:
            if len(matched_aliases) >= 2:
                absence_answer = (
                    f"[AUSENCIA DE EVIDENCIA] No se encontraron fragmentos suficientes para comparar a "
                    f"{matched_aliases[0]['official_name']} y {matched_aliases[1]['official_name']} "
                    "en el tema consultado dentro del corpus indexado."
                )
            else:
                absence_answer = _candidate_absence_message(matched_aliases[0], question)
            return ChatResponse(
                answer=absence_answer,
                sources=[],
                provider=settings.llm_provider,
                evidence_found=False,
                structured=_build_structured_response(
                    question=question,
                    answer=absence_answer,
                    sources=[],
                    evidence_found=False,
                ),
            )

    if not chunks:
        return ChatResponse(
            answer=_NO_EVIDENCE_MSG,
            sources=[],
            provider=settings.llm_provider,
            evidence_found=False,
            structured=_build_structured_response(
                question=question,
                answer=_NO_EVIDENCE_MSG,
                sources=[],
                evidence_found=False,
            ),
        )

    context_blocks = []
    sources: list[ChatSource] = []
    if len(matched_aliases) >= 2:
        scope_prefix = _comparison_scope_prefix(matched_aliases)
    else:
        scope_prefix = _candidate_scope_prefix(primary_alias) if primary_alias else ""
    chunk_cap = max(limit, 8) if len(matched_aliases) >= 2 else max(limit, 6)
    for chunk in chunks[:chunk_cap]:
        metadata = chunk.metadata
        resolved_candidate_name, resolved_party = _resolve_source_identity(
            str(metadata.get("candidate_name", "")),
            str(metadata.get("party", "")),
        )
        context_blocks.append(
            (
                f"Candidato: {resolved_candidate_name}\n"
                f"Partido: {resolved_party or metadata.get('party', '')}\n"
                f"Eje: {metadata['axis']}\n"
                f"Titulo: {metadata['title']}\n"
                f"Fuente: {metadata['source_name']} - {metadata['source_url']}\n"
                f"Contenido: {chunk.text}"
            )
        )
        sources.append(
            ChatSource(
                candidate_name=resolved_candidate_name,
                axis=metadata["axis"],
                title=metadata["title"],
                source_name=metadata["source_name"],
                source_url=metadata["source_url"],
                excerpt=chunk.text[:240],
                page_number=int(metadata["page_number"]) if metadata.get("page_number") is not None else None,
            )
        )

    if scope_prefix:
        answer = provider.generate(
            question=effective_question,
            context=scope_prefix + "\n\n---\n\n".join(context_blocks),
        )
    else:
        answer = provider.generate(question=effective_question, context="\n\n---\n\n".join(context_blocks))

    # Si el LLM devuelve vacío, usar mensaje estándar de ausencia
    if not answer or not answer.strip():
        return ChatResponse(
            answer=_NO_EVIDENCE_MSG,
            sources=sources,
            provider=settings.llm_provider,
            evidence_found=False,
            structured=_build_structured_response(
                question=question,
                answer=_NO_EVIDENCE_MSG,
                sources=sources,
                evidence_found=False,
            ),
        )

    return ChatResponse(
        answer=answer,
        sources=sources,
        provider=settings.llm_provider,
        evidence_found=True,
        structured=_build_structured_response(
            question=question,
            answer=answer,
            sources=sources,
            evidence_found=True,
        ),
    )


def simplify_text(text: str) -> SimplifyResponse:
    settings = get_settings()
    provider = build_llm_provider(settings)
    simplified = provider.simplify(text)
    return SimplifyResponse(simplified=simplified, provider=settings.llm_provider)
