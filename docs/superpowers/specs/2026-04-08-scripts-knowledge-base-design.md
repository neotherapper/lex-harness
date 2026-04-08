# Design: Scripts Layer + Knowledge Base — lex-harness

**Date:** 2026-04-08
**Author:** Georgios Pilitsoglou
**Status:** Approved — ready for implementation planning

---

## 1. Goals

1. Replace the current single-file `scripts/fetch-greece-laws.py` (argparse + requests) with a structured, extensible scripts layer using **Google Fire + UV**.
2. Enforce a **stable public API** (Fire CLI commands) with swappable implementations behind a facade — adding a new country never touches the public interface.
3. Make the plugin **self-configuring**: after `git clone` + plugin activation, users run one setup command and all scripts work. Jurisdiction is detected automatically from a settings file.
4. Allow **source priority to be user-overridable** per case while keeping sensible per-jurisdiction defaults.
5. Port the relevant **jurisdiction-generic research** from the yestay project into a structured knowledge base in this repo, so any fork or new session has the information needed without re-researching.

---

## 2. Constraints

- **Stable public API:** the Fire CLI commands (`fetch`, `verify`, `build`, `status`, `sources`) never change. Only the implementations behind the facade change.
- **Country-modular:** adding `uk/` or `de/` is purely additive — no changes to core, facade, or CLI.
- **Plugin install model:** users install via `/plugin install neotherapper/lex-harness`. Plugin files land in `~/.claude/plugins/cache/lex-harness/`. Users never clone the repo. Scripts are referenced via the `${CLAUDE_PLUGIN_ROOT}` env var that Claude Code expands in commands.
- **Plugin setup:** `plugin.json` has no `postInstall` hook. Setup runs via `/lex-harness:setup` command which uses `${CLAUDE_PLUGIN_ROOT}` to find and sync the UV environment.
- **EU fetchers are shared:** EUR-Lex and N-Lex cover all EU member states. They live in `scripts/shared/` and each country opts in via its `__init__.py`.
- **No case-specific content in lex-harness:** all content ported from yestay must be stripped of George/YESTAY/VIAMAR references, property addresses, charge codes, and specific monetary amounts.

---

## 3. Scripts Layer Architecture

### 3.1 Directory Structure

```
scripts/
  pyproject.toml                    ← UV project (fire, httpx, pyyaml, pymupdf, beautifulsoup4)
  laws.py                           ← Fire CLI entry point — public API, never changes
  core/
    __init__.py
    base.py                         ← BaseFetcher ABC: fetch(entry) → str, verify(entry) → bool
    registry.py                     ← register(country, source_id, cls) + resolve(country, source_id)
    facade.py                       ← fetch(), verify(), build(), status(), sources()
    settings.py                     ← load_settings() — walks CWD up to find .lex-harness.json
  shared/                           ← Reusable across any EU/international country pack
    __init__.py
    eur_lex.py                      ← EurLexFetcher (CELEX numbers, any EU member state)
    n_lex.py                        ← NLexFetcher (EU N-Lex gateway, ELI search)
  greece/
    __init__.py                     ← self-registers all Greek fetchers + opted-in shared fetchers
    constants.py                    ← JURISDICTION, SOURCE_PRIORITY, PACK_DIR, ARTICLE_ID_PREFIXES
    fetchers/
      __init__.py
      kodiko.py                     ← KodikoFetcher
      et_gr.py                      ← EtGrFetcher
      gslegal.py                    ← GsLegalFetcher
      hellenicparliament.py         ← HellenicParliamentFetcher
  # uk/, de/, fr/ — future, same pattern; zero changes to core or CLI
```

### 3.2 Abstract Base

