from __future__ import annotations

import json
from pathlib import Path

from sqlalchemy import delete

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Candidate, PromiseTracking, Proposal

LP_INDEX = Path("/app/data/downloads/lp_plans/index.json")


def clean_candidate_name(raw_name: str | None, party_name: str) -> str:
    if not raw_name:
        return party_name
    noise_tokens = {"DNI", "FIR", "FECHA", "AUT", "PLAN", "PARA", "LA", "PATRIA"}
    parts = [part for part in raw_name.split() if part.upper() not in noise_tokens]
    cleaned = " ".join(parts[:6]).strip()
    return cleaned or party_name


def run() -> None:
    Base.metadata.create_all(bind=engine)
    payload = json.loads(LP_INDEX.read_text(encoding="utf-8"))
    db = SessionLocal()

    db.execute(delete(PromiseTracking))
    db.execute(delete(Proposal))
    db.execute(delete(Candidate))
    db.commit()

    seen: set[tuple[str, str]] = set()
    imported = 0

    for item in payload:
        party = item["party_name"].strip()
        candidate_name = clean_candidate_name(item.get("candidate_name"), party)
        dedupe_key = (party.lower(), candidate_name.lower())
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        candidate = Candidate(
            name=candidate_name,
            party=party,
            region="Perú",
            office="Presidencia de la República",
            biography="Importado desde recopilación documental de planes de gobierno. La ficha detallada aún está en proceso de estructuración.",
            metadata_json={
                "imported_from": "LP Derecho / documentos vinculados al JNE",
                "source_article": item.get("source_article"),
                "full_plan_pdf_url": item.get("source_pdf_url"),
                "local_full_plan_path": item.get("local_pdf_path"),
                "summary_pdf_url": None,
                "photo_url": None,
            },
        )
        db.add(candidate)
        imported += 1

    db.commit()
    db.close()
    print(f"Importación completada: {imported} candidatos cargados.")


if __name__ == "__main__":
    run()
