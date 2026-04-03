from __future__ import annotations

import json
from pathlib import Path
from slugify import slugify

from app.scrapers.jne import (
    JNEScraper,
    document_to_dict,
    listing_to_dict,
    profile_to_dict,
)

MANIFEST_PATH = Path("/app/data/source_manifest.json")
OUTPUT_PATH = Path("/app/data/raw_sources.json")


def run() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    scraper = JNEScraper()

    payload: dict[str, list[dict]] = {
        "plan_listings": [],
        "candidate_profiles": [],
        "documents": [],
    }

    try:
        for source in manifest.get("plan_pages", []):
            listings = scraper.scrape_plan_listings(source["url"])
            payload["plan_listings"].extend(listing_to_dict(listing) for listing in listings)

            if source.get("download_plan_documents"):
                for index, listing in enumerate(listings, start=1):
                    if not listing.plan_url:
                        continue
                    file_stem = slugify(f"{listing.organization_name}-{listing.department}-{listing.province}-{index}")
                    document = scraper.fetch_document(
                        url=listing.plan_url,
                        source_name="JNE",
                        title=f"Plan de gobierno - {listing.organization_name}",
                        file_stem=file_stem,
                    )
                    document.metadata = {
                        "expediente": listing.expediente,
                        "organization_name": listing.organization_name,
                        "department": listing.department,
                        "province": listing.province,
                    }
                    payload["documents"].append(document_to_dict(document))

        for source in manifest.get("candidate_pages", []):
            profile = scraper.scrape_candidate_profile(source["url"])
            payload["candidate_profiles"].append(profile_to_dict(profile))

        for source in manifest.get("uploaded_documents", []):
            path = Path(source["path"])
            if not path.exists():
                print(f"Saltando documento local inexistente: {path}")
                continue

            document = scraper.extract_local_pdf(
                path=path,
                source_name=source.get("source_name", "Documento cargado"),
                title=source.get("title", path.stem),
            )
            payload["documents"].append(document_to_dict(document))
    finally:
        scraper.close()

    OUTPUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        "Scraping completado: "
        f"{len(payload['plan_listings'])} listados, "
        f"{len(payload['candidate_profiles'])} perfiles, "
        f"{len(payload['documents'])} documentos."
    )


if __name__ == "__main__":
    run()