```python
# scripts/core/base.py
from abc import ABC, abstractmethod

class BaseFetcher(ABC):
    source_id: str  # e.g. "kodiko", "et_gr", "eur_lex"

    @abstractmethod
    def fetch(self, entry: dict) -> str:
        """Fetch verbatim text for one manifest entry. Returns text or raises."""

    @abstractmethod
    def verify(self, entry: dict) -> bool:
        """Re-fetch and compare sha256 against stored value. Returns True if match."""
```

### 3.3 Registry

```python
# scripts/core/registry.py
_REGISTRY: dict[str, dict[str, type[BaseFetcher]]] = {}

def register(country: str, source_id: str, fetcher_cls: type[BaseFetcher]) -> None:
    _REGISTRY.setdefault(country, {})[source_id] = fetcher_cls

def resolve(country: str, source_id: str) -> type[BaseFetcher]:
    try:
        return _REGISTRY[country][source_id]
    except KeyError:
        raise ValueError(f"No fetcher registered for {country}/{source_id}")

def list_sources(country: str) -> list[str]:
    return list(_REGISTRY.get(country, {}).keys())
```

### 3.4 Facade

```python
# scripts/core/facade.py
from scripts.core.registry import resolve, list_sources
from scripts.core.settings import load_settings

def fetch(article_id: str, country: str | None = None) -> str:
    settings = load_settings(country_override=country)
    entry = _load_entry(settings, article_id)
    for source_id in settings.source_priority:
        fetcher_cls = resolve(settings.jurisdiction, source_id)
        try:
            return fetcher_cls().fetch(entry)
        except Exception:
            continue  # try next source in priority order
    raise RuntimeError(f"All sources failed for {article_id}")

def verify(article_id: str, country: str | None = None) -> bool: ...
def build(layer: str | None = None, country: str | None = None) -> None: ...
def status(country: str | None = None) -> dict: ...
def sources(country: str | None = None) -> list[str]: ...
```

### 3.5 Country Self-Registration

```python
# scripts/greece/__init__.py
from scripts.core.registry import register
from scripts.greece.fetchers.et_gr import EtGrFetcher
from scripts.greece.fetchers.kodiko import KodikoFetcher
from scripts.greece.fetchers.gslegal import GsLegalFetcher
from scripts.greece.fetchers.hellenicparliament import HellenicParliamentFetcher
from scripts.shared.eur_lex import EurLexFetcher

register("greece", "et_gr",               EtGrFetcher)
register("greece", "kodiko",              KodikoFetcher)
register("greece", "gslegal",             GsLegalFetcher)
register("greece", "hellenicparliament",  HellenicParliamentFetcher)
register("greece", "eur_lex",             EurLexFetcher)   # EU shared, opted in here
```

Adding `uk/` = new `__init__.py` registering UK-specific fetchers. EUR-Lex can be opted in or not. Zero changes to `core/` or `laws.py`.

### 3.6 Public API — Fire CLI

```python
# scripts/laws.py
import fire
from scripts.core.facade import fetch, verify, build, status, sources
import scripts.greece  # auto-import triggers self-registration
# import scripts.uk     # add as new packs ship

class LawsCLI:
    def fetch(self, article_id: str, country: str = None):
        """Fetch verbatim text for an article."""
        print(fetch(article_id, country=country))

    def verify(self, article_id: str, country: str = None):
        """Re-verify sha256 of a fetched article against live source."""
        ok = verify(article_id, country=country)
        print("OK" if ok else "MISMATCH")

    def build(self, layer: str = None, country: str = None):
        """Build/refresh the law pack (all entries or filtered by layer)."""
        build(layer=layer, country=country)

    def status(self, country: str = None):
        """Show fetch status and sha256 manifest summary."""
        import json; print(json.dumps(status(country=country), indent=2, ensure_ascii=False))

    def sources(self, country: str = None):
        """List registered fetchers and active source priority."""
        for s in sources(country=country):
            print(s)

if __name__ == "__main__":
    fire.Fire(LawsCLI)
```

**CLI usage:**

