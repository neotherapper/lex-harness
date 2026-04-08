# scripts/shared/eur_lex.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
_EUR_LEX_BASE = "https://eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:{celex}"


class EurLexFetcher(BaseFetcher):
    """Fetches EU regulations/directives from EUR-Lex by CELEX number.
    Reusable across all EU member state jurisdiction packs.
    Language: Greek (EL) by default.
    """
    source_id = "eur_lex"

    def fetch(self, entry: dict) -> str:
        celex = entry.get("celex")
        if not celex:
            raise ValueError(f"No celex number for {entry.get('article_id')}")
        url = _EUR_LEX_BASE.format(celex=celex)
        resp = httpx.get(url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # EUR-Lex wraps text in div#text or div.eli-main-title + div.eli-subdivision
        for selector in ["div#text", "div.eli-subdivision", "div.tabContent", "article"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from EUR-Lex for CELEX:{celex}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
