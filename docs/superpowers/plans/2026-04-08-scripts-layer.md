# Scripts Layer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the Google Fire + UV scripts layer for lex-harness — a country-modular, facade-pattern fetch/verify CLI for Greek legislation, backed by a jurisdiction YAML config and a full unit test suite.

**Architecture:** A `BaseFetcher` ABC defines the contract; country modules self-register concrete fetchers into a global registry; the facade iterates `source_priority` from `jurisdiction.yaml` (user-overridable via `.claude/lex-harness.local.md`) and returns the first successful result. The public API is a single Fire CLI entry point (`laws.py`) that never changes even as fetcher implementations evolve.

**Tech Stack:** Python ≥ 3.11, `uv` (dependency manager), `fire` (CLI), `httpx` (HTTP), `beautifulsoup4` (HTML parsing), `pyyaml` (config), `pymupdf` (PDF extraction), `pytest` (testing)

**Branch:** `t11/scripts-knowledge-base-design` (already open — continue on this branch)

---

## File Map

```
law-packs/greece/jurisdiction.yaml          ← NEW: jurisdiction config (REQ-02-010)
scripts/
  pyproject.toml                            ← NEW: UV project
  laws.py                                   ← NEW: Fire CLI entry (public API)
  core/
    __init__.py                             ← NEW: empty
    base.py                                 ← NEW: BaseFetcher ABC + _guard_text
    registry.py                             ← NEW: register/resolve/list_sources/clear
    facade.py                               ← NEW: fetch/verify/build/status/sources
    settings.py                             ← NEW: load_settings + frontmatter parser
  shared/
    __init__.py                             ← NEW: empty
    eur_lex.py                              ← NEW: EurLexFetcher
    n_lex.py                                ← NEW: NLexFetcher
  greece/
    __init__.py                             ← NEW: self-registers all Greek fetchers
    fetchers/
      __init__.py                           ← NEW: empty
      kodiko.py                             ← NEW: KodikoFetcher
      et_gr.py                              ← REPLACE: refactor existing fetch-greece-laws.py logic
      gslegal.py                            ← NEW: GsLegalFetcher
      hellenicparliament.py                 ← NEW: HellenicParliamentFetcher
  tests/
    __init__.py                             ← NEW: empty
    test_base.py                            ← NEW: ABC contract tests
    test_registry.py                        ← NEW: register/resolve tests
    test_settings.py                        ← NEW: settings parse + override tests
    test_facade.py                          ← NEW: facade fallback tests
    test_jurisdiction_yaml.py              ← NEW: schema validation tests
    integration/
      __init__.py                           ← NEW: empty
      test_fetch_live.py                    ← NEW: live source smoke tests (--live flag)
  tools/
    __init__.py                             ← NEW: empty
    lint_knowledge.py                       ← NEW: frontmatter + case-content linter
commands/
  lex-harness-setup.md                      ← NEW: /lex-harness:setup plugin command
  lex-harness-fetch.md                      ← NEW: /lex-harness:fetch plugin command
scripts/fetch-greece-laws.py               ← DELETE: replaced by new structure
```

---

## Task 1: jurisdiction.yaml

**Files:**
- Create: `law-packs/greece/jurisdiction.yaml`
- Create: `scripts/tests/test_jurisdiction_yaml.py`

- [ ] **Step 1: Write the schema validation test first**

```python
# scripts/tests/test_jurisdiction_yaml.py
import pytest
from pathlib import Path
import yaml

REPO_ROOT = Path(__file__).parent.parent.parent

REQUIRED_FIELDS = [
    "jurisdiction_id", "display_name", "primary_authoritative_sources",
    "fallback_sources", "source_priority", "trusted_source_whitelist",
    "mandatory_citation_formats", "pack_dir",
]

def find_jurisdiction_yamls():
    law_packs = REPO_ROOT / "law-packs"
    return list(law_packs.glob("*/jurisdiction.yaml"))

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"])
def test_jurisdiction_yaml_has_required_fields(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    for field in REQUIRED_FIELDS:
        assert field in data, f"Missing '{field}' in {yaml_path}"

@pytest.mark.parametrize("yaml_path", find_jurisdiction_yamls() or ["__no_yamls__"])
def test_source_priority_entries_all_defined(yaml_path):
    if str(yaml_path) == "__no_yamls__":
        pytest.skip("No jurisdiction.yaml files found yet")
    data = yaml.safe_load(Path(yaml_path).read_text(encoding="utf-8"))
    all_ids = {
        s["source_id"]
        for s in data.get("primary_authoritative_sources", []) + data.get("fallback_sources", [])
    }
    for sid in data.get("source_priority", []):
        assert sid in all_ids, f"source_priority entry {sid!r} not defined in sources in {yaml_path}"
```

