# scripts/greece/fetchers/et_gr.py
#
# INVESTIGATION RESULT (2026-04-08): search.et.gr is a React SPA backed by
# https://searchetv99.azurewebsites.net/api. PDFs live in Azure blob storage:
#   https://ia37rg02wpsa01.blob.core.windows.net/fek/{issueGroupId}/{year}/{name}.pdf
# where name = getFekName(docNum, issueGroupId, year) from the site's JS bundle:
#   name = year + issueGroupId.padStart(2,"0") + docNum.padStart(5,"0")
#
# issueGroupId values: "1"=ΦΕΚ Α (laws), "2"=ΦΕΚ Β (decisions), "3"=ΦΕΚ Γ, etc.
#
# Auto-discovery: POST https://searchetv99.azurewebsites.net/api/simplesearch
#   body: {"searchText": "<query>", "issueGroupId": "<id>"}
#   → returns hits with docNum + year fields → assemble PDF URL from formula above.
#
# Limitation: Pre-~2000 laws are NOT in blob storage (e.g. Ν. 2251/1994 → 404).
# For old laws, set et_gr_pdf_url: null and use source: manual.
import hashlib
import time
import httpx
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
_SIMPLESEARCH_URL = "https://searchetv99.azurewebsites.net/api/simplesearch"
_BLOB_BASE = "https://ia37rg02wpsa01.blob.core.windows.net/fek"


def _build_pdf_url(doc_num: str, issue_group_id: str, year: str) -> str:
    """Replicates getFekLink() from search.et.gr's JS bundle."""
    name = year + issue_group_id.zfill(2) + doc_num.zfill(5)
    return f"{_BLOB_BASE}/{issue_group_id.zfill(2)}/{year}/{name}.pdf"


class EtGrFetcher(BaseFetcher):
    """Fetches ΦΕΚ PDFs from search.et.gr blob storage and extracts article text.

    If et_gr_pdf_url is provided in the entry it is used directly. Otherwise,
    auto-discovery is attempted via the simplesearch API using et_gr_search_text
    and et_gr_issue_group_id from the entry.
    """
    source_id = "et_gr"

    def fetch(self, entry: dict) -> str:
        pdf_url = entry.get("et_gr_pdf_url") or self._resolve_url(entry)
        resp = httpx.get(pdf_url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        if not resp.headers.get("content-type", "").startswith("application/pdf"):
            raise ValueError(f"Expected PDF from {pdf_url}, got {resp.headers.get('content-type')}")
        return self._guard_text(self._extract_pdf(resp.content, entry), pdf_url)

    def _resolve_url(self, entry: dict) -> str:
        """Discover the ΦΕΚ PDF URL via the simplesearch API.

        Requires et_gr_search_text (e.g. "4308/2014") and et_gr_issue_group_id
        (e.g. "1" for ΦΕΚ Α) in the entry. Raises ValueError if no hit is found
        or if the blob URL returns 404 (pre-~2000 laws are not digitised).
        """
        search_text = entry.get("et_gr_search_text")
        issue_group_id = entry.get("et_gr_issue_group_id", "1")
        if not search_text:
            raise ValueError(
                f"No et_gr_pdf_url or et_gr_search_text for {entry.get('article_id')} — "
                "provide et_gr_pdf_url (direct) or et_gr_search_text + et_gr_issue_group_id "
                "(auto-discovery). Pre-2000 laws are not in blob storage; use source: manual."
            )
        resp = httpx.post(
            _SIMPLESEARCH_URL,
            json={"searchText": search_text, "issueGroupId": str(issue_group_id)},
            headers=_HEADERS,
            timeout=20,
        )
        resp.raise_for_status()
        hits = resp.json()
        if not hits:
            raise ValueError(
                f"simplesearch returned no results for {search_text!r} "
                f"(issueGroupId={issue_group_id}) — law may not be in et.gr index"
            )
        # Use the first hit; hits are sorted by relevance by the API.
        hit = hits[0]
        doc_num = str(hit.get("search_DocNum") or hit.get("docNum", ""))
        year = str(hit.get("search_Year") or hit.get("year", ""))
        if not doc_num or not year:
            raise ValueError(
                f"simplesearch hit missing docNum/year fields: {hit}"
            )
        return _build_pdf_url(doc_num, str(issue_group_id), year)

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
