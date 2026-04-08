#!/usr/bin/env python3
# scripts/laws.py
"""
lex-harness law pack CLI — public API.

Usage (from plugin):
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py fetch AK_592
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py verify AK_592
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py build --layer core
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py status
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py sources

All commands auto-detect jurisdiction from .claude/lex-harness.local.md.
Pass --country to override (e.g., --country greece).

This file is the stable public API — implementations behind it may change.
"""

from __future__ import annotations
import json
import sys
from pathlib import Path

# Ensure the repo root (parent of the scripts/ package) is on sys.path so that
# `import scripts.*` works when this file is executed directly via:
#   uv run --directory scripts python laws.py ...
_SCRIPTS_DIR = Path(__file__).parent
_REPO_ROOT = _SCRIPTS_DIR.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import fire

# Import country packs to trigger self-registration
import scripts.greece  # noqa: F401  registers Greek fetchers

from scripts.core.facade import (
    fetch as _fetch,
    verify as _verify,
    build as _build,
    status as _status,
    sources as _sources,
)


class LawsCLI:
    """lex-harness law pack management CLI."""

    def fetch(self, article_id: str, country: str = None):
        """Fetch verbatim text for a law article.

        Args:
            article_id: e.g. AK_592, KPolD_338
            country:    jurisdiction override (default: from .claude/lex-harness.local.md)
        """
        result = _fetch(article_id, country=country)
        print(result)

    def verify(self, article_id: str, country: str = None):
        """Re-verify sha256 of a fetched article against live source.

        Prints OK or MISMATCH (exit 0 either way — check output).
        """
        ok = _verify(article_id, country=country)
        print("OK" if ok else "MISMATCH — article may have been amended")

    def build(self, layer: str = None, country: str = None):
        """Fetch and write all articles in the manifest.

        Args:
            layer:   filter to 'core' or a module name e.g. 'tenancy'
            country: jurisdiction override
        """
        _build(layer=layer, country=country)

    def status(self, country: str = None):
        """Show jurisdiction, source priority, manifest size, registered sources."""
        data = _status(country=country)
        print(json.dumps(data, indent=2, ensure_ascii=False))

    def sources(self, country: str = None):
        """List active source priority for the jurisdiction."""
        for s in _sources(country=country):
            print(f"  {s}")


if __name__ == "__main__":
    fire.Fire(LawsCLI)
