from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.candidate import Candidate
from app.models.proposal import Proposal
from app.schemas.search import SearchResult


def search_content(db: Session, query: str, limit: int = 10) -> list[SearchResult]:
    stmt = (
        select(Proposal, Candidate)
        .join(Candidate, Candidate.id == Proposal.candidate_id)
        .where(
            or_(
                Proposal.title.ilike(f"%{query}%"),
                Proposal.content.ilike(f"%{query}%"),
                Proposal.axis.ilike(f"%{query}%"),
                Candidate.name.ilike(f"%{query}%"),
                Candidate.party.ilike(f"%{query}%"),
                Candidate.region.ilike(f"%{query}%"),
            )
        )
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    results: list[SearchResult] = []
    for proposal, candidate in rows:
        results.append(
            SearchResult(
                candidate_id=candidate.id,
                candidate_name=candidate.name,
                party=candidate.party,
                axis=proposal.axis,
                title=proposal.title,
                snippet=proposal.content[:280],
                source_name=proposal.source_name,
                source_url=proposal.source_url,
            )
        )
    return results

