from fastapi import APIRouter, HTTPException

from app.schemas.formula import PresidentialFormula
from app.services.formula_service import get_formulas

router = APIRouter()


@router.get("/formulas", response_model=list[PresidentialFormula])
async def list_formulas() -> list[PresidentialFormula]:
    try:
        return await get_formulas()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Error al consultar JNE: {exc}") from exc