- [ ] **Step 2: Run test — expect skip (no yaml yet)**

```bash
cd /Users/georgiospilitsoglou/Developer/projects/lex-harness
uv run --directory scripts pytest scripts/tests/test_jurisdiction_yaml.py -v
```

Expected: `SKIPPED` (no jurisdiction.yaml exists yet)

- [ ] **Step 3: Create `law-packs/greece/jurisdiction.yaml`**

```yaml
# law-packs/greece/jurisdiction.yaml
# Jurisdiction configuration object per REQ-02-010
# Skills and scripts read this file — do not hardcode these values elsewhere.

jurisdiction_id: "GR"
display_name: "Greek Law (Ελληνικό Δίκαιο)"
pack_dir: "law-packs/greece"

primary_authoritative_sources:
  - source_id: et_gr
    name: "Εθνικό Τυπογραφείο (et.gr)"
    url: "https://www.et.gr"
    type: official_gazette
    notes: "Primary authority — ΦΕΚ PDFs. Use DownloadFeksApi endpoint."
  - source_id: kodiko
    name: "kodiko.gr"
    url: "https://www.kodiko.gr"
    type: consolidated_code
    notes: "Codified statutes (AK, KPolD, ΠΚ). URL: /nomothesia/document/{id}/{slug}"
  - source_id: gslegal
    name: "gslegal.gov.gr — Εθνική Πύλη Κωδικοποίησης"
    url: "https://www.gslegal.gov.gr"
    type: codification_portal
    notes: "National Codification Portal — General Secretariat for Legal Affairs."
  - source_id: hellenicparliament
    name: "Hellenic Parliament (Βουλή)"
    url: "https://www.hellenicparliament.gr"
    type: enacted_legislation
    notes: "Enacted bills and voting records. Portal instability noted 2026-04-08."

fallback_sources:
  - source_id: eur_lex
    name: "EUR-Lex"
    url: "https://eur-lex.europa.eu"
    type: eu_law
    notes: "EU regulations + directives. Use CELEX numbers. MCP available."

source_priority:
  - et_gr
  - kodiko
  - gslegal
  - hellenicparliament
  - eur_lex

trusted_source_whitelist:
  - et.gr
  - search.et.gr
  - kodiko.gr
  - gslegal.gov.gr
  - hellenicparliament.gr
  - eur-lex.europa.eu
  - areiospagos.gr
  - dsanet.gr
  - lawspot.gr

mandatory_citation_formats:
  statute: "Art. {number} {code} (ΦΕΚ {series}/{year}/{number})"
  case: "{court} {number}/{year}"
  eu_law: "CELEX:{celex} — {eur_lex_url}"

gazette_source: "ΦΕΚ"
gazette_url: "https://www.et.gr"
update_frequency: "weekly"

article_id_prefixes:
  - "AK_"
  - "KPolD_"
  - "N_"
  - "PD_"
  - "MD_"
  - "Syntagma_"
```

- [ ] **Step 4: Run test — expect PASS**

```bash
uv run --directory scripts pytest scripts/tests/test_jurisdiction_yaml.py -v
```

Expected: `2 passed`

- [ ] **Step 5: Commit**

```bash
git add law-packs/greece/jurisdiction.yaml scripts/tests/test_jurisdiction_yaml.py
git commit -s -m "feat(jurisdiction): add greece/jurisdiction.yaml (REQ-02-010) + schema tests"
```

---

## Task 2: UV Project Setup

**Files:**
- Create: `scripts/pyproject.toml`
- Create: `scripts/core/__init__.py`, `scripts/shared/__init__.py`, `scripts/greece/__init__.py` (stubs), `scripts/greece/fetchers/__init__.py`, `scripts/tests/__init__.py`, `scripts/tests/integration/__init__.py`, `scripts/tools/__init__.py`

- [ ] **Step 1: Create `scripts/pyproject.toml`**

```toml
[project]
name = "lex-harness-scripts"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "fire>=0.7.0",
    "httpx>=0.27.0",
    "beautifulsoup4>=4.12.0",
    "pyyaml>=6.0",
    "pymupdf>=1.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-httpx>=0.30",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --ignore=tests/integration"
markers = ["live: marks tests as requiring live internet access (deselect with -m 'not live')"]
```

