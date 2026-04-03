from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.compare import CompareResponse
from app.services.compare_service import compare_candidates

router = APIRouter()


@router.get("/compare", response_model=CompareResponse)
def compare(
    c1: int = Query(..., description="ID del primer candidato"),
    c2: int = Query(..., description="ID del segundo candidato"),
    db: Session = Depends(get_db),
) -> CompareResponse:
    return compare_candidates(db, c1, c2)

