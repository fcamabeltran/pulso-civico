from pydantic import BaseModel


class SearchResult(BaseModel):
    candidate_id: int
    candidate_name: str
    party: str
    axis: str
    title: str
    snippet: str
    source_name: str
    source_url: str