```bash
# jurisdiction auto-detected from .lex-harness.json in case repo
uv run scripts/laws.py fetch AK_592
uv run scripts/laws.py verify AK_592
uv run scripts/laws.py build --layer core
uv run scripts/laws.py status
uv run scripts/laws.py sources

# explicit override
uv run scripts/laws.py fetch AK_592 --country greece
```

---

## 4. Settings System

### 4.1 Two-Layer Config

| Layer | File | Owner | Purpose |
|---|---|---|---|
| Defaults | `scripts/greece/constants.py` | Plugin maintainer | Per-jurisdiction static defaults |
| Override | `.claude/lex-harness.local.md` | User (case repo) | Per-case settings, created by `/lex-harness:init` |

This follows the standard Claude Code plugin-settings pattern: a `.claude/<plugin-name>.local.md` file with YAML frontmatter in the user's project directory. User-supplied values **always win**. `source_priority` in the user file completely replaces the constant (no merge).

### 4.2 Settings File Format (`.claude/lex-harness.local.md`)

```markdown
---
jurisdiction: greece
case_id: my-rental-dispute
forum: eirino
source_priority:
  - et_gr
  - kodiko
  - gslegal
  - eur_lex
---

# My Case Notes
Free-form notes about this case for reference.
```

Created by `/lex-harness:init`. Users edit `source_priority` to override fetch order. The file is gitignored by default (case-specific).

### 4.3 Settings Object

```python
# scripts/core/settings.py
from dataclasses import dataclass, field
from pathlib import Path
import re

@dataclass
class LexSettings:
    jurisdiction: str
    case_id: str | None = None
    forum: str | None = None
    source_priority: list[str] = field(default_factory=list)

def load_settings(country_override: str | None = None) -> LexSettings:
    """
    Walk up from CWD to find .claude/lex-harness.local.md (standard plugin-settings pattern).
    Parse YAML frontmatter. Merge with jurisdiction constants.
    CLI --country arg overrides everything.
    Falls back to 'greece' if no settings found (MVP default).
    """
    config = _parse_local_md()   # returns {} if not found
    jurisdiction = country_override or config.get("jurisdiction") or "greece"
    constants = _load_constants(jurisdiction)

    return LexSettings(
        jurisdiction=jurisdiction,
        case_id=config.get("case_id"),
        forum=config.get("forum"),
        source_priority=config.get("source_priority") or constants["SOURCE_PRIORITY"],
    )
```

### 4.4 Greece Constants

```python
# scripts/greece/constants.py
JURISDICTION = "greece"
PACK_DIR = "law-packs/greece"
SOURCE_PRIORITY = ["et_gr", "kodiko", "gslegal", "hellenicparliament", "eur_lex"]
ARTICLE_ID_PREFIXES = ["AK_", "KPolD_", "N_", "PD_", "MD_"]
HEADERS = {
    "User-Agent": "lex-harness/0.1 law-pack-builder (github.com/neotherapper/lex-harness)",
    "Accept-Language": "el,en;q=0.9",
}
```

---

## 5. Plugin Setup

`plugin.json` has no `postInstall` hook — confirmed across all official Claude Code plugins. Setup uses the `${CLAUDE_PLUGIN_ROOT}` env var, which Claude Code expands in commands to the plugin's installed path (`~/.claude/plugins/cache/lex-harness/`).

**`/lex-harness:setup` command** (in `commands/lex-harness-setup.md`):

```markdown
---
description: Set up the lex-harness Python environment (run once after install)
allowed-tools: Bash(uv:*)
---

Setting up lex-harness scripts environment:

!`uv sync --directory ${CLAUDE_PLUGIN_ROOT}/scripts`

Verify setup:
!`uv run --directory ${CLAUDE_PLUGIN_ROOT}/scripts python -c "import fire, httpx, yaml; print('OK')"`

Report the result. If successful, the user can now run:
  uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py status
```

**Plugin commands** reference scripts via `${CLAUDE_PLUGIN_ROOT}`:

