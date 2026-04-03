from pydantic import BaseModel, ConfigDict

from app.models.promise import PromiseStatus


class PromiseBase(BaseModel):
    candidate_id: int
    title: str
    description: str
    status: PromiseStatus
    source_name: str
    source_url: str
    evidence_note: str | None = None


class PromiseCreate(PromiseBase):
    pass


class PromiseRead(PromiseBase):
    model_config = ConfigDict(from_attributes=True)

    id: int

