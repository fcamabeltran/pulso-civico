from __future__ import annotations

from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.ai.vector_store import VectorStore
from app.db.session import SessionLocal
from app.models import Candidate, Proposal
from app.utils.document_chunks import build_chunks_from_pdf, build_chunks_from_text


def run() -> None:
    db = SessionLocal()
    vector_store = VectorStore()
    vector_store.reset()

    proposals = list(
        db.scalars(
            select(Proposal)
            .options(joinedload(Proposal.candidate))
            .order_by(Proposal.candidate_id, Proposal.axis, Proposal.id)
        ).all()
    )

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for proposal in proposals:
        candidate: Candidate = proposal.candidate
        candidate_metadata = dict(candidate.metadata_json or {})
        local_plan_path = candidate_metadata.get("local_full_plan_path")
        page_chunks = []
        if isinstance(local_plan_path, str) and local_plan_path:
            try:
                _, page_chunks = build_chunks_from_pdf(Path(local_plan_path))
            except Exception:
                page_chunks = []

        if not page_chunks:
            page_chunks = build_chunks_from_text(proposal.content)

        for chunk_index, chunk in enumerate(page_chunks):
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
    print(f"Reindexación RAG completada: {len(ids)} chunks.")


if __name__ == "__main__":
    run()
