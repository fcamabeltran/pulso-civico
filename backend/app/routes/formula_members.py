from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.formula_member import (
    FormulaMemberDetail,
    FormulaMemberRead,
    FormulaMembersResponse,
    FormulaProfileRead,
)
from app.services.formula_member_service import (
    get_formula_members,
    get_member_by_name,
    get_member_detail,
    list_formula_profiles,
)

router = APIRouter()


@router.get("/formula-profiles", response_model=list[FormulaProfileRead])
def list_formula_profiles_endpoint(db: Session = Depends(get_db)) -> list[FormulaProfileRead]:
    return list_formula_profiles(db)


@router.get("/formula-members/by-name/{name}", response_model=FormulaMemberDetail)
def get_member_by_name_endpoint(name: str, db: Session = Depends(get_db)) -> FormulaMemberDetail:
    member = get_member_by_name(db, name)
    if not member:
        raise HTTPException(status_code=404, detail="No se encontró un miembro con ese nombre.")
    return member


@router.get("/formula-members/{member_id}", response_model=FormulaMemberDetail)
def get_member_detail_endpoint(member_id: int, db: Session = Depends(get_db)) -> FormulaMemberDetail:
    member = get_member_detail(db, member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Miembro no encontrado.")
    return member


@router.get("/formulas/{organization_id}/members", response_model=FormulaMembersResponse)
def formula_members(organization_id: int, db: Session = Depends(get_db)) -> FormulaMembersResponse:
    formula = get_formula_members(db, organization_id)
    if not formula:
        raise HTTPException(status_code=404, detail="No se encontró información de hoja de vida para esta fórmula.")
    return formula
