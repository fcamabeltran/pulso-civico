from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import httpx
from pypdf import PdfReader
from slugify import slugify

LP_URL = "https://lpderecho.pe/elecciones-2026-lea-aqui-planes-gobierno-presentados-partidos-postulantes/"
OUTPUT_DIR = Path("/app/data/downloads/lp_plans")


def extract_party_name(text: str) -> str:
    patterns = [
        r"plan de gobierno de (.+?)\.$",
        r"plan de gobierno del (.+?)\.$",
    ]
    clean_text = text.strip()
    for pattern in patterns:
        match = re.search(pattern, clean_text, flags=re.IGNORECASE)
        if match:
            return match.group(1).strip()
    return clean_text


def infer_candidate_name(pdf_path: Path) -> str | None:
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return None

    text = "\n".join((page.extract_text() or "") for page in reader.pages[:3])
    patterns = [
        r"candidato(?:a)?\s+(?:a la presidencia|presidencial)?\s*:\s*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑñ\s]+)",
        r"personero legal titular\s*:\s*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑñ\s]+)",
        r"firmado digitalmente por:\s*([A-ZÁÉÍÓÚÑ][A-Za-zÁÉÍÓÚÑñ\s]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return " ".join(match.group(1).split())
    return None


def build_relative_path(path: Path) -> str:
    try:
        return str(path.relative_to(Path("/app")))
    except ValueError:
        return str(path)


def run() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with httpx.Client(
        timeout=60,
        follow_redirects=True,
        headers={"User-Agent": "Pulso-Civico-Bot/0.1 (+https://localhost)"},
    ) as client:
        response = client.get(LP_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "lxml")

        downloads: list[dict] = []
        article_links = soup.select("li a[href*='img.lpderecho.pe'][href$='.pdf']")

        for link in article_links:
            href = link.get("href")
            if not href:
                continue

            line_text = link.parent.get_text(" ", strip=True)
            party_name = extract_party_name(line_text)
            party_slug = slugify(party_name)
            party_dir = OUTPUT_DIR / party_slug
            party_dir.mkdir(parents=True, exist_ok=True)

            filename = Path(urlparse(href).path).name
            pdf_path = party_dir / filename

            if not pdf_path.exists():
                pdf_response = client.get(href)
                pdf_response.raise_for_status()
                pdf_path.write_bytes(pdf_response.content)

            candidate_name = infer_candidate_name(pdf_path)
            metadata = {
                "party_name": party_name,
                "candidate_name": candidate_name,
                "party_slug": party_slug,
                "source_article": LP_URL,
                "source_pdf_url": href,
                "local_pdf_path": str(pdf_path),
                "relative_pdf_path": build_relative_path(pdf_path),
                "filename": filename,
            }

            metadata_path = party_dir / "metadata.json"
            metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
            downloads.append(metadata)

        summary_path = OUTPUT_DIR / "index.json"
        summary_path.write_text(json.dumps(downloads, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Descarga completada: {len(downloads)} planes guardados en {OUTPUT_DIR}")


if __name__ == "__main__":
    run()
