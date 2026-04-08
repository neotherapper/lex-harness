# scripts/tests/test_registry.py
import pytest
from scripts.core.base import BaseFetcher
from scripts.core import registry as reg


class _DummyFetcher(BaseFetcher):
    source_id = "dummy"
    def fetch(self, entry): return "x" * 100
    def verify(self, entry): return True


def setup_function():
    reg.clear()


def test_register_and_resolve():
    reg.register("greece", "dummy", _DummyFetcher)
    assert reg.resolve("greece", "dummy") is _DummyFetcher


def test_resolve_unknown_country_raises():
    with pytest.raises(ValueError, match="No fetcher registered for 'unknown'"):
        reg.resolve("unknown", "dummy")


def test_resolve_unknown_source_raises():
    reg.register("greece", "dummy", _DummyFetcher)
    with pytest.raises(ValueError, match="'greece'/'missing'"):
        reg.resolve("greece", "missing")


def test_list_sources_returns_registered():
    reg.register("greece", "dummy", _DummyFetcher)
    assert "dummy" in reg.list_sources("greece")


def test_list_sources_unknown_country_returns_empty():
    assert reg.list_sources("nowhere") == []


def test_clear_removes_all():
    reg.register("greece", "dummy", _DummyFetcher)
    reg.clear()
    assert reg.list_sources("greece") == []
