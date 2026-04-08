# scripts/tests/test_settings.py
import pytest
import yaml
from pathlib import Path
from scripts.core.settings import _parse_frontmatter, load_settings


def test_parse_frontmatter_extracts_keys(tmp_path):
    f = tmp_path / "lex-harness.local.md"
    f.write_text("---\njurisdiction: greece\ncase_id: my-case\n---\n\nNotes.")
    result = _parse_frontmatter(f)
    assert result["jurisdiction"] == "greece"
    assert result["case_id"] == "my-case"


def test_parse_frontmatter_no_block_returns_empty(tmp_path):
    f = tmp_path / "lex-harness.local.md"
    f.write_text("Just notes, no frontmatter.")
    assert _parse_frontmatter(f) == {}


def _write_jurisdiction_yaml(base: Path, sources=None, priority=None):
    jdir = base / "law-packs" / "greece"
    jdir.mkdir(parents=True, exist_ok=True)
    sources = sources or [{"source_id": "et_gr"}, {"source_id": "kodiko"}]
    priority = priority or ["et_gr", "kodiko"]
    (jdir / "jurisdiction.yaml").write_text(yaml.dump({
        "jurisdiction_id": "GR",
        "source_priority": priority,
        "primary_authoritative_sources": sources,
        "fallback_sources": [],
        "pack_dir": "law-packs/greece",
        "display_name": "Greek Law",
        "trusted_source_whitelist": [],
        "mandatory_citation_formats": {},
    }))
    return jdir


def test_defaults_to_greece_when_no_settings_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_jurisdiction_yaml(tmp_path)
    import scripts.core.settings as sm
    monkeypatch.setattr(sm, "_repo_root", lambda: tmp_path)
    result = load_settings()
    assert result.jurisdiction == "greece"


def test_user_source_priority_overrides_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_jurisdiction_yaml(tmp_path)
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "lex-harness.local.md").write_text(
        "---\njurisdiction: greece\nsource_priority:\n  - kodiko\n  - et_gr\n---\n"
    )
    import scripts.core.settings as sm
    monkeypatch.setattr(sm, "_repo_root", lambda: tmp_path)
    result = load_settings()
    assert result.source_priority == ["kodiko", "et_gr"]


def test_country_override_wins_over_settings_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_jurisdiction_yaml(tmp_path)
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "lex-harness.local.md").write_text(
        "---\njurisdiction: greece\n---\n"
    )
    import scripts.core.settings as sm
    monkeypatch.setattr(sm, "_repo_root", lambda: tmp_path)
    result = load_settings(country_override="greece")
    assert result.jurisdiction == "greece"


def test_unknown_source_id_in_override_raises(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    _write_jurisdiction_yaml(tmp_path)
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "lex-harness.local.md").write_text(
        "---\njurisdiction: greece\nsource_priority:\n  - unknown_xyz\n---\n"
    )
    import scripts.core.settings as sm
    monkeypatch.setattr(sm, "_repo_root", lambda: tmp_path)
    with pytest.raises(ValueError, match="Unknown source_id"):
        load_settings()
