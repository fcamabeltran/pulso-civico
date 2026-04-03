from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.search import SearchResult
from app.services.search_service import search_content

router = APIRouter()


@router.get("/search", response_model=list[SearchResult])
def search(
    q: str = Query(..., min_length=2, description="Texto a buscar"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
) -> list[SearchResult]:
    return search_content(db, q, limit=limit)

