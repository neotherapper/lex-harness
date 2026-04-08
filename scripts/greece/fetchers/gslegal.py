# scripts/greece/fetchers/gslegal.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}


class GsLegalFetcher(BaseFetcher):
    """Fetches from gslegal.gov.gr National Codification Portal."""
    source_id = "gslegal"

    def fetch(self, entry: dict) -> str:
        url = entry.get("gslegal_url")
        if not url:
            raise ValueError(f"No gslegal_url for {entry.get('article_id')}")
        resp = httpx.get(url, headers=_HEADERS, timeout=20, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in ["div.entry-content", "article", "main", "div.content"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from gslegal.gov.gr for {entry.get('article_id')}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
