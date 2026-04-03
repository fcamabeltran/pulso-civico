import httpx

from app.schemas.formula import FormulaCandidate, PresidentialFormula

JNE_URL = "https://web.jne.gob.pe/serviciovotoinformado/api/votoinf/listarCanditatos"
FOTO_BASE = "https://mpesije.jne.gob.pe/apidocs/"
LOGO_BASE = "https://votoinformado.jne.gob.pe/LogoOp/"
ESTADOS_EXCLUIDOS = {"IMPROCEDENTE", "RENUNCIA", "FALLECIDO"}


async def get_formulas() -> list[PresidentialFormula]:
    payload = {"idProcesoElectoral": 124, "strUbiDepartamento": "", "idTipoEleccion": 1}

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(JNE_URL, json=payload)
        resp.raise_for_status()
        data = resp.json()

    raw = data if isinstance(data, list) else data.get("data", [])
    raw = [c for c in raw if c.get("strEstadoCandidato") not in ESTADOS_EXCLUIDOS]

    partidos: dict[int, dict] = {}
    for c in raw:
        pid = c["idOrganizacionPolitica"]
        if pid not in partidos:
            partidos[pid] = {
                "id": pid,
                "nombre_partido": c["strOrganizacionPolitica"],
                "logo_url": f"{LOGO_BASE}{pid}.jpg",
                "candidatos": [],
            }
        nombre = f"{c['strNombres']} {c['strApellidoPaterno']} {c['strApellidoMaterno']}"
        partidos[pid]["candidatos"].append(
            FormulaCandidate(
                id_cargo=c["idCargo"],
                cargo=c["strCargo"],
                nombre=nombre.strip(),
                foto_url=f"{FOTO_BASE}{c['strNombre']}",
                dni=c["strDocumentoIdentidad"],
                posicion=c["intPosicion"],
            )
        )

    result: list[PresidentialFormula] = []
    for p in partidos.values():
        p["candidatos"].sort(key=lambda x: x.posicion)
        result.append(PresidentialFormula(**p))

    return sorted(result, key=lambda x: x.nombre_partido)
