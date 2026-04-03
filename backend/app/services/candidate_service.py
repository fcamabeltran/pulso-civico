from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.candidate import Candidate
from app.services.candidate_enrichment_service import enrich_candidate


def list_candidates(db: Session) -> list[Candidate]:
    stmt = select(Candidate).options(joinedload(Candidate.proposals)).order_by(Candidate.region, Candidate.name)
    candidates = list(db.scalars(stmt).unique().all())
    return [enrich_candidate(candidate) for candidate in candidates]


def get_candidate(db: Session, candidate_id: int) -> Candidate | None:
    stmt = (
        select(Candidate)
        .where(Candidate.id == candidate_id)
        .options(joinedload(Candidate.proposals), joinedload(Candidate.promises))
    )
    candidate = db.scalars(stmt).unique().one_or_none()
    if not candidate:
        return None
    return enrich_candidate(candidate)
