from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.candidate import CandidateDetail, CandidateRead
from app.services.candidate_service import get_candidate, list_candidates

router = APIRouter()


@router.get("/candidates", response_model=list[CandidateRead])
def get_candidates(db: Session = Depends(get_db)) -> list[CandidateRead]:
    return list_candidates(db)


@router.get("/candidate/{candidate_id}", response_model=CandidateDetail)
def get_candidate_detail(candidate_id: int, db: Session = Depends(get_db)) -> CandidateDetail:
    candidate = get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidato no encontrado.")
    return candidate

