from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.formula import PresidentialFormula
from app.services.formula_service import get_dni_index, get_formulas

router = APIRouter()


@router.get("/formulas", response_model=list[PresidentialFormula])
async def list_formulas(db: Session = Depends(get_db)) -> list[PresidentialFormula]:
    try:
        formulas = await get_formulas()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al consultar JNE: {exc}") from exc

    dni_to_id = get_dni_index(db)

    for formula in formulas:
        for cand in formula.candidatos:
            cand.candidate_id = dni_to_id.get(cand.dni.strip())

    return formulas
