# scripts/greece/fetchers/kodiko.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
_SELECTORS = [
    "div.nomothesia-content",
    "div.article-content",
    "div.diataksi-content",
    "article",
    "main",
]


class KodikoFetcher(BaseFetcher):
    """Fetches codified statute text from kodiko.gr."""
    source_id = "kodiko"

    def fetch(self, entry: dict) -> str:
        url = entry.get("kodiko_url")
        if not url:
            raise ValueError(f"No kodiko_url for {entry.get('article_id')}")
        resp = httpx.get(url, headers=_HEADERS, timeout=20, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in _SELECTORS:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        # Fallback: all paragraphs
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return self._guard_text(text, url)

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)  # polite delay
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
