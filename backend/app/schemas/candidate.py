from pydantic import BaseModel, ConfigDict, Field

from app.schemas.promise import PromiseRead
from app.schemas.proposal import ProposalRead


class CandidateBase(BaseModel):
    name: str
    party: str
    region: str
    office: str | None = None
    biography: str | None = None
    metadata: dict | None = Field(default=None, validation_alias="metadata_json", serialization_alias="metadata")


class CandidateCreate(CandidateBase):
    pass


class CandidateRead(CandidateBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class CandidateDetail(CandidateRead):
    proposals: list[ProposalRead] = Field(default_factory=list)
    promises: list[PromiseRead] = Field(default_factory=list)
