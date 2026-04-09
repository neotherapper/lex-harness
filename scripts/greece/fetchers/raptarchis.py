# scripts/greece/fetchers/raptarchis.py
#
# SOURCE: archive.raptarchis.gov.gr — Διαρκής Κώδικας Νομοθεσίας – Ραπτάρχης
# Operator: Αυτοτελές Τμήμα Διοικητικών Κωδικοποιήσεων, Γεν. Γραμ. Νομικών και
#           Κοινοβουλευτικών Θεμάτων, Προεδρία της Κυβέρνησης (gov.gr)
# Access: Public — PDFs served directly from WordPress/gov.gr infrastructure.
# No auth, no subscription required.
#
# CONFIRMED PDF URLs (verified 2026-04-09):
#   AK (Αστικός Κώδικας, modern demotic section starts p.219):
#     https://archive.raptarchis.gov.gr/wp-content/uploads/2020/11/THEMA812.pdf
#   KPolD (Κώδικας Πολιτικής Δικονομίας, Νέος, modern section starts ~p.230):
#     https://archive.raptarchis.gov.gr/wp-content/uploads/2020/11/THEMA11.12.pdf
#
# ARTICLE EXTRACTION:
#   Modern text uses "Άρθρο NNN." header (full word "Άρθρο", not "Άρθρ.").
#   Old καθαρεύουσα text uses "Άρθρ.NNN.-" — we skip it by searching for full pattern.
#   Text runs until the next "Άρθρο" heading (or end of document).
#
# HELLENICPARLIAMENT PDF for Constitution:
#   https://www.hellenicparliament.gr/UserFiles/f3c70a23-7696-49db-9148-f24dce6a27c8/
#     FEK%20211-A-24-12-2019%20NEO%20SYNTAGMA.pdf
#   Article format: "Άρθρο NNN\n" (no period after number).
import hashlib
import os
import re
import time
from pathlib import Path

import httpx

from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}

# Local cache directory for downloaded PDFs. Avoids re-downloading 3-4MB per verify() call.
_CACHE_DIR = Path(os.environ.get("LEX_PDF_CACHE", "/tmp/lex-harness-pdf-cache"))


def _cache_path(pdf_url: str) -> Path:
    slug = re.sub(r"[^a-zA-Z0-9._-]", "_", pdf_url.split("/")[-1])
    return _CACHE_DIR / slug


def _download_pdf(pdf_url: str, force: bool = False) -> bytes:
    """Download a PDF, using a local cache to avoid repeated fetches."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = _cache_path(pdf_url)
    if not force and cache_file.exists() and cache_file.stat().st_size > 10_000:
        return cache_file.read_bytes()
    resp = httpx.get(pdf_url, headers=_HEADERS, timeout=60, follow_redirects=True)
    resp.raise_for_status()
    if not resp.headers.get("content-type", "").startswith("application/pdf"):
        raise ValueError(f"Expected PDF from {pdf_url}, got {resp.headers.get('content-type')}")
    cache_file.write_bytes(resp.content)
    return resp.content


def _extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract full text from a PDF using PyMuPDF."""
    try:
        import fitz
    except ImportError:
        raise RuntimeError("pymupdf not installed — run: uv sync --directory scripts")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    return text


def _extract_article(full_text: str, article_num: int) -> str:
    """Extract verbatim text for a single article from concatenated PDF text.

    Handles two formats:
      - "Άρθρο 173.\\n  Title.\\n  Text..." (Raptarchis AK/KPolD PDFs)
      - "Άρθρο 25\\n**1. Text..."             (Hellenic Parliament Syntagma PDF)

    Returns the raw extracted text (not cleaned), including the article header.
    Raises ValueError if the article is not found.
    """
    # Pattern 1: Raptarchis format — "Άρθρο NNN." (with period)
    pat1 = re.compile(rf"Άρθρο\s+{article_num}\.\s", re.UNICODE)
    # Pattern 2: Hellenic Parliament format — "Άρθρο NNN\n" (no period, followed by newline)
    pat2 = re.compile(rf"Άρθρο\s+{article_num}\s*\n", re.UNICODE)

    m = pat1.search(full_text) or pat2.search(full_text)
    if not m:
        raise ValueError(
            f"Article {article_num} not found in PDF text "
            f"(searched for 'Άρθρο {article_num}.' and 'Άρθρο {article_num}\\n')"
        )

    start = m.start()
    # Find the next article heading after this one
    next_article = re.compile(r"Άρθρο\s+\d+[\.\s]", re.UNICODE)
    next_m = next_article.search(full_text, start + 10)
    end = next_m.start() if next_m else len(full_text)

    return full_text[start:end].strip()


def _extract_article_range(full_text: str, start_num: int, end_num: int) -> str:
    """Extract a contiguous range of articles (e.g. AK_440_452 → 440–452)."""
    parts = []
    for num in range(start_num, end_num + 1):
        try:
            parts.append(_extract_article(full_text, num))
        except ValueError:
            pass  # Some articles in range may be absent (renumbered, repealed)
    if not parts:
        raise ValueError(
            f"No articles found in range {start_num}–{end_num}"
        )
    return "\n\n".join(parts)


class RaptarchisFetcher(BaseFetcher):
    """Fetches verbatim statute text from official gov.gr PDFs.

    Entry fields:
      raptarchis_pdf_url  — direct URL to the PDF file (required)
      article_id          — used to derive article number(s) if not overridden
      raptarchis_article_start  — override: first article number to extract
      raptarchis_article_end    — override: last article number (for ranges; default = start)

    Article number is derived from article_id by default:
      "AK_173"      → 173
      "KPolD_338"   → 338
      "Syntagma_25" → 25
      "AK_440_452"  → range 440–452
    """
    source_id = "raptarchis"

    def fetch(self, entry: dict) -> str:
        pdf_url = entry.get("raptarchis_pdf_url")
        if not pdf_url:
            raise ValueError(
                f"No raptarchis_pdf_url for {entry.get('article_id')} — "
                "add raptarchis_pdf_url to the entry"
            )
        start_num, end_num = self._parse_article_nums(entry)
        pdf_bytes = _download_pdf(pdf_url)
        full_text = _extract_text_from_pdf(pdf_bytes)
        if start_num == end_num:
            text = _extract_article(full_text, start_num)
        else:
            text = _extract_article_range(full_text, start_num, end_num)
        return self._guard_text(text, pdf_url)

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False

    def _parse_article_nums(self, entry: dict) -> tuple[int, int]:
        """Return (start_num, end_num) from entry overrides or article_id."""
        if entry.get("raptarchis_article_start"):
            start = int(entry["raptarchis_article_start"])
            end = int(entry.get("raptarchis_article_end", start))
            return start, end
        article_id = entry.get("article_id", "")
        # Remove prefix (AK_, KPolD_, Syntagma_)
        nums_part = re.sub(r"^[A-Za-z]+_", "", article_id)
        parts = nums_part.split("_")
        start = int(parts[0])
        end = int(parts[-1]) if len(parts) > 1 else start
        return start, end