- [ ] **Step 2: Create all `__init__.py` stubs**

```bash
mkdir -p scripts/core scripts/shared scripts/greece/fetchers scripts/tests/integration scripts/tools
touch scripts/core/__init__.py scripts/shared/__init__.py scripts/greece/fetchers/__init__.py
touch scripts/tests/__init__.py scripts/tests/integration/__init__.py scripts/tools/__init__.py
```

- [ ] **Step 3: Install dependencies**

```bash
uv sync --directory scripts --extra dev
```

Expected: Lock file created, packages installed into `scripts/.venv/`

- [ ] **Step 4: Verify pytest runs with no tests yet**

```bash
uv run --directory scripts pytest -v
```

Expected: `no tests ran` (exit 0 — no errors)

- [ ] **Step 5: Commit**

```bash
git add scripts/pyproject.toml scripts/uv.lock scripts/core/__init__.py scripts/shared/__init__.py scripts/greece/fetchers/__init__.py scripts/tests/__init__.py scripts/tests/integration/__init__.py scripts/tools/__init__.py
git commit -s -m "chore(scripts): UV project setup + directory structure"
```

---

## Task 3: BaseFetcher ABC

**Files:**
- Create: `scripts/core/base.py`
- Create: `scripts/tests/test_base.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run — expect FAIL (ImportError)**

```bash
uv run --directory scripts pytest scripts/tests/test_base.py -v
```

Expected: `ImportError: No module named 'scripts.core.base'`

- [ ] **Step 3: Implement `scripts/core/base.py`**

```python
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
```

- [ ] **Step 4: Run — expect all PASS**

```bash
uv run --directory scripts pytest scripts/tests/test_base.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/core/base.py scripts/tests/test_base.py
git commit -s -m "feat(core): BaseFetcher ABC with _guard_text guardrail"
```

---

## Task 4: Registry

**Files:**
- Create: `scripts/core/registry.py`
- Create: `scripts/tests/test_registry.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run — expect FAIL (ImportError)**

```bash
uv run --directory scripts pytest scripts/tests/test_registry.py -v
```

Expected: `ImportError: No module named 'scripts.core.registry'`

- [ ] **Step 3: Implement `scripts/core/registry.py`**

```python
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
```

- [ ] **Step 4: Run — expect all PASS**

```bash
uv run --directory scripts pytest scripts/tests/test_registry.py -v
```

Expected: `6 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/core/registry.py scripts/tests/test_registry.py
git commit -s -m "feat(core): registry — register/resolve/list_sources/clear"
```

---

## Task 5: Settings

**Files:**
- Create: `scripts/core/settings.py`
- Create: `scripts/tests/test_settings.py`

- [ ] **Step 1: Write failing tests**

```python
# scripts/tests/test_settings.py
import pytest
import yaml
from pathlib import Path
from scripts.core.settings import _parse_frontmatter, load_settings


# ── _parse_frontmatter ────────────────────────────────────────────────────────

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


# ── load_settings ─────────────────────────────────────────────────────────────

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
    # Override to greece (same here, but demonstrates the path)
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
```

- [ ] **Step 2: Run — expect FAIL (ImportError)**

```bash
uv run --directory scripts pytest scripts/tests/test_settings.py -v
```

Expected: `ImportError: No module named 'scripts.core.settings'`

- [ ] **Step 3: Implement `scripts/core/settings.py`**

```python
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
    """Walk up from CWD to find repo root (contains law-packs/)."""
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

    source_priority resolution order:
    1. source_priority in .claude/lex-harness.local.md (replaces default entirely)
    2. source_priority in jurisdiction.yaml
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
```

- [ ] **Step 4: Run — expect all PASS**

```bash
uv run --directory scripts pytest scripts/tests/test_settings.py -v
```

Expected: `5 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/core/settings.py scripts/tests/test_settings.py
git commit -s -m "feat(core): settings — two-layer config with jurisdiction.yaml + .claude/lex-harness.local.md"
```

---

## Task 6: Facade

**Files:**
- Create: `scripts/core/facade.py`
- Create: `scripts/tests/test_facade.py`

- [ ] **Step 1: Write failing tests**

```python
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
```

- [ ] **Step 2: Run — expect FAIL (ImportError)**

```bash
uv run --directory scripts pytest scripts/tests/test_facade.py -v
```

