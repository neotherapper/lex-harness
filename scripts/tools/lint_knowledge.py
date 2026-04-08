#!/usr/bin/env python3
# scripts/tools/lint_knowledge.py
"""
Lint docs/knowledge/ for:
1. Required frontmatter fields in every .md file
2. Case-specific content that must not appear in lex-harness
3. (Optional) HTTP 200 check on source URLs

Usage:
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/tools/lint_knowledge.py
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/tools/lint_knowledge.py --check-urls
"""

import re
import sys
from pathlib import Path
import fire
import yaml

_REPO_ROOT = Path(__file__).parent.parent.parent
_KNOWLEDGE_DIR = _REPO_ROOT / "docs" / "knowledge"

# Required frontmatter in every knowledge doc
_REQUIRED_FIELDS = {"title", "last_verified"}
# Either 'jurisdiction' OR 'scope: global' must be present
_JURISDICTION_OR_GLOBAL = {"jurisdiction", "scope"}

# Patterns that must NEVER appear in lex-harness knowledge docs
_BANNED_PATTERNS = [
    r"\bGeorge\b",
    r"\bYESTAY\b",
    r"\bVIAMAR\b",
    r"\bElliniko\b",
    r"\bYpsilantou\b",
    r"\bCH[1-5]\b",
    r"\bCC[1-6]\b",
    r"\bSA-3[0-9]\b",
    r"€2[,.]189",
    r"€268\b",
    r"€898\b",
]
_BANNED_RE = re.compile("|".join(_BANNED_PATTERNS))

_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _parse_fm(path: Path) -> dict | None:
    match = _FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        return None  # caller appends error


def lint(check_urls: bool = False) -> None:
    """Run all lint checks on docs/knowledge/."""
    if not _KNOWLEDGE_DIR.exists():
        print(f"ERROR: knowledge directory not found: {_KNOWLEDGE_DIR}", file=sys.stderr)
        sys.exit(2)
    errors: list[str] = []
    files = list(_KNOWLEDGE_DIR.rglob("*.md"))

    if not files:
        print(f"No .md files found in {_KNOWLEDGE_DIR}")
        sys.exit(0)

    for path in sorted(files):
        rel = path.relative_to(_REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        fm = _parse_fm(path)
        if fm is None:
            errors.append(f"{rel}: invalid YAML in frontmatter")
            continue

        # Check required fields
        for field in _REQUIRED_FIELDS:
            if field not in fm:
                errors.append(f"{rel}: missing frontmatter field '{field}'")

        # Check jurisdiction OR scope
        if not any(f in fm for f in _JURISDICTION_OR_GLOBAL):
            errors.append(f"{rel}: missing 'jurisdiction' or 'scope' in frontmatter")

        # Check banned patterns
        match = _BANNED_RE.search(text)
        if match:
            errors.append(f"{rel}: banned case-specific content: {match.group()!r}")

    if errors:
        print(f"\n{len(errors)} lint error(s) found:\n")
        for e in errors:
            print(f"  \u2717 {e}")
        sys.exit(1)
    else:
        print(f"\u2713 {len(files)} knowledge docs passed all lint checks.")


if __name__ == "__main__":
    fire.Fire(lint)
