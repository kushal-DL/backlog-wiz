"""
ingest.py — Input ingestion. Handles .txt, .md, .pdf → normalised UTF-8 string.
PDF: text-extractable pages only (pypdf). Scanned PDFs emit a warning.
Inputs over MAX_INPUT_CHARS are truncated with a logged warning.
"""
import re
import sys
from pathlib import Path

SUPPORTED = {".txt", ".md", ".pdf"}
MAX_INPUT_CHARS = 12_000  # ~3 000 tokens; leaves room in a 4k-context call


def load_input(path: str) -> str:
    """Load and return clean text from a .txt, .md, or .pdf file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    suffix = p.suffix.lower()
    if suffix not in SUPPORTED:
        raise ValueError(f"Unsupported file type '{suffix}'. Accepted: {', '.join(sorted(SUPPORTED))}")
    text = _pdf(p) if suffix == ".pdf" else _text(p)
    return _guard(text, path)


def _text(p: Path) -> str:
    try:
        raw = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raw = p.read_text(encoding="latin-1")
    return _norm(raw)


def _pdf(p: Path) -> str:
    from pypdf import PdfReader
    pages = [page.extract_text() or "" for page in PdfReader(str(p)).pages]
    text = _norm("\n".join(pages))
    if not text.strip():
        print(f"Warning: no extractable text in '{p}'. File may be scanned.", file=sys.stderr)
    return text


def _norm(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def _guard(text: str, source: str) -> str:
    if len(text) > MAX_INPUT_CHARS:
        print(f"Warning: '{source}' truncated to {MAX_INPUT_CHARS} chars.", file=sys.stderr)
        return text[:MAX_INPUT_CHARS]
    return text
