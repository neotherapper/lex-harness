# scripts/tests/test_facade.py
import pytest
from scripts.core.base import BaseFetcher
from scripts.core import registry as reg
from scripts.core import facade
from scripts.core.settings import LexSettings


class _OKFetcher(BaseFetcher):
    source_id = "ok"
    def fetch(self, entry): return "Άρθρο verbatim text " * 5
    def verify(self, entry): return True


class _FailFetcher(BaseFetcher):
    source_id = "fail"
    def fetch(self, entry): raise ConnectionError("source down")
    def verify(self, entry): return False


def _mock_settings(priority: list[str]) -> LexSettings:
    return LexSettings(jurisdiction="greece", source_priority=priority)


def _mock_entries(article_id: str) -> list[dict]:
    return [{"article_id": article_id, "layer": "core", "sha256": "abc123"}]


def setup_function():
    reg.clear()


def test_fetch_returns_first_successful_source(monkeypatch):
    reg.register("greece", "fail", _FailFetcher)
    reg.register("greece", "ok", _OKFetcher)
    monkeypatch.setattr(facade, "load_settings", lambda **kw: _mock_settings(["fail", "ok"]))
    monkeypatch.setattr(facade, "_load_manifest", lambda s: _mock_entries("AK_592"))
    result = facade.fetch("AK_592")
    assert "verbatim text" in result


def test_fetch_returns_unverified_when_all_fail(monkeypatch):
    reg.register("greece", "fail", _FailFetcher)
    monkeypatch.setattr(facade, "load_settings", lambda **kw: _mock_settings(["fail"]))
    monkeypatch.setattr(facade, "_load_manifest", lambda s: _mock_entries("AK_592"))
    result = facade.fetch("AK_592")
    assert result.startswith("[UNVERIFIED")
    assert "AK_592" in result


def test_fetch_unknown_article_raises(monkeypatch):
    monkeypatch.setattr(facade, "load_settings", lambda **kw: _mock_settings([]))
    monkeypatch.setattr(facade, "_load_manifest", lambda s: [])
    with pytest.raises(ValueError, match="not found in manifest"):
        facade.fetch("UNKNOWN_999")


def test_sources_returns_priority_list(monkeypatch):
    monkeypatch.setattr(facade, "load_settings", lambda **kw: _mock_settings(["et_gr", "kodiko"]))
    result = facade.sources()
    assert result == ["et_gr", "kodiko"]
