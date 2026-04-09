# scripts/greece/fetchers/kodiko.py
#
# INVESTIGATION RESULT (2026-04-08): kodiko.gr is a Vue 2 SPA backed by
# app.kodiko.gr JSON APIs. ALL article content (nomothesia tree, article text,
# diataksi endpoints) is behind a paid subscription. The openDocument() JS
# function is overridden to call alertUnauthenticated() — no article can be
# read without a valid session cookie from a paid account.
#
# Additionally, the kodiko_url IDs in laws-manifest.yaml are incorrect —
# IDs in the 57000-range point to unrelated laws (e.g. Νόμος 3865/2010),
# not AK articles.
#
# For AK / KPolD articles use source: manual (hand-authored statute text).
# For ΦΕΚ originals use source: et_gr (PDF blob storage, publicly accessible).
from scripts.core.base import BaseFetcher


class KodikoFetcher(BaseFetcher):
    """
    Placeholder fetcher for kodiko.gr.

    kodiko.gr requires a paid subscription to read any article content —
    the site is a JavaScript SPA whose article-tree and statute-text endpoints
    all return 401 / alertUnauthenticated() without a valid session.

    This fetcher always raises NotImplementedError. Do not set source: kodiko
    in laws-manifest.yaml entries. Use:
      - source: manual   for AK / KPolD articles (hand-authored verbatim text)
      - source: et_gr    for ΦΕΚ originals accessible via PDF blob storage
      - source: eur_lex  for EU-transposed statutes via CELEX number
    """
    source_id = "kodiko"

    def fetch(self, entry: dict) -> str:
        raise NotImplementedError(
            f"kodiko.gr requires a paid subscription — article content is behind "
            f"authentication and cannot be fetched programmatically. "
            f"Entry {entry.get('article_id')!r}: use source: manual, et_gr, or eur_lex instead."
        )

    def verify(self, entry: dict) -> bool:
        return False
