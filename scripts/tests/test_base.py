# scripts/tests/test_base.py
import pytest
from scripts.core.base import BaseFetcher


class _ConcreteOK(BaseFetcher):
    source_id = "test"
    def fetch(self, entry: dict) -> str:
        return "x" * 100
    def verify(self, entry: dict) -> bool:
        return True


def test_concrete_subclass_instantiates():
    f = _ConcreteOK()
    assert f.source_id == "test"


def test_missing_fetch_raises_type_error():
    class _NoFetch(BaseFetcher):
        source_id = "t"
        def verify(self, entry): return True
    with pytest.raises(TypeError):
        _NoFetch()


def test_missing_verify_raises_type_error():
    class _NoVerify(BaseFetcher):
        source_id = "t"
        def fetch(self, entry): return "x" * 100
    with pytest.raises(TypeError):
        _NoVerify()


def test_guard_text_raises_on_short_text():
    f = _ConcreteOK()
    with pytest.raises(ValueError, match="too short"):
        f._guard_text("hi", "http://example.com")


def test_guard_text_passes_on_sufficient_text():
    f = _ConcreteOK()
    text = "Άρθρο 592 — " + "α" * 100
    result = f._guard_text(text, "http://example.com")
    assert result == text