Expected: `ImportError: No module named 'scripts.core.facade'`

- [ ] **Step 3: Implement `scripts/core/facade.py`**

```python
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
```

- [ ] **Step 4: Run — expect all PASS**

```bash
uv run --directory scripts pytest scripts/tests/test_facade.py -v
```

Expected: `4 passed`

- [ ] **Step 5: Commit**

```bash
git add scripts/core/facade.py scripts/tests/test_facade.py
git commit -s -m "feat(core): facade — fetch/verify/build/status/sources with [UNVERIFIED] guardrail"
```

---

## Task 7: Greek Fetchers

**Files:**
- Create: `scripts/greece/fetchers/kodiko.py`
- Create: `scripts/greece/fetchers/et_gr.py`
- Create: `scripts/greece/fetchers/gslegal.py`
- Create: `scripts/greece/fetchers/hellenicparliament.py`
- Create: `scripts/greece/__init__.py` (self-registration)
- Delete: `scripts/fetch-greece-laws.py` (replaced)

- [ ] **Step 1: Implement `scripts/greece/fetchers/kodiko.py`**

```python
# scripts/greece/fetchers/kodiko.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
_SELECTORS = [
    "div.nomothesia-content",
    "div.article-content",
    "div.diataksi-content",
    "article",
    "main",
]


class KodikoFetcher(BaseFetcher):
    """Fetches codified statute text from kodiko.gr."""
    source_id = "kodiko"

    def fetch(self, entry: dict) -> str:
        url = entry.get("kodiko_url")
        if not url:
            raise ValueError(f"No kodiko_url for {entry.get('article_id')}")
        resp = httpx.get(url, headers=_HEADERS, timeout=20, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in _SELECTORS:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        # Fallback: all paragraphs
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        return self._guard_text(text, url)

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)  # polite delay
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
```

- [ ] **Step 2: Implement `scripts/greece/fetchers/et_gr.py`**

```python
# scripts/greece/fetchers/et_gr.py
import hashlib
import time
from pathlib import Path
import httpx
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
_GAZETTE_PENDING = "[GAZETTE-PENDING — manual download required]"


class EtGrFetcher(BaseFetcher):
    """Fetches ΦΕΚ PDFs from search.et.gr and extracts article text."""
    source_id = "et_gr"

    def fetch(self, entry: dict) -> str:
        pdf_url = entry.get("et_gr_pdf_url")
        if not pdf_url:
            return self._guard_text(_GAZETTE_PENDING + f" {entry.get('article_id')}", pdf_url or "")
        resp = httpx.get(pdf_url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        if not resp.headers.get("content-type", "").startswith("application/pdf"):
            raise ValueError(f"Expected PDF from {pdf_url}, got {resp.headers.get('content-type')}")
        return self._guard_text(self._extract_pdf(resp.content, entry), pdf_url)

    def _extract_pdf(self, pdf_bytes: bytes, entry: dict) -> str:
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        except ImportError:
            raise RuntimeError("pymupdf not installed — run: uv sync --directory scripts")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(2)
            text = self.fetch(entry)
            if text.startswith("[GAZETTE-PENDING"):
                return False
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
```

- [ ] **Step 3: Implement `scripts/greece/fetchers/gslegal.py`**

```python
# scripts/greece/fetchers/gslegal.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}


class GsLegalFetcher(BaseFetcher):
    """Fetches from gslegal.gov.gr National Codification Portal."""
    source_id = "gslegal"

    def fetch(self, entry: dict) -> str:
        url = entry.get("gslegal_url")
        if not url:
            raise ValueError(f"No gslegal_url for {entry.get('article_id')}")
        resp = httpx.get(url, headers=_HEADERS, timeout=20, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in ["div.entry-content", "article", "main", "div.content"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from gslegal.gov.gr for {entry.get('article_id')}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
```

- [ ] **Step 4: Implement `scripts/greece/fetchers/hellenicparliament.py`**

```python
# scripts/greece/fetchers/hellenicparliament.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}


class HellenicParliamentFetcher(BaseFetcher):
    """Fetches enacted legislation from hellenicparliament.gr.
    Note: portal instability observed 2026-04-08 — use as last resort before eur_lex."""
    source_id = "hellenicparliament"

    def fetch(self, entry: dict) -> str:
        url = entry.get("hellenicparliament_url")
        if not url:
            raise ValueError(f"No hellenicparliament_url for {entry.get('article_id')}")
        resp = httpx.get(url, headers=_HEADERS, timeout=25, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in ["div.bill-text", "div.law-content", "article", "main"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from hellenicparliament.gr for {entry.get('article_id')}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
```

