# scripts/core/registry.py
from __future__ import annotations
from scripts.core.base import BaseFetcher

_REGISTRY: dict[str, dict[str, type[BaseFetcher]]] = {}


def register(country: str, source_id: str, fetcher_cls: type[BaseFetcher]) -> None:
    """Register a fetcher class for a given country and source_id."""
    _REGISTRY.setdefault(country, {})[source_id] = fetcher_cls


def resolve(country: str, source_id: str) -> type[BaseFetcher]:
    """Return the fetcher class for country/source_id, or raise ValueError."""
    try:
        return _REGISTRY[country][source_id]
    except KeyError:
        raise ValueError(f"No fetcher registered for {country!r}/{source_id!r}")


def list_sources(country: str) -> list[str]:
    """List all registered source_ids for a country."""
    return list(_REGISTRY.get(country, {}).keys())


def clear() -> None:
    """Reset registry. For testing only."""
    _REGISTRY.clear()
