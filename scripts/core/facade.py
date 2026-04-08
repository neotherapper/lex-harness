# scripts/core/facade.py
from __future__ import annotations
import hashlib
from pathlib import Path
import yaml

from scripts.core.base import BaseFetcher
from scripts.core.registry import resolve, list_sources
from scripts.core.settings import load_settings, LexSettings

_UNVERIFIED = "[UNVERIFIED — all sources failed:"


def _load_manifest(settings: LexSettings) -> list[dict]:
    from scripts.core.settings import _repo_root
    pack_dir = _repo_root() / "law-packs" / settings.jurisdiction
    manifest_path = pack_dir / "laws-manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    entries: list[dict] = list(data.get("core", []))
    for mod_entries in data.get("modules", {}).values():
        entries.extend(mod_entries)
    return entries


def _find_entry(entries: list[dict], article_id: str) -> dict:
    for e in entries:
        if e.get("article_id") == article_id:
            return e
    raise ValueError(f"article_id {article_id!r} not found in manifest")


def fetch(article_id: str, country: str | None = None) -> str:
    settings = load_settings(country_override=country)
    entries = _load_manifest(settings)
    entry = _find_entry(entries, article_id)

    errors: list[str] = []
    for source_id in settings.source_priority:
        try:
            fetcher_cls = resolve(settings.jurisdiction, source_id)
            return fetcher_cls().fetch(entry)
        except Exception as exc:
            errors.append(f"{source_id}: {exc}")

    return f"{_UNVERIFIED} {article_id}] errors: {'; '.join(errors)}"


def verify(article_id: str, country: str | None = None) -> bool:
    settings = load_settings(country_override=country)
    entries = _load_manifest(settings)
    entry = _find_entry(entries, article_id)
    stored_sha = entry.get("sha256", "")

    for source_id in settings.source_priority:
        try:
            fetcher_cls = resolve(settings.jurisdiction, source_id)
            text = fetcher_cls().fetch(entry)
            live_sha = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live_sha == stored_sha
        except Exception:
            continue
    return False


def build(layer: str | None = None, country: str | None = None) -> None:
    settings = load_settings(country_override=country)
    entries = _load_manifest(settings)
    if layer:
        entries = [e for e in entries if e.get("layer") == layer or e.get("module") == layer]
    for entry in entries:
        text = fetch(entry["article_id"], country=settings.jurisdiction)
        status = "UNVERIFIED" if text.startswith(_UNVERIFIED) else "OK"
        print(f"  [{status}] {entry['article_id']}")


def status(country: str | None = None) -> dict:
    settings = load_settings(country_override=country)
    entries = _load_manifest(settings)
    return {
        "jurisdiction": settings.jurisdiction,
        "source_priority": settings.source_priority,
        "entries_total": len(entries),
        "registered_sources": list_sources(settings.jurisdiction),
    }


def sources(country: str | None = None) -> list[str]:
    settings = load_settings(country_override=country)
    return settings.source_priority