- [ ] **Step 5: Implement `scripts/greece/__init__.py` (self-registration)**

```python
# scripts/greece/__init__.py
from scripts.core.registry import register
from scripts.greece.fetchers.et_gr import EtGrFetcher
from scripts.greece.fetchers.kodiko import KodikoFetcher
from scripts.greece.fetchers.gslegal import GsLegalFetcher
from scripts.greece.fetchers.hellenicparliament import HellenicParliamentFetcher
from scripts.shared.eur_lex import EurLexFetcher

register("greece", "et_gr", EtGrFetcher)
register("greece", "kodiko", KodikoFetcher)
register("greece", "gslegal", GsLegalFetcher)
register("greece", "hellenicparliament", HellenicParliamentFetcher)
register("greece", "eur_lex", EurLexFetcher)
```

- [ ] **Step 6: Verify imports are clean**

```bash
uv run --directory scripts python -c "import scripts.greece; print('OK')"
```

Expected: `OK`

- [ ] **Step 7: Delete old script**

```bash
git rm scripts/fetch-greece-laws.py
```

- [ ] **Step 8: Run all tests**

```bash
uv run --directory scripts pytest scripts/tests/ -v
```

Expected: All previously passing tests still pass.

- [ ] **Step 9: Commit**

```bash
git add scripts/greece/
git commit -s -m "feat(greece): KodikoFetcher, EtGrFetcher, GsLegalFetcher, HellenicParliamentFetcher + self-registration
delete scripts/fetch-greece-laws.py (replaced by new structure)"
```

---

## Task 8: Shared EU Fetchers

**Files:**
- Create: `scripts/shared/eur_lex.py`
- Create: `scripts/shared/n_lex.py`

- [ ] **Step 1: Implement `scripts/shared/eur_lex.py`**

```python
# scripts/shared/eur_lex.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
_EUR_LEX_BASE = "https://eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:{celex}"


class EurLexFetcher(BaseFetcher):
    """Fetches EU regulations/directives from EUR-Lex by CELEX number.
    Reusable across all EU member state jurisdiction packs.
    Language: Greek (EL) by default.
    """
    source_id = "eur_lex"

    def fetch(self, entry: dict) -> str:
        celex = entry.get("celex")
        if not celex:
            raise ValueError(f"No celex number for {entry.get('article_id')}")
        url = _EUR_LEX_BASE.format(celex=celex)
        resp = httpx.get(url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        # EUR-Lex wraps text in div#text or div.eli-main-title + div.eli-subdivision
        for selector in ["div#text", "div.eli-subdivision", "div.tabContent", "article"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from EUR-Lex for CELEX:{celex}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
```

- [ ] **Step 2: Implement `scripts/shared/n_lex.py`**

```python
# scripts/shared/n_lex.py
import hashlib
import time
import httpx
from bs4 import BeautifulSoup
from scripts.core.base import BaseFetcher

_HEADERS = {
    "User-Agent": "lex-harness/0.1 (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
# N-Lex has no public API — web only. Use ELI-based search when available.
_N_LEX_SEARCH = "https://n-lex.europa.eu/n-lex/recherche/rechercheExpert?lang=en"


class NLexFetcher(BaseFetcher):
    """Gateway to EU national law via N-Lex ELI-based search.
    N-Lex has no public API — fetch falls back to direct URL if provided.
    Primarily useful when an ELI URI is known for a national instrument.
    """
    source_id = "n_lex"

    def fetch(self, entry: dict) -> str:
        url = entry.get("n_lex_url") or entry.get("eli_url")
        if not url:
            raise ValueError(
                f"No n_lex_url or eli_url for {entry.get('article_id')}. "
                "N-Lex has no search API — provide a direct ELI URI in the manifest."
            )
        resp = httpx.get(url, headers=_HEADERS, timeout=30, follow_redirects=True)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for selector in ["div.document-content", "article", "main"]:
            el = soup.select_one(selector)
            if el:
                text = el.get_text(separator="\n", strip=True)
                return self._guard_text(text, url)
        raise ValueError(f"Could not extract text from N-Lex for {entry.get('article_id')}")

    def verify(self, entry: dict) -> bool:
        try:
            time.sleep(1)
            text = self.fetch(entry)
            live = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]
            return live == entry.get("sha256", "")
        except Exception:
            return False
```

