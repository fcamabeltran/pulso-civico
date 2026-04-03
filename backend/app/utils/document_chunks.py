from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass
class DocumentChunk:
    text: str
    page_number: int | None = None


def normalize_text(text: str) -> str:
    text = text.replace("\x00", " ")
    text = re.sub(r"\r\n?", "\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, chunk_size: int = 450, overlap: int = 75) -> list[str]:
    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(text[start:end])
        if end == len(text):
            break
        start = end - overlap
    return chunks


def extract_pdf_pages(path: Path) -> list[str]:
    reader = PdfReader(str(path))
    pages: list[str] = []
    for page in reader.pages:
        pages.append(normalize_text((page.extract_text() or "").strip()))
    return pages


def build_chunks_from_pdf(path: Path, chunk_size: int = 450, overlap: int = 75) -> tuple[str, list[DocumentChunk]]:
    pages = extract_pdf_pages(path)
    full_text = "\n\n".join(page for page in pages if page).strip()
    chunks: list[DocumentChunk] = []
    for page_index, page_text in enumerate(pages, start=1):
        if not page_text:
            continue
        for chunk in chunk_text(page_text, chunk_size=chunk_size, overlap=overlap):
            chunks.append(DocumentChunk(text=chunk, page_number=page_index))
    return full_text, chunks


def build_chunks_from_text(text: str, chunk_size: int = 450, overlap: int = 75) -> list[DocumentChunk]:
    normalized = normalize_text(text)
    return [DocumentChunk(text=chunk, page_number=None) for chunk in chunk_text(normalized, chunk_size, overlap)]
