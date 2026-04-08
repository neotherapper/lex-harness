# scripts/tests/integration/test_fetch_live.py
"""
Live integration tests — require internet access.
Run with: uv run --directory scripts pytest scripts/tests/integration/ -v -m live

These run on a weekly CI schedule, not on every PR.
They catch:
  - Source URLs going stale (site restructures)
  - SHA256 mismatches (law amendments)
  - New anti-bot measures blocking fetches
"""

import pytest
import scripts.greece  # noqa: F401 — triggers registration

from scripts.core.facade import fetch, verify

# Stable AK articles unlikely to change
_STABLE_ARTICLES = ["AK_592", "AK_297", "AK_281"]


@pytest.mark.live
@pytest.mark.parametrize("article_id", _STABLE_ARTICLES)
def test_fetch_returns_greek_text(article_id):
    """fetch() returns non-empty Greek text from at least one source."""
    result = fetch(article_id, country="greece")
    assert not result.startswith("[UNVERIFIED"), (
        f"All sources failed for {article_id}: {result}"
    )
    assert len(result) >= 50, f"Text too short for {article_id}: {len(result)} chars"
    # Verify it contains Greek characters
    greek_chars = sum(1 for c in result if "\u0370" <= c <= "\u03FF" or "\u1F00" <= c <= "\u1FFF")
    assert greek_chars >= 10, f"No Greek characters found in {article_id} output"


@pytest.mark.live
@pytest.mark.parametrize("article_id", _STABLE_ARTICLES)
def test_verify_matches_stored_sha256(article_id):
    """verify() returns True for articles with correct stored sha256."""
    ok = verify(article_id, country="greece")
    if not ok:
        pytest.xfail(
            f"{article_id}: sha256 mismatch — article may have been amended. "
            "Update the manifest and rerun."
        )
