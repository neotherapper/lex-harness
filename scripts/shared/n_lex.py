# scripts/shared/n_lex.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}

class NLexFetcher(BaseFetcher):
    """Gateway to EU national law via N-Lex ELI-based search.
    N-Lex has no public API — fetch falls back to direct URL if provided.
    Primarily useful when an ELI URI is known for a national instrument.
    """
    source_id = "n_lex"

    def fetch(self, entry: dict) -> str:
        url = entry.get("n_lex_url") or entry.get("eli_url")
        if not url:
            raise ValueError(
                f"No n_lex_url or eli_url for {entry.get('article_id')}. "
                "N-Lex has no search API — provide a direct ELI URI in the manifest."
            )
        resp = httpx.get(url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in ["div.document-content", "article", "main"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from N-Lex for {entry.get('article_id')}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
