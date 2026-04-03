from pydantic import BaseModel

from app.schemas.candidate import CandidateRead
from app.schemas.proposal import ProposalRead


class CompareInsights(BaseModel):
    differences: str
    coincidences: str
    detail: str
    evidence_gaps: str


class CompareResponse(BaseModel):
    left_candidate: CandidateRead
    right_candidate: CandidateRead
    left_proposals: list[ProposalRead]
    right_proposals: list[ProposalRead]
    insights: CompareInsights | None = None