```markdown
# commands/lex-harness-fetch.md
---
description: Fetch verbatim text for a Greek law article
argument-hint: [article-id]
allowed-tools: Bash(uv:*)
---

!`uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py fetch $1`
```

Users run `/lex-harness:setup` once after installing the plugin. All subsequent commands work without any path knowledge.

---

## 6. Source Priority for Greece

Ordered by authority and programmatic reliability:

| Priority | Source ID | Class | Coverage | Access Method |
|---|---|---|---|---|
| 1 | `et_gr` | `EtGrFetcher` | All ΦΕΚ PDFs (primary authority) | HTTP download, PDF extraction |
| 2 | `kodiko` | `KodikoFetcher` | Codified statutes (AK, KPolD, ΠΚ) | HTML scrape, verified URL pattern |
| 3 | `gslegal` | `GsLegalFetcher` | National Codification Portal | HTML scrape |
| 4 | `hellenicparliament` | `HellenicParliamentFetcher` | Enacted bills, voting records | HTML scrape (portal instability noted) |
| 5 | `eur_lex` | `EurLexFetcher` (shared) | EU regulations (GDPR, directives) | CELEX URI, MCP or HTTP |

`EurLexFetcher` and `NLexFetcher` live in `scripts/shared/` and are reusable by any EU jurisdiction pack.

---

## 7. Knowledge Base

### 7.1 Purpose

A structured set of research documents committed to this repo so that:
- Any contributor forking lex-harness has the foundational Greek law knowledge without re-researching
- Skills can reference these docs as authoritative background
- Future jurisdiction packs can see the pattern for what to document

### 7.2 Directory Structure

```
docs/knowledge/
  README.md                          ← index + how to use
  LEGAL_AI_FRAMEWORK.md              ← jurisdiction-agnostic: 7-layer system, SOLAR verification,
                                        hybrid RAG, phase gates (ported from yestay, stripped)
  greece/
    CORPUS_MAP.md                    ← 21 core articles + 8 module trigger conditions
    COURT_AUTHORITY.md               ← court hierarchy, citation weights, EU supremacy, soft law
    LAW_SOURCES.md                   ← source priority matrix, access methods, live probe findings
    sources/
      et_gr.md                       ← ΦΕΚ REST API, Azure backend, URL patterns
      kodiko_gr.md                   ← consolidated article text, URL structure
      areiospagos_gr.md              ← ΑΠ search, windows-1253 charset, POST forms
      diavgeia_gov_gr.md             ← REST API (no auth), parameter quirks, pagination
      nomiki_vivliothiki.md          ← Qualex, 469K decisions, subscription — flag for users
      isocrates_dsanet.md            ← ΔΣΑ Isocrates, eirino decisions
      lawspot_gr.md                  ← free summaries, cross-verification use
      eur_lex.md                     ← CELEX patterns, ELI, Greek-language access
      n_lex.md                       ← EU gateway, multi-country search, no API
    modules/
      consumer_protection.md         ← Law 2251/1994, Directive 93/13, ECJ cases (stripped)
```

### 7.3 Content Sources and Porting Rules

| Knowledge Doc | Source in yestay | Relevance | What to strip |
|---|---|---|---|
| `LEGAL_AI_FRAMEWORK.md` | `09_ai_research/LEGAL_AI_FRAMEWORK.md` | HIGH — jurisdiction-agnostic | Case-specific phase examples |
| `greece/CORPUS_MAP.md` | `09_ai_research/LEGAL_CORPUS_MAP.md` | HIGH | YESTAY module triggers, charge codes |
| `greece/COURT_AUTHORITY.md` | `09_ai_research/COURT_AUTHORITY_SOURCES.md` | HIGH | George/case references |
| `greece/LAW_SOURCES.md` | `09_ai_research/LAW_SOURCE_DISCOVERY.md` | HIGH | Case-specific probe notes |
| `greece/sources/*.md` | `09_ai_research/research/12_greek_legal_databases/` | HIGH — no case content | Nothing — already generic |
| `greece/modules/consumer_protection.md` | `05_legal_research/consumer_protection_law.md` | HIGH | Specific amounts, G vs Y framing |

