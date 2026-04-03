from pydantic import BaseModel, ConfigDict


class ProposalBase(BaseModel):
    candidate_id: int
    axis: str
    title: str
    content: str
    source_name: str
    source_url: str


class ProposalCreate(ProposalBase):
    pass


class ProposalRead(ProposalBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

