from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from sqlalchemy import delete

from app.ai.vector_store import VectorStore
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Candidate, PromiseTracking, Proposal
from app.utils.document_chunks import build_chunks_from_pdf

LP_ROOT = Path("/app/data/downloads/lp_plans")
LP_INDEX = LP_ROOT / "index.json"
AUDIT_PATH = LP_ROOT / "corpus_status.json"


@dataclass
class PlanAudit:
    party_name: str
    candidate_name: str
    pdf_path: str
    status: str
    text_length: int
    chunk_count: int
    notes: str | None = None

def clean_candidate_name(raw_name: str | None, party_name: str) -> str:
    if not raw_name:
        return party_name
    noise_tokens = {"DNI", "FIR", "FECHA", "AUT", "PLAN", "PARA", "LA", "PATRIA"}
    parts = [part for part in raw_name.split() if part.upper() not in noise_tokens]
    cleaned = " ".join(parts[:6]).strip()
    return cleaned or party_name


def resolve_pdf_path(item: dict) -> Path:
    relative_path = item.get("relative_pdf_path")
    if relative_path:
        return Path("/app") / relative_path
    return Path(item["local_pdf_path"])

def write_audit_report(entries: list[PlanAudit], indexed_chunk_count: int) -> None:
    payload = {
        "summary": {
            "total_plans": len(entries),
            "ready_plans": sum(1 for entry in entries if entry.status == "ready"),
            "missing_pdfs": sum(1 for entry in entries if entry.status == "missing_pdf"),
            "empty_text": sum(1 for entry in entries if entry.status == "empty_text"),
            "extract_errors": sum(1 for entry in entries if entry.status == "extract_error"),
            "indexed_chunks": indexed_chunk_count,
        },
        "plans": [asdict(entry) for entry in entries],
    }
    AUDIT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def run() -> None:
    Base.metadata.create_all(bind=engine)
    payload = json.loads(LP_INDEX.read_text(encoding="utf-8"))
    db = SessionLocal()
    vector_store = VectorStore()
    vector_store.reset()

    db.execute(delete(PromiseTracking))
    db.execute(delete(Proposal))
    db.execute(delete(Candidate))
    db.commit()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []
    audit_entries: list[PlanAudit] = []
    seen: set[tuple[str, str]] = set()

    for item in payload:
        party_name = item["party_name"].strip()
        candidate_name = clean_candidate_name(item.get("candidate_name"), party_name)
        dedupe_key = (party_name.lower(), candidate_name.lower())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        pdf_path = resolve_pdf_path(item)
        if not pdf_path.exists():
            audit_entries.append(
                PlanAudit(
                    party_name=party_name,
                    candidate_name=candidate_name,
                    pdf_path=str(pdf_path),
                    status="missing_pdf",
                    text_length=0,
                    chunk_count=0,
                    notes="No se encontro el PDF local referenciado por el indice.",
                )
            )
            continue

        try:
            text, proposal_chunks = build_chunks_from_pdf(pdf_path)
        except Exception as exc:
            audit_entries.append(
                PlanAudit(
                    party_name=party_name,
                    candidate_name=candidate_name,
                    pdf_path=str(pdf_path),
                    status="extract_error",
                    text_length=0,
                    chunk_count=0,
                    notes=str(exc),
                )
            )
            continue

        if not text:
            audit_entries.append(
                PlanAudit(
                    party_name=party_name,
                    candidate_name=candidate_name,
                    pdf_path=str(pdf_path),
                    status="empty_text",
                    text_length=0,
                    chunk_count=0,
                    notes="El PDF existe, pero no se pudo extraer texto util.",
                )
            )
            continue

        candidate = Candidate(
            name=candidate_name,
            party=party_name,
            region="Perú",
            office="Presidencia de la República",
            biography="Importado desde el corpus local de planes de gobierno LP Derecho/JNE.",
            metadata_json={
                "imported_from": "LP Derecho / documentos vinculados al JNE",
                "source_article": item.get("source_article"),
                "full_plan_pdf_url": item.get("source_pdf_url"),
                "local_full_plan_path": str(pdf_path),
                "relative_full_plan_path": item.get("relative_pdf_path"),
                "filename": item.get("filename"),
            },
        )
        db.add(candidate)
        db.flush()

        proposal = Proposal(
            candidate_id=candidate.id,
            axis="Plan de gobierno",
            title=f"Plan de gobierno completo - {party_name}",
            content=text,
            source_name="LP Derecho",
            source_url=item.get("source_pdf_url") or item.get("source_article") or "",
        )
        db.add(proposal)
        db.flush()

        for chunk_index, chunk in enumerate(proposal_chunks):
            ids.append(f"proposal-{proposal.id}-{chunk_index}")
            documents.append(chunk.text)
            metadatas.append(
                {
                    "proposal_id": proposal.id,
                    "candidate_id": candidate.id,
                    "candidate_name": candidate.name,
                    "party": candidate.party,
                    "axis": proposal.axis,
                    "title": proposal.title,
                    "source_name": proposal.source_name,
                    "source_url": proposal.source_url,
                    "page_number": chunk.page_number,
                }
            )

        audit_entries.append(
            PlanAudit(
                party_name=party_name,
                candidate_name=candidate_name,
                pdf_path=str(pdf_path),
                status="ready",
                text_length=len(text),
                chunk_count=len(proposal_chunks),
            )
        )

    db.commit()

    if ids:
        batch_size = 5000
        for start in range(0, len(ids), batch_size):
            end = start + batch_size
            vector_store.add_documents(
                ids=ids[start:end],
                documents=documents[start:end],
                metadatas=metadatas[start:end],
            )

    db.close()
    write_audit_report(audit_entries, indexed_chunk_count=len(ids))
    print(
        "Importacion LP -> RAG completada: "
        f"{sum(1 for entry in audit_entries if entry.status == 'ready')} planes listos, "
        f"{len(ids)} chunks indexados. "
        f"Auditoria: {AUDIT_PATH}"
    )


if __name__ == "__main__":
    run()