**Strip rule:** remove any reference to: George, YESTAY, VIAMAR, Elliniko, Ypsilantou, specific monetary amounts (€2,189 etc.), charge codes (CH1-CH5, CC1-CC6, SA-31), case-specific dates tied to the dispute.

**Keep:** statutes, case law citations (ΑΠ decisions etc.), API patterns, URL structures, court hierarchy rules, database access methods, module trigger conditions — all jurisdiction knowledge, none of the case knowledge.

---

## 8. Jurisdiction Config Object (REQ-02-010 alignment)

The formal requirements define **jurisdiction as a YAML config object** — not Python constants — so skills and agents can read it without importing Python. Our `constants.py` is superseded by `law-packs/greece/jurisdiction.yaml`, which the scripts import at runtime.

```yaml
# law-packs/greece/jurisdiction.yaml
jurisdiction_id: "GR"
display_name: "Greek Law (Ελληνικό Δίκαιο)"
primary_authoritative_sources:
  - source_id: et_gr
    name: "Εθνικό Τυπογραφείο (et.gr)"
    url: "https://www.et.gr"
    type: official_gazette
  - source_id: kodiko
    name: "kodiko.gr"
    url: "https://www.kodiko.gr"
    type: consolidated_code
  - source_id: gslegal
    name: "gslegal.gov.gr"
    url: "https://www.gslegal.gov.gr"
    type: codification_portal
  - source_id: hellenicparliament
    name: "Hellenic Parliament"
    url: "https://www.hellenicparliament.gr"
    type: enacted_legislation
fallback_sources:
  - source_id: eur_lex
    name: "EUR-Lex"
    url: "https://eur-lex.europa.eu"
    type: eu_law
source_priority:
  - et_gr
  - kodiko
  - gslegal
  - hellenicparliament
  - eur_lex
trusted_source_whitelist:
  - et.gr
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
gazette_source: "ΦΕΚ / et.gr"
gazette_url: "https://www.et.gr"
update_frequency: "weekly"
article_id_prefixes:
  - "AK_"
  - "KPolD_"
  - "N_"
  - "PD_"
  - "MD_"
pack_dir: "law-packs/greece"
```

`scripts/core/settings.py` loads this YAML to populate `source_priority`, the trusted whitelist, and citation formats. `scripts/greece/constants.py` is removed — `jurisdiction.yaml` is the single source of truth. Skills can read the same file directly with `@${CLAUDE_PLUGIN_ROOT}/law-packs/greece/jurisdiction.yaml`.

---

## 9. Tests

### 9.1 Unit Tests (`scripts/tests/`)

| Test file | What it covers |
|---|---|
| `test_registry.py` | `register()` + `resolve()` correct; `resolve()` raises `ValueError` for unknown country/source |
| `test_settings.py` | Frontmatter parse; user `source_priority` wins over jurisdiction default; missing file falls back to "greece"; `--country` CLI arg overrides all |
| `test_facade.py` | Source priority fallback with mock fetchers (first fails, second succeeds); all-fail raises `RuntimeError` |
| `test_base.py` | Subclass without implementing `fetch()` / `verify()` raises `TypeError` |
| `test_jurisdiction_yaml.py` | Each `law-packs/*/jurisdiction.yaml` validates against the schema; `source_priority` entries all present in `primary_authoritative_sources` + `fallback_sources` |

Run with: `uv run pytest scripts/tests/ -v`

### 9.2 Integration Tests (scheduled, not on every commit)

Run against live sources on a weekly CI schedule to detect source breakage or law amendments:

