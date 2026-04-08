# scripts/core/settings.py
from __future__ import annotations
import re
from dataclasses import dataclass, field
from pathlib import Path
import yaml

_SETTINGS_FILENAME = ".claude/lex-harness.local.md"
_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


@dataclass
class LexSettings:
    jurisdiction: str
    case_id: str | None = None
    forum: str | None = None
    source_priority: list[str] = field(default_factory=list)


def _repo_root() -> Path:
    """Walk up from CWD to find repo root (dir containing law-packs/)."""
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / "law-packs").is_dir():
            return parent
    return current  # fallback


def _find_settings_file() -> Path | None:
    current = Path.cwd()
    for parent in [current, *current.parents]:
        candidate = parent / _SETTINGS_FILENAME
        if candidate.exists():
            return candidate
    return None


def _parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def _load_jurisdiction_yaml(jurisdiction: str, base: Path | None = None) -> dict:
    root = base or _repo_root()
    path = root / "law-packs" / jurisdiction / "jurisdiction.yaml"
    if not path.exists():
        raise FileNotFoundError(
            f"jurisdiction.yaml not found at {path}. "
            f"Is '{jurisdiction}' a valid law pack?"
        )
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def load_settings(country_override: str | None = None) -> LexSettings:
    """
    Resolution order:
    1. country_override (CLI --country flag)
    2. jurisdiction field in .claude/lex-harness.local.md
    3. "greece" (MVP default)

    source_priority: user file replaces default entirely (no merge).
    """
    settings_file = _find_settings_file()
    config = _parse_frontmatter(settings_file) if settings_file else {}

    jurisdiction = country_override or config.get("jurisdiction") or "greece"
    jdata = _load_jurisdiction_yaml(jurisdiction)

    user_priority: list[str] | None = config.get("source_priority")
    if user_priority:
        valid_ids = {
            s["source_id"]
            for s in jdata.get("primary_authoritative_sources", [])
            + jdata.get("fallback_sources", [])
        }
        unknown = [s for s in user_priority if s not in valid_ids]
        if unknown:
            raise ValueError(
                f"Unknown source_id(s) in source_priority: {unknown}. "
                f"Valid for '{jurisdiction}': {sorted(valid_ids)}"
            )
        source_priority = user_priority
    else:
        source_priority = jdata["source_priority"]

    return LexSettings(
        jurisdiction=jurisdiction,
        case_id=config.get("case_id"),
        forum=config.get("forum"),
        source_priority=source_priority,
    )
