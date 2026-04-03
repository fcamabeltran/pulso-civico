import json
from pathlib import Path

from sqlalchemy import delete

from app.ai.vector_store import VectorStore
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Candidate, PromiseTracking, Proposal
from app.models.promise import PromiseStatus
from app.utils.document_chunks import build_chunks_from_text

DATA_FILE = Path("/app/data/seed_candidates.json")


def run() -> None:
    Base.metadata.create_all(bind=engine)
    payload = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    db = SessionLocal()
    vector_store = VectorStore()

    db.execute(delete(PromiseTracking))
    db.execute(delete(Proposal))
    db.execute(delete(Candidate))
    db.commit()

    ids: list[str] = []
    documents: list[str] = []
    metadatas: list[dict] = []

    for candidate_data in payload["candidates"]:
        candidate = Candidate(
            name=candidate_data["name"],
            party=candidate_data["party"],
            region=candidate_data["region"],
            office=candidate_data.get("office"),
            biography=candidate_data.get("biography"),
            metadata_json=candidate_data.get("metadata"),
        )
        db.add(candidate)
        db.flush()

        for proposal_data in candidate_data.get("proposals", []):
            proposal = Proposal(candidate_id=candidate.id, **proposal_data)
            db.add(proposal)
            db.flush()

            for chunk_index, chunk in enumerate(build_chunks_from_text(proposal.content)):
                ids.append(f"proposal-{proposal.id}-{chunk_index}")
                documents.append(chunk.text)
                metadatas.append(
                    {
                        "proposal_id": proposal.id,
                        "candidate_id": candidate.id,
                        "candidate_name": candidate.name,
                        "axis": proposal.axis,
                        "title": proposal.title,
                        "source_name": proposal.source_name,
                        "source_url": proposal.source_url,
                        "page_number": chunk.page_number,
                    }
                )

        for promise_data in candidate_data.get("promises", []):
            db.add(
                PromiseTracking(
                    candidate_id=candidate.id,
                    title=promise_data["title"],
                    description=promise_data["description"],
                    status=PromiseStatus(promise_data["status"]),
                    source_name=promise_data["source_name"],
                    source_url=promise_data["source_url"],
                    evidence_note=promise_data.get("evidence_note"),
                )
            )

    db.commit()
    if ids:
        vector_store.add_documents(ids=ids, documents=documents, metadatas=metadatas)
    db.close()
    print(f"Ingesta completada: {len(ids)} chunks indexados.")


if __name__ == "__main__":
    run()
