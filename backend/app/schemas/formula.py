from pydantic import BaseModel


class FormulaCandidate(BaseModel):
    id_cargo: int
    cargo: str
    nombre: str
    foto_url: str
    dni: str
    posicion: int
    candidate_id: int | None = None


class PresidentialFormula(BaseModel):
    id: int
    nombre_partido: str
    logo_url: str
    candidatos: list[FormulaCandidate]
