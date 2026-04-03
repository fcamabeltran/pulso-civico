from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=5, max_length=800)
    top_k: int | None = Field(default=None, ge=1, le=8)


class ChatSource(BaseModel):
    candidate_name: str
    axis: str
    title: str
    source_name: str
    source_url: str
    excerpt: str
    page_number: int | None = None


class ChatStructuredResponse(BaseModel):
    summary: str
    findings: list[str] = Field(default_factory=list)
    evidence_gaps: list[str] = Field(default_factory=list)
    inferences: list[str] = Field(default_factory=list)
    follow_ups: list[str] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    provider: str
    evidence_found: bool = True
    structured: ChatStructuredResponse | None = None


class SimplifyRequest(BaseModel):
    text: str = Field(..., min_length=10, max_length=4000)


class SimplifyResponse(BaseModel):
    simplified: str
    provider: str