| Test | Source | What it checks |
|---|---|---|
| `test_fetch_kodiko_live.py` | kodiko.gr | Fetch AK_592 returns ≥ 200 chars of Greek text |
| `test_fetch_et_gr_live.py` | et.gr | PDF download returns valid PDF bytes |
| `test_sha256_manifest.py` | All fetchers | Re-verify all articles in manifest; flag sha256 mismatches as `[LAW-AMENDED]` |

Run with: `uv run pytest scripts/tests/integration/ -v --live`

### 9.3 Knowledge Base Lint Tests

| Check | What it enforces |
|---|---|
| Required frontmatter fields | Every `.md` in `docs/knowledge/` has `title`, `jurisdiction` (or `scope: global`), `source`, `last_verified` |
| No case-specific content | Regex scan for "George", "YESTAY", "VIAMAR", "Elliniko", "CH1", "CC1", "SA-31" — fail if found |
| Broken source links | All `source:` URLs return HTTP 200 (or documented as subscription-only) |

Run with: `uv run python scripts/tools/lint_knowledge.py`

---

## 10. Guardrails

### 10.1 Fetch Guardrails (enforced in `BaseFetcher`)

| Guardrail | Mechanism | Failure output |
|---|---|---|
| **Non-empty text** | `fetch()` raises if returned text < 50 chars | Calling facade catches → tries next source |
| **Trusted source only** | `BaseFetcher.__init__` checks URL against `jurisdiction.yaml:trusted_source_whitelist` | Raises `ValueError` — not silently skipped |
| **`[UNVERIFIED]` tag on all-source failure** | Facade wraps total failure in `[UNVERIFIED — all sources failed: {article_id}]` | Placeholder written to `.md`; SHA256 manifest marks as `needs-manual` |
| **No training-memory fill** | `BaseFetcher.fetch()` must either return fetched text or raise — no `return` of a synthesised string | Enforced by code review + type annotation `-> str` (no `| None`) |
| **`[GAZETTE-PENDING]` when PDF unavailable** | `EtGrFetcher` writes tag when PDF 404 | Logged to `FETCH_LOG.json`; session brief queues for human resolution |

### 10.2 Settings Guardrails

| Guardrail | Mechanism |
|---|---|
| **Unknown source_id in override** | `load_settings()` validates every entry in user's `source_priority` against `jurisdiction.yaml:primary_authoritative_sources + fallback_sources`; unknown entries raise `ValueError` with clear message |
| **Missing jurisdiction** | No settings file + no `--country` flag → defaults to `"greece"` (MVP); logs a warning |
| **Source not registered** | If user's `source_priority` includes a source that has no registered fetcher → warning, not error; skipped silently |

### 10.3 CI Guardrails

| Check | When | Action on failure |
|---|---|---|
| SHA256 manifest verify | Weekly scheduled CI | Flag mismatches as `[LAW-AMENDED]`; open GitHub issue |
| Knowledge base lint | Every PR touching `docs/knowledge/` | Block merge |
| Unit tests | Every PR | Block merge |
| `jurisdiction.yaml` schema | Every PR touching `law-packs/*/jurisdiction.yaml` | Block merge |

---

## 11. Requirements Coverage

Source: `yestay/docs/specs/AI-LEGAL-HARNESS-REQUIREMENTS.md` (129 requirements across 14 categories).

This design covers the **scripts + knowledge base layer** (Layers 1+2 of the plugin). Requirements relating to case facts (T1/T2/T3), agent reasoning, human oversight, and strategy are addressed by skills (Layer 1 skills) and the case repo (Layer 3) — out of scope for this spec.

