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

## 8. Deliverables Summary

| # | Deliverable | Description |
|---|---|---|
| S1 | `scripts/pyproject.toml` | UV project with all dependencies |
| S2 | `scripts/laws.py` | Fire CLI public API |
| S3 | `scripts/core/` | base, registry, facade, settings (4 files) |
| S4 | `scripts/shared/` | EurLexFetcher, NLexFetcher |
| S5 | `scripts/greece/` | constants + 4 fetcher implementations |
| S6 | `commands/lex-harness-setup.md` | `/lex-harness:setup` — runs `uv sync` via `${CLAUDE_PLUGIN_ROOT}` |
| S7 | `commands/lex-harness-fetch.md` | `/lex-harness:fetch [id]` — invokes `laws.py fetch` via plugin root |
| K1 | `docs/knowledge/README.md` | Knowledge base index |
| K2 | `docs/knowledge/LEGAL_AI_FRAMEWORK.md` | Ported, stripped |
| K3 | `docs/knowledge/greece/CORPUS_MAP.md` | Ported, stripped |
| K4 | `docs/knowledge/greece/COURT_AUTHORITY.md` | Ported, stripped |
| K5 | `docs/knowledge/greece/LAW_SOURCES.md` | Ported, stripped |
| K6 | `docs/knowledge/greece/sources/` (9 files) | Ported from 12_greek_legal_databases/ |
| K7 | `docs/knowledge/greece/modules/consumer_protection.md` | Ported, stripped |
| C1 | CLAUDE.md update | Add uv sync guard + knowledge base pointers |