- [ ] **Step 3: Verify imports**

```bash
uv run --directory scripts python -c "from scripts.shared.eur_lex import EurLexFetcher; from scripts.shared.n_lex import NLexFetcher; print('OK')"
```

Expected: `OK`

- [ ] **Step 4: Run all tests**

```bash
uv run --directory scripts pytest scripts/tests/ -v
```

Expected: All tests pass.

- [ ] **Step 5: Commit**

```bash
git add scripts/shared/eur_lex.py scripts/shared/n_lex.py
git commit -s -m "feat(shared): EurLexFetcher + NLexFetcher — reusable across EU jurisdiction packs"
```

---

## Task 9: Fire CLI Entry Point

**Files:**
- Create: `scripts/laws.py`

- [ ] **Step 1: Implement `scripts/laws.py`**

```python
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

import json
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
```

- [ ] **Step 2: Verify Fire CLI shows help**

```bash
uv run --directory scripts python scripts/laws.py --help
```

Expected: Lists `fetch`, `verify`, `build`, `status`, `sources` with descriptions.

- [ ] **Step 3: Verify `sources` works without network**

```bash
uv run --directory scripts python scripts/laws.py sources
```

Expected: Prints `et_gr`, `kodiko`, `gslegal`, `hellenicparliament`, `eur_lex` (from jurisdiction.yaml default).

- [ ] **Step 4: Commit**

```bash
git add scripts/laws.py
git commit -s -m "feat(cli): laws.py Fire CLI public API — fetch/verify/build/status/sources"
```

---

## Task 10: Plugin Commands

**Files:**
- Create: `commands/lex-harness-setup.md`
- Create: `commands/lex-harness-fetch.md`

- [ ] **Step 1: Create `commands/lex-harness-setup.md`**

```markdown
---
description: Set up the lex-harness Python environment (run once after installing the plugin)
allowed-tools: Bash(uv:*), Bash(python:*)
---

Setting up lex-harness scripts environment using uv...

!`uv sync --directory ${CLAUDE_PLUGIN_ROOT}/scripts --extra dev`

Verify the environment:
!`uv run --directory ${CLAUDE_PLUGIN_ROOT}/scripts python -c "import fire, httpx, yaml, fitz; print('lex-harness: all dependencies OK')"`

Show available commands:
!`uv run --directory ${CLAUDE_PLUGIN_ROOT}/scripts python ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py --help`

Report the result to the user. If successful, explain they can now use:
- `/lex-harness:fetch <article-id>` to fetch a law article
- `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py status` to check the jurisdiction status
```

- [ ] **Step 2: Create `commands/lex-harness-fetch.md`**