| REQ Category | Coverage | Notes |
|---|---|---|
| **REQ-02 Law Authority & Citation** (10 reqs) | **Partial** | REQ-02-001 SOLAR: scripts enforce verbatim-text-only fetch, never synthesised. REQ-02-002 hot/cold vault: `law-packs/greece/` = hot vault, `pdfs/` = cold vault. REQ-02-003 temporal versioning: `effective_date` + `operative_until` in article frontmatter — partial. REQ-02-005 fallback chain: facade source priority loop. **REQ-02-010 jurisdiction config**: `jurisdiction.yaml` fully implements the schema. Gap: REQ-02-004 citation linter not yet in scripts. |
| **REQ-03 Retrieval Strategy** (8 reqs) | **Covered** | Facade + registry + country self-registration implements the modular retrieval strategy. Source whitelist enforcement covers trusted-source-only retrieval. |
| **REQ-05 Verification Gates** (10 reqs) | **Partial** | SHA256 manifest + `verify` command covers source verification. Citation linter (REQ-02-004) not in scope for this task — flagged as gap. |
| **REQ-01 Fact Integrity** (10 reqs) | **Not in scope** | Layer 3 (case repo). T1/T2/T3 separation is the case repo's responsibility. |
| **REQ-04 Agent Behavior** (13 reqs) | **Not in scope** | Skills layer. SOLAR pre-loading, CREAC structure, DA dispatch — implemented in skills. |
| **REQ-06 Evidence Preservation** (9 reqs) | **Not in scope** | Layer 3 (case repo). SHA-256 + RFC 3161 timestamps apply to case evidence, not statute text. |
| **REQ-07 Human Oversight** (9 reqs) | **Not in scope** | Skills layer. |
| **REQ-08 Forum Sequencing** (8 reqs) | **Covered by existing T8-T10** | `law-packs/greece/forums.yaml` already implemented. |
| **REQ-09–14** | **Not in scope** | Strategy, memory, OSINT, AI tooling, language — skills layer. |

**Key gap identified:** REQ-02-004 (citation format linter) and REQ-02-003 (full operative-date-range checking per event date) are not in the current scripts design. These should be tracked as future tasks (T12+).

---

## 12. Deliverables Summary

| # | Deliverable | Description |
|---|---|---|
| S1 | `scripts/pyproject.toml` | UV project with all dependencies + test deps (pytest) |
| S2 | `scripts/laws.py` | Fire CLI public API |
| S3 | `scripts/core/` | base, registry, facade, settings (4 files) |
| S4 | `scripts/shared/` | EurLexFetcher, NLexFetcher |
| S5 | `scripts/greece/` | 4 fetcher implementations (constants.py removed — see J1) |
| S6 | `scripts/tests/` | Unit + integration + lint tests |
| S7 | `scripts/tools/lint_knowledge.py` | Knowledge base linter (frontmatter + case-content scan) |
| S8 | `commands/lex-harness-setup.md` | `/lex-harness:setup` — runs `uv sync` via `${CLAUDE_PLUGIN_ROOT}` |
| S9 | `commands/lex-harness-fetch.md` | `/lex-harness:fetch [id]` — invokes `laws.py fetch` via plugin root |
| J1 | `law-packs/greece/jurisdiction.yaml` | Jurisdiction config object (REQ-02-010); replaces constants.py |
| K1 | `docs/knowledge/README.md` | Knowledge base index |
| K2 | `docs/knowledge/LEGAL_AI_FRAMEWORK.md` | Ported, stripped |
| K3 | `docs/knowledge/greece/CORPUS_MAP.md` | Ported, stripped |
| K4 | `docs/knowledge/greece/COURT_AUTHORITY.md` | Ported, stripped |
| K5 | `docs/knowledge/greece/LAW_SOURCES.md` | Ported, stripped |
| K6 | `docs/knowledge/greece/sources/` (9 files) | Ported from 12_greek_legal_databases/ |
| K7 | `docs/knowledge/greece/modules/consumer_protection.md` | Ported, stripped |
| R1 | `docs/knowledge/REQUIREMENTS.md` | 129 requirements ported from yestay (stripped of case refs) |
| C1 | CLAUDE.md update | Add uv sync guard + knowledge base pointers + jurisdiction.yaml note |
