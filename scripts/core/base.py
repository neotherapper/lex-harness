# scripts/core/base.py
from abc import ABC, abstractmethod


class BaseFetcher(ABC):
    """
    Contract for all law fetchers. Subclasses must:
    - Set class attribute source_id (str)
    - Implement fetch(entry) → str  (≥50 chars, verbatim text, or raise)
    - Implement verify(entry) → bool (re-fetch + sha256 compare)

    Never return synthesised or model-generated text from fetch().
    Raise ValueError or a network exception instead.
    """

    source_id: str

    @abstractmethod
    def fetch(self, entry: dict) -> str:
        """Fetch verbatim statutory text. Returns text (≥50 chars) or raises."""

    @abstractmethod
    def verify(self, entry: dict) -> bool:
        """Re-fetch live text; compare sha256[:16] against entry['sha256']."""

    def _guard_text(self, text: str, url: str) -> str:
        """Call this before returning from fetch(). Enforces minimum length."""
        if len(text.strip()) < 50:
            raise ValueError(
                f"Fetched text too short ({len(text.strip())} chars) from {url!r} — "
                "source returned empty/redirect/error page"
            )
        return text
