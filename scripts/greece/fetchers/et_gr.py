# scripts/greece/fetchers/et_gr.py
import hashlib
import time
from pathlib import Path
import httpx
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}


class EtGrFetcher(BaseFetcher):
    """Fetches ΦΕΚ PDFs from search.et.gr and extracts article text."""
    source_id = "et_gr"

    def fetch(self, entry: dict) -> str:
        pdf_url = entry.get("et_gr_pdf_url")
        if not pdf_url:
            raise ValueError(
                f"No et_gr_pdf_url for {entry.get('article_id')} — "
                "gazette PDF URL required; manual download may be necessary"
            )
        resp = httpx.get(pdf_url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        if not resp.headers.get("content-type", "").startswith("application/pdf"):
            raise ValueError(f"Expected PDF from {pdf_url}, got {resp.headers.get('content-type')}")
        return self._guard_text(self._extract_pdf(resp.content, entry), pdf_url)

    def _extract_pdf(self, pdf_bytes: bytes, entry: dict) -> str:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        except ImportError:
            raise RuntimeError("pymupdf not installed — run: uv sync --directory scripts")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(2)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