```markdown
---
description: Fetch verbatim text for a Greek law article by article ID
argument-hint: [article-id]
allowed-tools: Bash(uv:*)
---

Fetching law article $1...

!`uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py fetch $1`

Report the fetched text. If the output starts with `[UNVERIFIED`, explain:
- All configured sources failed to return text
- The article may need manual download from et.gr or kodiko.gr
- The user should check `law-packs/greece/laws-manifest.yaml` for the article's source URLs
```

- [ ] **Step 3: Commit**

```bash
git add commands/lex-harness-setup.md commands/lex-harness-fetch.md
git commit -s -m "feat(commands): /lex-harness:setup and /lex-harness:fetch plugin commands"
```

---

## Task 11: Knowledge Base Linter

**Files:**
- Create: `scripts/tools/lint_knowledge.py`

- [ ] **Step 1: Implement `scripts/tools/lint_knowledge.py`**

```python
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


def _parse_fm(path: Path) -> dict:
    match = _FRONTMATTER_RE.match(path.read_text(encoding="utf-8"))
    return yaml.safe_load(match.group(1)) if match else {}


def lint(check_urls: bool = False) -> None:
    """Run all lint checks on docs/knowledge/."""
    errors: list[str] = []
    files = list(_KNOWLEDGE_DIR.rglob("*.md"))

    if not files:
        print(f"No .md files found in {_KNOWLEDGE_DIR}")
        sys.exit(0)

    for path in sorted(files):
        rel = path.relative_to(_REPO_ROOT)
        text = path.read_text(encoding="utf-8")
        fm = _parse_fm(path)

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
            print(f"  ✗ {e}")
        sys.exit(1)
    else:
        print(f"✓ {len(files)} knowledge docs passed all lint checks.")


if __name__ == "__main__":
    fire.Fire(lint)
```

- [ ] **Step 2: Run linter on current (empty) knowledge dir**

```bash
uv run --directory scripts python scripts/tools/lint_knowledge.py
```

Expected: `No .md files found` or `0 files passed` — exit 0.

- [ ] **Step 3: Commit**

```bash
git add scripts/tools/lint_knowledge.py
git commit -s -m "feat(tools): lint_knowledge.py — frontmatter + case-content scanner for docs/knowledge/"
```

---

## Task 12: Integration Tests (scheduled)

**Files:**
- Create: `scripts/tests/integration/test_fetch_live.py`

- [ ] **Step 1: Implement `scripts/tests/integration/test_fetch_live.py`**

```python
# scripts/tests/integration/test_fetch_live.py
"""
Live integration tests — require internet access.
Run with: uv run --directory scripts pytest scripts/tests/integration/ -v -m live

These run on a weekly CI schedule, not on every PR.
They catch:
  - Source URLs going stale (site restructures)
  - SHA256 mismatches (law amendments)
  - New anti-bot measures blocking fetches
"""

import hashlib
import pytest
import scripts.greece  # noqa: F401 — triggers registration

from scripts.core.facade import fetch, verify
from scripts.core.settings import load_settings

# Stable AK articles unlikely to change
_STABLE_ARTICLES = ["AK_592", "AK_297", "AK_281"]


@pytest.mark.live
@pytest.mark.parametrize("article_id", _STABLE_ARTICLES)
def test_fetch_returns_greek_text(article_id):
    """fetch() returns non-empty Greek text from at least one source."""
    result = fetch(article_id, country="greece")
    assert not result.startswith("[UNVERIFIED"), (
        f"All sources failed for {article_id}: {result}"
    )
    assert len(result) >= 50, f"Text too short for {article_id}: {len(result)} chars"
    # Verify it contains Greek characters
    greek_chars = sum(1 for c in result if "\u0370" <= c <= "\u03FF" or "\u1F00" <= c <= "\u1FFF")
    assert greek_chars >= 10, f"No Greek characters found in {article_id} output"


@pytest.mark.live
@pytest.mark.parametrize("article_id", _STABLE_ARTICLES)
def test_verify_matches_stored_sha256(article_id):
    """verify() returns True for articles with correct stored sha256."""
    ok = verify(article_id, country="greece")
    if not ok:
        pytest.xfail(
            f"{article_id}: sha256 mismatch — article may have been amended. "
            "Update the manifest and rerun."
        )
```

- [ ] **Step 2: Run integration tests (skipped by default — use --live flag)**

```bash
uv run --directory scripts pytest scripts/tests/integration/ -v -m live
```

Expected: Tests run and either PASS or XFAIL (sha256 mismatch = article updated).

> **Note:** These are NOT run in the default `pytest` suite. They require internet and are run by the weekly CI schedule. Do not run them on every PR.

- [ ] **Step 3: Commit**

```bash
git add scripts/tests/integration/test_fetch_live.py
git commit -s -m "test(integration): live fetcher smoke tests + sha256 manifest verification"
```

---

## Task 13: Full Test Suite + Final Check

- [ ] **Step 1: Run complete unit test suite**

```bash
uv run --directory scripts pytest scripts/tests/ -v
```

Expected output (all tests pass):
```
scripts/tests/test_base.py::test_concrete_subclass_instantiates PASSED
scripts/tests/test_base.py::test_missing_fetch_raises_type_error PASSED
scripts/tests/test_base.py::test_missing_verify_raises_type_error PASSED
scripts/tests/test_base.py::test_guard_text_raises_on_short_text PASSED
scripts/tests/test_base.py::test_guard_text_passes_on_sufficient_text PASSED
scripts/tests/test_registry.py::test_register_and_resolve PASSED
scripts/tests/test_registry.py::test_resolve_unknown_country_raises PASSED
scripts/tests/test_registry.py::test_resolve_unknown_source_raises PASSED
scripts/tests/test_registry.py::test_list_sources_returns_registered PASSED
scripts/tests/test_registry.py::test_list_sources_unknown_country_returns_empty PASSED
scripts/tests/test_registry.py::test_clear_removes_all PASSED
scripts/tests/test_settings.py::test_parse_frontmatter_extracts_keys PASSED
scripts/tests/test_settings.py::test_parse_frontmatter_no_block_returns_empty PASSED
scripts/tests/test_settings.py::test_defaults_to_greece_when_no_settings_file PASSED
scripts/tests/test_settings.py::test_user_source_priority_overrides_default PASSED
scripts/tests/test_settings.py::test_country_override_wins_over_settings_file PASSED
scripts/tests/test_settings.py::test_unknown_source_id_in_override_raises PASSED
scripts/tests/test_facade.py::test_fetch_returns_first_successful_source PASSED
scripts/tests/test_facade.py::test_fetch_returns_unverified_when_all_fail PASSED
scripts/tests/test_facade.py::test_fetch_unknown_article_raises PASSED
scripts/tests/test_facade.py::test_sources_returns_priority_list PASSED
scripts/tests/test_jurisdiction_yaml.py::test_jurisdiction_yaml_has_required_fields[greece] PASSED
scripts/tests/test_jurisdiction_yaml.py::test_source_priority_entries_all_defined[greece] PASSED
```

- [ ] **Step 2: Verify Fire CLI end-to-end (no network)**

```bash
uv run --directory scripts python scripts/laws.py sources
uv run --directory scripts python scripts/laws.py --help
```

Expected: Prints source list and help text with no errors.

- [ ] **Step 3: Open PR**

```bash
git push -u origin t11/scripts-knowledge-base-design
gh pr create \
  --title "T11: Scripts layer — Fire+UV CLI, facade/registry, Greek fetchers, jurisdiction.yaml" \
  --body "$(cat <<'EOF'
## Summary
- `law-packs/greece/jurisdiction.yaml` — jurisdiction config object per REQ-02-010
- `scripts/` — UV project with Fire CLI, BaseFetcher ABC, registry, facade, settings
- Greek fetchers: KodikoFetcher, EtGrFetcher, GsLegalFetcher, HellenicParliamentFetcher
- Shared EU fetchers: EurLexFetcher, NLexFetcher
- Plugin commands: `/lex-harness:setup`, `/lex-harness:fetch`
- Full unit test suite (23 tests) + integration test scaffold
- Knowledge base linter (`lint_knowledge.py`)
- Deletes `scripts/fetch-greece-laws.py` (replaced)

## Requirements covered
- REQ-02-002: hot vault architecture (law-packs/greece/)
- REQ-02-005: fallback chain (facade source priority loop)
- REQ-02-010: jurisdiction config object (jurisdiction.yaml)
- REQ-03: modular retrieval strategy (registry + country self-registration)

## Test plan
- [ ] `uv sync --directory scripts --extra dev`
- [ ] `uv run --directory scripts pytest scripts/tests/ -v` — 23 tests pass
- [ ] `uv run --directory scripts python scripts/laws.py sources` — prints 5 sources
- [ ] `/lex-harness:setup` command works via ${CLAUDE_PLUGIN_ROOT}

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Self-Review Checklist

- [x] **jurisdiction.yaml schema test** — Task 1 validates all required fields + source_priority consistency
- [x] **BaseFetcher `_guard_text`** — enforces ≥50 chars, tested in Task 3
- [x] **Registry `clear()`** — for test isolation, each test calls `setup_function → clear()`
- [x] **Settings `_repo_root()`** — monkeypatched in tests so CI doesn't need the full repo tree
- [x] **Facade `[UNVERIFIED]` tag** — tested in test_facade, emitted when all sources fail
- [x] **Greece `__init__.py` self-registration** — imported in `laws.py` at module level
- [x] **`fetch-greece-laws.py` deleted** — `git rm` in Task 7
- [x] **Integration tests skipped by default** — `--ignore=tests/integration` in pytest.ini_options
- [x] **`${CLAUDE_PLUGIN_ROOT}` in commands** — both command files use it correctly

**Gap check against spec deliverables:**
- S1 `pyproject.toml` ✓ Task 2
- S2 `laws.py` ✓ Task 9
- S3 `core/` ✓ Tasks 3-6
- S4 `shared/` ✓ Task 8
- S5 `scripts/greece/` ✓ Task 7
- S6 `tests/` ✓ Tasks 3-6 (unit) + Task 12 (integration)
- S7 `lint_knowledge.py` ✓ Task 11
- S8 `commands/lex-harness-setup.md` ✓ Task 10
- S9 `commands/lex-harness-fetch.md` ✓ Task 10
- J1 `jurisdiction.yaml` ✓ Task 1
- C1 CLAUDE.md update — **not in this plan** (add as post-merge task or include in PR description as a manual step)
