from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import httpx
from pypdf import PdfReader

from app.core.config import get_settings


@dataclass
class RemoteDocument:
    source_url: str
    source_name: str
    title: str
    text: str
    content_type: str
    local_path: str | None = None
    metadata: dict | None = None


@dataclass
class PlanListing:
    organization_name: str
    election_process: str
    election_type: str
    department: str
    province: str
    jurisdiction: str
    jee: str
    expediente: str
    plan_url: str | None
    resolution_url: str | None


@dataclass
class CandidateProfile:
    source_url: str
    full_name: str
    office: str | None
    organization: str | None
    region: str | None
    raw_text: str


class JNEScraper:
    def __init__(self) -> None:
        settings = get_settings()
        self.timeout = settings.scrape_timeout_seconds
        self.user_agent = settings.scrape_user_agent
        self.raw_dir = Path(settings.scrape_raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.client = httpx.Client(
            timeout=self.timeout,
            follow_redirects=True,
            headers={"User-Agent": self.user_agent},
        )

    def close(self) -> None:
        self.client.close()

    def fetch_html(self, url: str) -> BeautifulSoup:
        response = self.client.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, "lxml")

    def scrape_plan_listings(self, url: str) -> list[PlanListing]:
        soup = self.fetch_html(url)
        process_label = self._find_text_near_label(soup, "Proceso Electoral")
        organization_name = self._extract_heading(soup, fallback="Organizacion politica")

        rows = []
        table_rows = soup.select("table tr")
        if not table_rows:
            table_rows = soup.find_all("tr")

        for row in table_rows:
            cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
            if len(cells) < 6 or "Departamento" in cells[0]:
                continue

            plan_url = None
            resolution_url = None
            links = row.find_all("a", href=True)
            if links:
                plan_url = urljoin(url, links[0]["href"])
            if len(links) > 1:
                resolution_url = urljoin(url, links[1]["href"])

            data = cells[-7:] if len(cells) >= 7 else cells
            department = data[0] if len(data) > 0 else ""
            province = data[1] if len(data) > 1 else ""
            election_type = data[2] if len(data) > 2 else ""
            jee = data[3] if len(data) > 3 else ""
            expediente = data[-1] if data else ""

            rows.append(
                PlanListing(
                    organization_name=organization_name,
                    election_process=process_label or "",
                    election_type=election_type,
                    department=department,
                    province=province,
                    jurisdiction=election_type,
                    jee=jee,
                    expediente=expediente,
                    plan_url=plan_url,
                    resolution_url=resolution_url,
                )
            )

        return rows

    def scrape_candidate_profile(self, url: str) -> CandidateProfile:
        soup = self.fetch_html(url)
        raw_text = soup.get_text("\n", strip=True)
        full_name = self._find_text_near_label(soup, "Nombres") or self._extract_heading(soup, fallback="Candidato")
        last_name = self._find_text_near_label(soup, "Apellido Paterno")
        second_last_name = self._find_text_near_label(soup, "Apellido Materno")
        full_name = " ".join(part for part in [full_name, last_name, second_last_name] if part).strip() or full_name

        return CandidateProfile(
            source_url=url,
            full_name=full_name,
            office=self._find_text_near_label(soup, "Cargo al que Postula"),
            organization=self._find_text_near_label(soup, "Organización Política"),
            region=self._find_text_near_label(soup, "Región"),
            raw_text=raw_text,
        )

    def fetch_document(self, url: str, source_name: str, title: str, file_stem: str) -> RemoteDocument:
        response = self.client.get(url)
        response.raise_for_status()
        content_type = response.headers.get("content-type", "application/octet-stream")
        suffix = ".pdf" if "pdf" in content_type or url.lower().endswith(".pdf") else ".bin"
        local_path = self.raw_dir / f"{file_stem}{suffix}"
        local_path.write_bytes(response.content)

        if suffix == ".pdf":
            text = self._extract_pdf_text(local_path)
        else:
            text = response.text

        return RemoteDocument(
            source_url=url,
            source_name=source_name,
            title=title,
            text=text,
            content_type=content_type,
            local_path=str(local_path),
        )

    def extract_local_pdf(self, path: Path, source_name: str, title: str) -> RemoteDocument:
        return RemoteDocument(
            source_url=str(path),
            source_name=source_name,
            title=title,
            text=self._extract_pdf_text(path),
            content_type="application/pdf",
            local_path=str(path),
        )

    def _extract_pdf_text(self, path: Path) -> str:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "").strip() for page in reader.pages).strip()

    def _find_text_near_label(self, soup: BeautifulSoup, label: str) -> str | None:
        node = soup.find(string=lambda text: isinstance(text, str) and label.lower() in text.lower())
        if not node:
            return None
        parent = node.parent
        if parent:
            text = parent.get_text(" ", strip=True)
            if ":" in text:
                return text.split(":", 1)[1].strip() or None
        sibling = node.find_next(string=True)
        return sibling.strip() if sibling else None

    def _extract_heading(self, soup: BeautifulSoup, fallback: str) -> str:
        for tag in ("h1", "h2", "h3", "title"):
            element = soup.find(tag)
            if element and element.get_text(strip=True):
                return element.get_text(strip=True)
        return fallback


def listing_to_dict(listing: PlanListing) -> dict:
    return asdict(listing)


def profile_to_dict(profile: CandidateProfile) -> dict:
    return asdict(profile)


def document_to_dict(document: RemoteDocument) -> dict:
    return asdict(document)

