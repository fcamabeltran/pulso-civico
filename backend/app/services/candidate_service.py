from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.candidate import Candidate
from app.services.candidate_enrichment_service import enrich_candidate

_LOCAL_KEYS = {"local_summary_path", "local_full_plan_path", "local_hoja_vida_path"}


def _strip_local_paths(candidate: Candidate) -> Candidate:
    """Remove server-side file paths from metadata before sending to frontend."""
    if candidate.metadata_json:
        candidate.metadata_json = {
            k: v for k, v in candidate.metadata_json.items()
            if k not in _LOCAL_KEYS and not k.startswith("local_")
        }
    return candidate


def list_candidates(db: Session) -> list[Candidate]:
    # No joinedload(proposals) — list view doesn't need them (saves ~2644 rows)
    stmt = select(Candidate).order_by(Candidate.region, Candidate.name)
    candidates = list(db.scalars(stmt).all())
    return [_strip_local_paths(enrich_candidate(c)) for c in candidates]


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
