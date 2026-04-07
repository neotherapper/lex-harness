---
document_type: design-spec
feature_name: lex-harness — Open-source AI Legal Harness Plugin
version: 1.0
created_date: 2026-04-07
status: draft
supersedes:
  - docs/superpowers/specs/2026-04-06-ai-harness-unified-design.md  # pivot from yestay-local harness to public plugin
  - docs/superpowers/plans/2026-04-07-harness-mvp-wave.md            # replaced by lex-harness v0.1 plan
parent_specs:
  - docs/specs/AI-LEGAL-HARNESS-REQUIREMENTS.md     # the 14 REQs still apply to plugin content
  - docs/architecture/skill-ecosystem.md            # skill composition rules
---

# lex-harness — Plugin Design Spec

> **Purpose.** Design spec for `lex-harness`, an open-source Claude Code plugin (also distributed for Codex and Gemini CLI) that packages the AI legal harness as reusable infrastructure. Greek civil law is the MVP jurisdiction; the architecture supports community contributions for any country.
>
> **Audience.** Future sessions building the plugin, contributors adding jurisdiction packs, and the yestay repo (which becomes the first consumer).

---

## 1. Goal (restated)

> *"A framework any lawyer or informed claimant can drop into a new legal dispute and have an AI system that reasons correctly, cites accurately, and never corrupts the facts. It is very important to emphasize the strategy part — be able to extract information, pressure for data, push other party to make mistakes. The OSINT/research part enhances counter arguments and is case-by-case reasoning. As simple and effective as it can be, not over-engineered."*

Pivot from round 5: instead of shipping the harness inside yestay, ship it as a **public Claude Code plugin** (`lex-harness`) that yestay — and anyone else — consumes. The harness "engine" becomes reusable infrastructure; yestay becomes the reference case.

---

## 2. The 3-Layer Architecture

The single most important decision in this design.

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1: PLUGIN CORE — jurisdiction-AGNOSTIC                      │
│ skills/  commands/  templates/  docs/  schemas/                   │
│ The harness "engine" — identical for every country, every case    │
│ Repo: github.com/neotherapper/lex-harness (MIT)                          │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 2: LAW PACKS — jurisdiction-SPECIFIC, case-AGNOSTIC         │
│ law-packs/greece/   law-packs/germany/   law-packs/france/        │
│ Statutes + case law + forum rules + procedural templates +        │
│ foundational legal concepts (per country)                         │
│ Greek pack = MVP. Other packs = community contributions.          │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 3: CASE REPO — CASE-SPECIFIC                                │
│ 01_case_summary/  02_contracts/  06_claims_and_defenses/  ...     │
│ Facts (PFs), charges, evidence, drafts, settlement numbers        │
│ Lives in YOUR repo (e.g., yestay)                                 │
└──────────────────────────────────────────────────────────────────┘
```

**The plugin ships Layers 1 + 2.** Layer 3 is the user's case repo.

### What goes where

| Item | Layer | Rationale |
|---|---|---|
| 4 skill SKILL.md files (jurisdiction-agnostic bodies) | 1 | Reasoning is universal; inputs come from 2 + 3 |
| `verify-gate.md` 9-stage workflow | 1 | Gate logic is universal |
| `atomic-decomposition.md` workflow | 1 | Compound-argument decomposition is universal |
| `strategy-reasoning.md` 1-page checklist | 1 | Decision-tree shape is universal |
| Footer block schema (4 fields) | 1 | Format is universal; content is per-case |
| PROVEN_FACTS_REGISTER schema header + Categories A–H + P + T + N | 1 | Categories are universal |
| Git pre-commit hook (T1 isolation via Co-Authored-By trailer) | 1 | Mechanism is universal |
| Case-repo folder templates (01_case_summary/, 02_contracts/, …) | 1 | Structure is universal |
| 22 Greek core articles (AK, KPolD, Syntagma) | **2** | Greek-specific statute text |
| 8 Greek modules (tenancy, tax_invoices, corporate, …) | **2** | Greek-specific module bodies |
| ΑΠ inline case law summaries | **2** | Greek case law |
| Forum rules (Art. 52 KPolD blocks civil if criminal first) | **2** | Greek procedural rule |
| Phase 3 demand letter Greek template | **2** | Greek language + civil law conventions |
| 10 Greek foundational concepts (αοριστία, παραγραφή, …) | **2** | Greek legal terminology |
| Consumer Ombudsman complaint template | **2** | Greek forum |
| Greek playbook of common plays | **2** | Greek jurisdiction-specific plays |
| Specific PF codes (PF-A29 etc.) | **3** | Yestay's facts |
| CH1-CH5 / CC1-CC6 / SA-31 content | **3** | Yestay's case content |
| DL-01 = 2026-06-07 deadline | **3** | Yestay's specific deadline |
| Drafted Phase 3 letter output | **3** | Yestay's specific output |

---

## 3. Strategy: Universal Reasoning + Jurisdiction Rules + Case Content

Is strategy universal or country-specific? **Both** — split across the 3 layers:

| Aspect | Layer | Example |
|---|---|---|
| **Reasoning workflow** ("frame → list candidates → apply gates → rank → recommend ONE") | 1 | `skills/legal-strategy/references/strategy-reasoning.md` |
| **Decision principles** ("Information First, Attack Second"; "dropped arguments stay dropped"; "criminal last"; "absence is evidence") | 1 | Documented in skill body |
| **Settlement economics math** (ZOPA, BATNA, expected value) | 1 | `skills/legal-strategy/references/settlement-math.md` |
| **Forum types catalog** (civil / ombudsman / regulator / criminal — abstract) | 1 | Concept in skill body |
| **Forum sequencing rules** (Art. 52 KPolD blocks civil if criminal first — Greek) | 2 | `law-packs/greece/forums.yaml` |
| **Limitation periods catalog** (Art. 602 ΑΚ = 6 months for rental — Greek) | 2 | `law-packs/greece/limitation_periods.yaml` |
| **Forum templates** (Consumer Ombudsman complaint structure — Greek format) | 2 | `law-packs/greece/templates/` |
| **Common plays for this jurisdiction** (50 Greek plays) | 2 | `law-packs/greece/playbook.yaml` |
| **THIS case's specific arguments** (SA-31 systematic bad faith for Yestay) | 3 | `<case-repo>/07_strategy/SA31_*.md` |
| **THIS case's settlement number** (€1,500–€2,960 ZOPA) | 3 | `<case-repo>/07_strategy/core/SETTLEMENT_ECONOMICS.md` |

**One** `legal-strategy` skill, **one** universal reasoning workflow. The skill loads jurisdiction rules from the active law pack at runtime and case content from the case repo. A future Germany pack ships `law-packs/germany/forums.yaml` with German rules — same skill, different data.

**We do NOT need a separate "strategy" skill.** `legal-strategy` IS the strategy skill.

---

## 4. Plugin Structure (canonical, per plugin-dev skill)

```
lex-harness/                               # root of github.com/neotherapper/lex-harness
├── .claude-plugin/
│   └── plugin.json                        # Claude Code manifest
├── .codex-plugin/
│   └── plugin.json                        # Codex manifest (v0.3)
├── gemini-extension.json                  # Gemini manifest (v0.3)
├── CLAUDE.md                              # Claude Code context file
├── GEMINI.md                              # Gemini CLI context file (v0.3)
├── AGENTS.md                              # Codex / generic context file (v0.3)
├── README.md
├── LICENSE                                # MIT
├── CHANGELOG.md
├── CONTRIBUTING.md                        # how to add a law pack
│
├── skills/                                # LAYER 1 — jurisdiction-agnostic
│   ├── legal-strategy/
│   │   ├── SKILL.md                       # frontmatter description ≤1024 chars (Codex hard limit)
│   │   └── references/
│   │       ├── knowledge-vault.md         # SOLAR + verbatim retrieval workflow
│   │       ├── strategy-reasoning.md      # 1-page checklist
│   │       ├── verify-gate.md             # 9-stage consolidated gate
│   │       ├── atomic-decomposition.md    # compound argument → element rows
│   │       ├── settlement-math.md         # ZOPA / BATNA / expected value
│   │       └── mcp-tools-guide.md         # how to use recommended MCPs
│   ├── osint-investigation/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── chain-of-custody.md
│   ├── document-production/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── mad-judges.md              # v0.3 — dispatch pattern
│   └── devil-advocate/
│       ├── SKILL.md
│       └── references/
│           └── isolation-rule.md
│
├── commands/                              # LAYER 1 — 3 commands at v0.1
│   ├── init.md                            # /lex-harness:init <jurisdiction>
│   ├── fact.md                            # /lex-harness:fact (append to PENDING_FACTS)
│   └── devil.md                           # /lex-harness:devil <argument-id>
│
├── templates/                             # LAYER 1 — scaffolded into case repos by /init
│   ├── case_skeleton/                     # 01_case_summary through 09_ai_research
│   │   ├── 01_case_summary/README.md
│   │   ├── 02_contracts/README.md
│   │   ├── ...
│   │   └── 09_ai_research/README.md
│   ├── PROVEN_FACTS_REGISTER.md           # schema header only, no entries
│   ├── PENDING_FACTS.md                   # empty queue
│   ├── DEADLINE_REGISTER.md               # empty register
│   ├── CLAUDE.md                          # case-agnostic project instructions
│   └── pre-commit                         # T1 write-path isolation git hook
│
├── law-packs/                             # LAYER 2 — jurisdiction monorepo
│   ├── _schema.md                         # pack contract (what a pack MUST have)
│   ├── README.md                          # how to contribute a pack
│   └── greece/                            # MVP
│       ├── pack.json                      # {name, version, language, mcp_servers[], modules[]}
│       ├── MODULE_INDEX.md                # routing table (task → modules)
│       ├── forums.yaml                    # forum rules + preconditions
│       ├── limitation_periods.yaml        # statutory deadlines
│       ├── playbook.yaml                  # common plays
│       ├── glossary.md                    # Greek legal terms + EN translations
│       ├── foundational_concepts/         # 10 plain-language concept files
│       │   ├── default_judgment.md
│       │   ├── limitation_period.md
│       │   └── ... (8 more)
│       ├── core/                          # 22 always-loaded Greek articles
│       │   ├── AK_173.md .. Syntagma_25.md
│       │   └── _sha256_manifest.txt
│       ├── modules/
│       │   ├── tenancy/                   # 8 articles + inline case law
│       │   ├── consumer_protection/
│       │   ├── gdpr/
│       │   ├── tort_damages/
│       │   ├── corporate/
│       │   ├── tax_invoices/
│       │   ├── criminal_regulatory/
│       │   └── procedure_eirinodikio/
│       ├── case_law/
│       │   ├── ap/                        # ~28 ΑΠ decisions (cold tier)
│       │   ├── lower_courts/
│       │   ├── hdpa/
│       │   └── cjeu/
│       └── templates/                     # Greek-language draft templates
│           ├── phase3_civil_demand.md
│           ├── consumer_ombudsman_complaint.md
│           └── hdpa_complaint.md
│
├── hooks/                                 # v0.2 — deferred
│   └── hooks.json                         # SessionStart, PreCommit
│
├── .mcp.json                              # v0.2 — recommended MCP servers
├── scripts/
│   └── validate-pack.sh                   # CI helper: lint a law pack against _schema
├── tests/
│   ├── greece/                            # smoke tests for Greek pack
│   │   └── load_pack.test.md
│   ├── plugin_structure.test.md
│   └── README.md
└── docs/
    ├── ARCHITECTURE.md                    # 3 pillars + memory matrix + fact isolation
    ├── JURISDICTION_PACK_SPEC.md          # formal pack contract
    ├── PLUGIN_REQUIREMENTS.md             # PR-01..PR-10 (§7 below)
    ├── ROADMAP.md                         # v0.1 / v0.2 / v0.3 / v0.4+
    └── SECURITY.md                        # trust model + excludeTools list
```

### `.claude-plugin/plugin.json`

```json
{
  "name": "lex-harness",
  "version": "0.1.0",
  "description": "Open-source AI legal harness for civil disputes. Verbatim citations, fact integrity, devil's advocate review, jurisdiction-aware law packs. Ships with Greek law pack; extensible to any country.",
  "author": {
    "name": "Georgios Pilitsoglou",
    "url": "https://github.com/neotherapper"
  },
  "homepage": "https://github.com/neotherapper/lex-harness#readme",
  "repository": "https://github.com/neotherapper/lex-harness",
  "license": "MIT",
  "keywords": [
    "legal",
    "law",
    "litigation",
    "civil-dispute",
    "greek-law",
    "harness",
    "devils-advocate",
    "citation-verification",
    "jurisdiction-aware"
  ]
}
```

**Path rules:**
- Manifest MUST live at `.claude-plugin/plugin.json`
- Everything else (`commands/`, `skills/`, `hooks/`, `templates/`) at plugin root
- Intra-plugin paths use `${CLAUDE_PLUGIN_ROOT}` env var — never hardcoded absolute paths
- All file/directory names kebab-case

---

## 5. The 4 Skills (trigger specs)

Per nikai finding #2: **description is the trigger, body is lazy-loaded.** Codex enforces ≤1024 chars on the description. Rewrite all 4 skill descriptions as dense trigger specs, not summaries.

### 5.1 `skills/legal-strategy/SKILL.md`

```yaml
---
name: legal-strategy
version: "4.0"
description: >-
  Use when working on any civil legal dispute — drafting demand letters
  (εξώδικο), formal complaints, αγωγή, counterclaims, HDPA/GDPR filings,
  consumer ombudsman complaints, settlement negotiations, strategy decisions
  on what to do next, analysing opposing-party responses, choosing which
  legal play to deploy, citing Greek civil code articles (ΑΚ, ΚΠολΔ),
  computing limitation periods (παραγραφή), assessing argument vulnerability,
  or reasoning about when to pressure the other side. Loads the active
  jurisdiction's law pack from law-packs/<jurisdiction>/ and reads the
  case repo's 07_strategy/ + 06_claims_and_defenses/ + DECISION_LOG for
  context. Runs VERIFY gate before any formal output.
writes_to:
  - "<case-repo>/CURRENT_STATUS.md"
  - "<case-repo>/06_claims_and_defenses/PENDING_FACTS.md"
  - "<case-repo>/07_strategy/core/DECISION_LOG.md"
  - "<case-repo>/09_ai_research/research_queue.md"
reads_from:
  - "<case-repo>/01_case_summary/CASE_OVERVIEW.md"
  - "<case-repo>/06_claims_and_defenses/"
  - "<case-repo>/07_strategy/"
  - "${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/"
  - "${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/"
handoff_to:
  - document-production
  - devil-advocate
---
```

Body loads only on match. Body references `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/*.md` for the 9-stage verify-gate, atomic decomposition, knowledge vault, strategy reasoning, and settlement math workflows.

### 5.2 `skills/osint-investigation/SKILL.md`

```yaml
---
name: osint-investigation
version: "1.1"
description: >-
  Use when collecting public evidence (OSINT) for a legal case, preserving
  web content before it disappears, capturing witness statements into
  04_evidence/testimony/, grading evidence admissibility (Admiralty A1-F5),
  producing OSINT Finding Reports (OFR), investigating corporate records
  (ΓΕΜΗ, AADE), preserving screenshots with SHA-256 + RFC3161 timestamps,
  or building the chain of custody for documentary evidence before filing.
  Also captures first-party testimony (non-OSINT) with the same chain of
  custody discipline. Proposes facts to PENDING_FACTS.md — never writes
  PROVEN_FACTS_REGISTER directly.
writes_to:
  - "<case-repo>/04_evidence/osint/"
  - "<case-repo>/04_evidence/testimony/"
  - "<case-repo>/04_evidence/CHAIN_OF_CUSTODY.log"
  - "<case-repo>/06_claims_and_defenses/PENDING_FACTS.md"
reads_from:
  - "<case-repo>/01_case_summary/CASE_OVERVIEW.md"
  - "${CLAUDE_PLUGIN_ROOT}/skills/osint-investigation/references/"
handoff_to:
  - legal-strategy  # promotes facts back to strategy
---
```

### 5.3 `skills/document-production/SKILL.md`

```yaml
---
name: document-production
version: "1.0"
description: >-
  Use when producing any formal legal document that will leave the case
  workspace — Phase 3 demand letters, αγωγή, HDPA complaints, consumer
  ombudsman filings, criminal referrals, formal email responses, settlement
  proposals. Loads templates from the active law pack, runs the 9-stage
  verify-gate before release, enforces the mandatory draft footer block
  (pf_ids, law_articles, evidence_items, da_review_refs), dispatches
  devil-advocate per high-risk element. OWNS writes to 08_drafts/. Never
  releases a draft that fails the gate. Never paraphrases statutes in the
  legal basis section.
writes_to:
  - "<case-repo>/08_drafts/"
reads_from:
  - "<case-repo>/06_claims_and_defenses/"
  - "<case-repo>/07_strategy/"
  - "<case-repo>/04_evidence/"
  - "${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/templates/"
  - "${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/verify-gate.md"
handoff_to:
  - devil-advocate
---
```

### 5.4 `skills/devil-advocate/SKILL.md`

```yaml
---
name: devil-advocate
version: "1.0"
description: >-
  Use when adversarially reviewing a strategic argument, claim, or compound
  argument element (CH/CC/SA files, or specific elements of them). MUST be
  dispatched as a fresh subagent with NO inherited session context — only
  the raw argument text, the verbatim facts, the cited statutes, and the
  forum + stakes. The isolation is the whole point: a session-aware DA
  collapses to sycophantic agreement. Refuses with [ISOLATION-BREACH] if
  it detects strategy memos, prior DA reviews, or case theory in its
  dispatch payload. Outputs a per-argument DA review file with
  counter-arguments rated HIGH/MEDIUM/LOW + holes in the factual chain +
  verdict (SOUND/NEEDS-WORK/DROP).
writes_to:
  - "<case-repo>/07_strategy/da_reviews/"
reads_from: []
handoff_to: []
---
```

**All 4 descriptions are <1024 chars.** Trigger vocabulary mixes Greek + English legal jargon the user actually types.

**Description anti-pattern reminder:** do NOT summarize workflow in descriptions. Describe *when to trigger*, not *what it does*. (From writing-skills meta-skill + nikai finding.)

---

## 6. The 3 Slash Commands (v0.1)

### 6.1 `commands/init.md`

```markdown
---
description: Scaffold a new legal case repo with the active jurisdiction's law pack, folder structure, git hooks, and initial metadata.
---

Usage: `/lex-harness:init <jurisdiction>`

Example: `/lex-harness:init greece`

Actions:
1. Confirm target directory (CWD) is empty or prompt
2. Copy `${CLAUDE_PLUGIN_ROOT}/templates/case_skeleton/` into CWD
3. Copy `${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/` into `<cwd>/05_legal_research/law_pack/`
4. Copy `${CLAUDE_PLUGIN_ROOT}/templates/pre-commit` into `<cwd>/.githooks/pre-commit`; set `core.hooksPath`
5. Prompt for case metadata: claimant, opposing party, deposit/claim amount, key dates
6. Populate `01_case_summary/CASE_OVERVIEW.md` from answers
7. Compute limitation deadline from the jurisdiction's limitation_periods.yaml; append to DEADLINE_REGISTER.md as DL-01
8. Commit the scaffolded repo (human commit — no AI trailer so the git hook allows it)
9. Print next-steps message pointing at `/lex-harness:fact` and the legal-strategy skill

Reentrant: re-running with `--update-pack` refreshes `05_legal_research/law_pack/` from the plugin without destroying case content.
```

### 6.2 `commands/fact.md`

```markdown
---
description: Append a proposed fact to PENDING_FACTS.md with correct schema (category, source, text, status). Human promotes to PROVEN_FACTS_REGISTER in a separate commit.
---

Usage: `/lex-harness:fact`

Actions:
1. Prompt for category (A–H, P, T, N)
2. Prompt for source file or URL
3. Prompt for fact text (one factual claim)
4. Generate next PF ID (read PROVEN_FACTS_REGISTER + PENDING_FACTS, increment)
5. Append formatted YAML entry to `06_claims_and_defenses/PENDING_FACTS.md`
6. Print reminder: "Propose only. Human reviews and promotes in a separate commit WITHOUT Co-Authored-By: Claude trailer."
```

### 6.3 `commands/devil.md`

```markdown
---
description: Dispatch devil-advocate skill on a specific argument (CH/CC/SA file or element). Runs in isolated subagent context with only raw facts + cited law + argument text. No session state inheritance.
---

Usage: `/lex-harness:devil <argument-id>`

Examples:
- `/lex-harness:devil SA-31`
- `/lex-harness:devil SA-31-E01`
- `/lex-harness:devil CC3`

Actions:
1. Locate the argument file in `07_strategy/` or `06_claims_and_defenses/`
2. Extract the argument text + referenced PF IDs + cited law articles
3. Fetch verbatim text for each cited law from the active law pack
4. Build isolation payload: {argument, facts, laws, forum}
5. Dispatch devil-advocate skill via Task tool with isolation payload
6. Save result to `07_strategy/da_reviews/DA_<argument-id>_<YYYY-MM-DD>.md`
7. Update `<case-repo>/07_strategy/core/DECISION_LOG.md` with DA outcome
```

TOML versions (`.toml` with `{{args}}` placeholders) ship in v0.3 for Codex + Gemini parity.

---

## 7. Plugin Requirements (PR-01 through PR-10)

Like the harness has REQ-01..REQ-14, the plugin has its own requirements. These govern plugin-level discipline, not legal content discipline.

| # | Requirement | Severity |
|---|---|---|
| **PR-01** | **Strict layer separation.** Plugin code (Layer 1) MUST NOT reference any country name, statute ID, or case detail. Layer 2 (law packs) MUST NOT reference any case detail. Layer 3 (case repo) is the only place case content lives. CI grep check enforces this. | CRITICAL |
| **PR-02** | **Law pack contract.** Every country pack ships a `pack.json` matching `docs/JURISDICTION_PACK_SPEC.md` schema. Required fields: `name`, `version`, `language`, `modules[]`, `mcp_servers[]`, `forum_rules_file`, `limitation_periods_file`, `playbook_file`. The plugin REFUSES to load a pack that fails schema validation (exit non-zero). | CRITICAL |
| **PR-03** | **Jurisdiction-agnostic skill bodies.** No skill SKILL.md or reference file may contain statute IDs, country names, or procedural terms hardcoded in the skill body. All such content lives in the active law pack. CI grep check enforces this. | CRITICAL |
| **PR-04** | **Reentrant `/init`.** Re-running `/lex-harness:init <jurisdiction>` MUST NOT destroy existing case content. It refreshes the law pack in `05_legal_research/law_pack/` and creates missing templates. Detects existing `01_case_summary/CASE_OVERVIEW.md` and prompts before overwriting. | HIGH |
| **PR-05** | **Semver + backward compat.** Major version bumps (0.x → 1.x, 1.x → 2.x) REQUIRE an explicit migration note in CHANGELOG.md. Minor versions (0.1 → 0.2) MUST NOT break existing case repos. Patch versions (0.1.0 → 0.1.1) MUST NOT break anything. Tested against a pinned yestay snapshot in CI. | HIGH |
| **PR-06** | **Greek MVP test coverage.** Every Greek law module ships with at least one smoke test that verifies: the module loads, articles parse, case_law_inline lists the expected ΑΠ decisions, and the pack.json validates against schema. CI runs these on every PR. | HIGH |
| **PR-07** | **Contribution path documented.** `CONTRIBUTING.md` walks through "how to add a country pack" in ≤10 steps. `docs/JURISDICTION_PACK_SPEC.md` is the formal contract. New country PRs auto-fail if `pack.json` doesn't validate or schema grep check fails. | MEDIUM |
| **PR-08** | **MIT license + DCO sign-off.** All contributions MIT-licensed. Every commit must carry Developer Certificate of Origin sign-off (`Signed-off-by: ...`). No CLA. Automated DCO check on PRs. | MEDIUM |
| **PR-09** | **Plugin works without case repo.** A user can install the plugin and inspect skill behavior without having a case repo at all — skills respond with "no case detected — run /lex-harness:init" rather than crashing. | MEDIUM |
| **PR-10** | **No hidden state.** All plugin behavior is determined by files in the plugin or the case repo. No environment variables required (${CLAUDE_PLUGIN_ROOT} is set automatically by Claude Code), no global config in `~/.config/`, no hidden caches. Reproducible by reading the file tree. | HIGH |
| **PR-11** | **All external tools are OPTIONAL.** The plugin ships with ZERO mandatory external dependencies beyond Claude Code itself. Chrome DevTools MCP, Neo4j, ChromaDB, Dikaio.ai, any MCP server — all optional. Every workflow that CAN use an external tool MUST also have a documented fallback path (e.g., manual web fetch instead of Chrome MCP, markdown-only instead of Neo4j, inline case law summaries instead of ChromaDB). Graceful degradation is required, not a nice-to-have. | CRITICAL |
| **PR-12** | **Tool detection + graceful degradation.** Every skill that references an optional tool MUST: (a) check for tool availability before use, (b) fall back to the manual/offline path if unavailable, (c) log the degradation as `[TOOL-UNAVAILABLE:<tool-name>]` in the session brief so the user knows. Never crash, never block a workflow, never require installation mid-session. | CRITICAL |
| **PR-13** | **Documented fallback matrix.** `docs/TOOL_OPTIONALITY.md` ships a table mapping every referenced tool to its fallback: Chrome MCP → manual fetch + paste, Neo4j → markdown PROVEN_FACTS only, ChromaDB → inline case law summaries in module files, Dikaio.ai → manual verification via kodiko.gr + note in draft, EUR-Lex MCP → manual fetch. User can build the entire harness with ZERO MCPs installed — the full-power path is an opt-in upgrade. | HIGH |
| **PR-14** | **Install path completeness.** A user can install the plugin and run `/lex-harness:init greece` with ONLY Claude Code installed — no other software. The `/init` command does not prompt for or require any external tool. If advanced tools are beneficial, the README's "Optional tools for advanced workflows" section documents them with one-sentence reasons. | HIGH |
| **PR-15** | **Skill descriptions must declare optional dependencies.** Every skill SKILL.md frontmatter MAY declare `optional_tools:` — a list of external tools that enhance the skill but are NOT required. Users inspecting the skill can see at a glance what's optional and what (if anything) is required. | MEDIUM |

---

## 7a. Gherkin Scenarios — What a User Actually Experiences

These are the user-experience scenarios the plugin MUST satisfy to be considered done. They drive the acceptance tests + documentation + README examples. Every scenario has an observable outcome.

### Actor: First-time user (new case, no legal background)

```gherkin
Feature: Install the plugin and start a new case in 60 seconds

  Scenario: User installs lex-harness and initialises a Greek civil case
    Given the user has Claude Code installed
    And the user has no external MCP servers installed
    When the user runs "/plugin install lex-harness@neotherapper-marketplace"
    And the user navigates to an empty directory
    And the user runs "/lex-harness:init greece"
    Then the plugin scaffolds the full case folder structure (01_case_summary through 09_ai_research)
    And the plugin copies law-packs/greece/ into 05_legal_research/law_pack/
    And the plugin installs the git pre-commit hook for T1 write-path isolation
    And the plugin prompts for case metadata (parties, amounts, key dates)
    And the plugin populates 01_case_summary/CASE_OVERVIEW.md from the answers
    And the plugin creates DEADLINE_REGISTER.md with the statutory limitation as DL-01
    And the plugin prints a "next steps" message pointing at the legal-strategy skill
    And the entire workflow completes in under 60 seconds
    And ZERO external tools were required (no Chrome MCP, no Neo4j, no ChromaDB)

  Scenario: User adds a fact they found in an old email
    Given an initialised Greek case repo
    When the user runs "/lex-harness:fact"
    Then the plugin prompts for category (A–H, P, T, N)
    And the plugin prompts for source (file path or URL)
    And the plugin prompts for the fact text
    And the plugin generates the next PF ID (e.g. PF-C47)
    And the plugin appends a formatted YAML entry to 06_claims_and_defenses/PENDING_FACTS.md
    And the plugin prints "Propose only. Human reviews and promotes in a separate commit WITHOUT Co-Authored-By: Claude trailer."
    And the git pre-commit hook does NOT block this AI commit (because PENDING_FACTS.md is a queue, not T1)
```

**Readiness:** `MUST`

```gherkin
Feature: Evidence capture works with OR without Chrome MCP (PR-11)

  Scenario: User preserves a web page WITHOUT Chrome MCP installed
    Given the user has NO Chrome DevTools MCP installed
    And the user wants to preserve a Google Maps review URL as evidence
    When the user asks the legal-strategy skill to capture the URL
    Then the skill detects Chrome MCP is unavailable
    And the skill logs "[TOOL-UNAVAILABLE:chrome-devtools-mcp]" in the session brief
    And the skill falls back to manual WebFetch (or prompts the user to paste the page content)
    And the skill computes sha256 of the captured content
    And the skill writes the evidence to 04_evidence/osint/<slug>_<date>.md with chain-of-custody metadata
    And the workflow completes successfully

  Scenario: User preserves a web page WITH Chrome MCP installed (upgrade path)
    Given the user has Chrome DevTools MCP installed
    When the user asks the legal-strategy skill to capture the same URL
    Then the skill uses Chrome DevTools MCP (navigate_page, take_snapshot, take_screenshot)
    And the skill captures a full-fidelity snapshot including JS-rendered content
    And the skill writes the evidence with the same schema as the manual path
    And both paths produce files that satisfy the chain-of-custody requirements
```

**Readiness:** `MUST`

```gherkin
Feature: User brainstorms next strategic play

  Scenario: George asks "what should I do next?"
    Given an initialised Greek case repo with some facts + charges + strategic arguments
    When the user asks the legal-strategy skill "what's my next move?"
    Then the skill reads CURRENT_STATUS.md + DECISION_LOG.md + CASE_OVERVIEW.md
    And the skill consults law-packs/greece/playbook.yaml for candidate plays
    And the skill consults law-packs/greece/forums.yaml for forum preconditions
    And the skill applies the strategy-reasoning.md 1-page checklist
    And the skill filters plays by deadline pressure + readiness + forum precondition
    And the skill returns ONE recommended next play with one-paragraph rationale
    And the skill lists 2–3 alternatives considered but not recommended
    And the skill logs the recommendation to DECISION_LOG.md as a new DL-NN entry
    And the skill NEVER recommends a play that has a statutory_blocking precondition unmet
    And the skill NEVER recommends a dropped argument from DECISION_LOG
```

**Readiness:** `MUST`

```gherkin
Feature: User drafts a formal demand letter

  Scenario: User drafts a Phase 3 demand letter for a compound argument
    Given an initialised Greek case repo with SA-31 (15-element bad faith pattern)
    When the user asks document-production to draft a Phase 3 demand letter for SA-31
    Then the skill invokes atomic-decomposition.md workflow to produce 15 element rows
    And the skill dispatches devil-advocate in isolated subagent mode for each element
    And the skill loads law-packs/greece/templates/phase3_civil_demand.md template
    And the skill populates the template placeholders from the element decomposition
    And the skill loads verbatim Greek text for every cited article from the active law pack
    And the skill runs verify-gate.md (9 stages)
    And Stage 3b catches any article cited outside its actual holding
    And the skill appends the mandatory 4-field footer block (pf_ids, law_articles, evidence_items, da_review_refs)
    And the skill saves to 08_drafts/phase3_demand_SA31_<date>.md
    And a human reviewer can trace any 5 random PF codes to source in ≤2 minutes
```

**Readiness:** `MUST`

```gherkin
Feature: User wants devil-advocate review of an argument

  Scenario: User runs /lex-harness:devil on SA-31
    Given an initialised case repo with 07_strategy/SA31_SYSTEMATIC_BAD_FAITH.md
    When the user runs "/lex-harness:devil SA-31"
    Then the command reads the SA-31 file + extracts the 15 elements
    And the command fetches verbatim text for each cited article from the law pack
    And the command builds an isolation payload: {argument, facts, laws, forum}
    And the command dispatches devil-advocate via Task tool with the payload
    And devil-advocate refuses to run if it detects strategy memos or case theory in the payload (ISOLATION-BREACH)
    And devil-advocate produces a DA review file with ≥3 counter-arguments rated HIGH/MEDIUM/LOW
    And devil-advocate identifies holes in the factual chain
    And devil-advocate emits a verdict (SOUND / NEEDS-WORK / DROP) with 2–3 sentence rationale
    And the result is saved to 07_strategy/da_reviews/DA_SA31_<date>.md
    And the DECISION_LOG.md is updated with the DA outcome
```

**Readiness:** `MUST`

### Actor: Returning user (existing case)

```gherkin
Feature: Session resume for an existing case

  Scenario: User opens Claude Code in their case repo after a week
    Given an initialised Greek case repo with existing facts + charges + strategic arguments
    And the legal-strategy skill is available via the installed plugin
    When the user starts a new Claude Code session
    Then the legal-strategy skill auto-triggers on any case-related prompt
    And the skill reads CURRENT_STATUS.md + DECISION_LOG.md + CASE_OVERVIEW.md
    And the skill reads law-packs/greece/MODULE_INDEX.md for the routing table
    And the skill reads DEADLINE_REGISTER.md for days-remaining warnings
    And the skill produces a session brief: phase, last action, critical deadlines, ONE next action
    And the skill warns if any Art. 602-style limitation period is within 60 days
```

**Readiness:** `MUST`

```gherkin
Feature: Plugin updates don't break the case (PR-05 backward compat)

  Scenario: User runs /lex-harness:init --update-pack after a plugin upgrade
    Given a case repo initialised with lex-harness v0.1.0
    And the user has upgraded the plugin to v0.2.0
    When the user runs "/lex-harness:init greece --update-pack"
    Then the plugin refreshes 05_legal_research/law_pack/ from law-packs/greece/
    And the plugin DOES NOT touch any case content (01-04, 06-09 directories)
    And the plugin DOES NOT overwrite CASE_OVERVIEW.md
    And the plugin logs all changes to CHANGELOG.md (append-only)
    And any references to moved / renamed law pack files are flagged [REQUIRES-REVIEW]
    And the workflow is safe to run blindly — re-running it twice is idempotent
```

**Readiness:** `MUST`

### Actor: Contributor (adding a new country pack)

```gherkin
Feature: Developer contributes a new country pack (PR-07)

  Scenario: Developer adds a France law pack
    Given the developer has forked github.com/neotherapper/lex-harness
    When the developer creates law-packs/france/pack.json matching the schema in docs/JURISDICTION_PACK_SPEC.md
    And the developer populates law-packs/france/core/ with French civil code articles
    And the developer creates law-packs/france/modules/ with at least one module
    And the developer creates law-packs/france/forums.yaml with French civil courts
    And the developer runs "./scripts/validate-pack.sh france"
    Then the validator confirms pack.json matches schema
    And the validator confirms all required files exist
    And the validator confirms no French-specific content leaked into skills/ (layer separation)
    And the developer opens a PR
    And CI runs the validator + grep check for PR-01 layer separation
    And CI passes
    And the PR is reviewed and merged
    And the next plugin release ships France as an available jurisdiction
```

**Readiness:** `SHOULD` (not required for v0.1 but must be documented)

### Actor: Retained lawyer reviewing the case

```gherkin
Feature: Lawyer verifies a citation chain in 2 minutes (REQ-07-004)

  Scenario: Lawyer picks 5 random PF codes from a Phase 3 letter footer
    Given a Phase 3 demand letter draft in 08_drafts/
    And the draft has a footer block listing pf_ids, law_articles, evidence_items, da_review_refs
    When the lawyer picks 5 random PF codes from the footer
    Then each PF resolves to an entry in 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md in ≤10 seconds
    And each entry has a source field pointing to a real file or URL
    And the lawyer can navigate to the source and verify the fact in ≤30 seconds
    And the full trace for 5 PFs completes in ≤2 minutes total
    And the lawyer does not need AI assistance to complete the trace
```

**Readiness:** `MUST`

### Actor: AI Agent (the skills themselves)

```gherkin
Feature: Skills degrade gracefully when optional tools unavailable (PR-11, PR-12)

  Scenario: legal-strategy skill runs with zero MCPs installed
    Given the user has NO external MCPs installed (no Chrome, no Neo4j, no ChromaDB, no Dikaio)
    When the user asks legal-strategy to draft a demand letter
    Then the skill completes the task using only:
      - markdown files in the case repo
      - markdown files in ${CLAUDE_PLUGIN_ROOT}/law-packs/greece/
      - Claude Code's native WebFetch for any external URL lookups
      - Manual Dikaio.ai verification (user copies/pastes to the website)
    And the session brief logs "[TOOL-UNAVAILABLE:neo4j]" "[TOOL-UNAVAILABLE:chromadb]" "[TOOL-UNAVAILABLE:dikaio-ai]"
    And the draft is produced with the same quality gates (verify-gate stages still run)
    And the only difference from the full-power path is: manual Dikaio verification step in the footer

  Scenario: legal-strategy skill runs with ALL MCPs installed (full-power path)
    Given the user has Chrome DevTools MCP + Neo4j MCP + ChromaDB + Dikaio.ai MCP installed
    When the user asks legal-strategy to draft the same demand letter
    Then the skill uses Neo4j for fact traversal queries
    And the skill uses ChromaDB for semantic case-law lookup
    And the skill uses Dikaio.ai MCP for automated citation verification
    And the skill uses Chrome DevTools for live web evidence capture
    And the draft is produced faster and with automated verification
    And the output draft is functionally EQUIVALENT to the zero-MCP path (same schema, same footer, same gate checks)
```

**Readiness:** `MUST` (PR-11 + PR-12 compliance)

```gherkin
Feature: AI agent never pollutes T1 facts (PR-01 layer separation + D19 write-path isolation)

  Scenario: AI agent tries to edit PROVEN_FACTS_REGISTER.md directly
    Given an initialised case repo
    And the AI agent has generated a new fact it believes should be added
    When the AI agent stages a commit touching 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
    And the commit message contains "Co-Authored-By: Claude"
    Then the git pre-commit hook rejects the commit with [T1-WRITE-VIOLATION]
    And the hook prints: "AI must propose new facts via PENDING_FACTS.md for human review"
    And the AI agent appends the proposed fact to 06_claims_and_defenses/PENDING_FACTS.md instead
    And a separate human commit (no AI trailer) later promotes the fact to PROVEN_FACTS_REGISTER.md
```

**Readiness:** `MUST`

### Coverage summary

| Scenario | Actor | Readiness | PR reference |
|---|---|---|---|
| Install + init in 60s with zero external tools | First-time user | MUST | PR-11, PR-14 |
| Add a fact via /lex-harness:fact | First-time user | MUST | D19, D30 |
| Evidence capture without Chrome MCP | First-time user | MUST | PR-11, PR-12 |
| Evidence capture with Chrome MCP (upgrade) | First-time user | MUST | PR-13 |
| Brainstorm next strategic play | First-time user | MUST | PR-01 (universal reasoning) |
| Draft Phase 3 demand letter | First-time user | MUST | REQ-05-001, PR-01 |
| Run devil-advocate via /lex-harness:devil | First-time user | MUST | D17 (isolation) |
| Session resume after a week | Returning user | MUST | REQ-04-012 |
| Plugin update is backward-compatible | Returning user | MUST | PR-04, PR-05 |
| Add a new country pack | Contributor | SHOULD | PR-02, PR-07 |
| Lawyer 2-min trace | Lawyer | MUST | REQ-07-004 |
| Skill runs with zero MCPs | AI Agent | MUST | PR-11, PR-12 |
| Skill runs with all MCPs (full power) | AI Agent | MUST | PR-13 |
| T1 write-path isolation enforced | AI Agent | MUST | D19, D30 |

---

## 8. Differentiation from Existing Community Skills

Nikai finding #3: two community legal skills already exist on GitHub. Differentiation is critical for adoption.

| Project | Scope | Jurisdiction | Gap we fill |
|---|---|---|---|
| `evolsb/claude-legal-skill` | Contract review (CUAD-grounded, 41 risk categories, NDA/indemnification/termination) | **US-only** (hardcoded) | No dispute/litigation workflow; no jurisdiction packs; US-specific |
| `zubair-trabzada/ai-legal-claude` | 14 skills + 5 agents for broad legal AI workflows | **US-centric** | No fact-integrity discipline; no verify-gate; no jurisdiction extensibility |
| **`lex-harness`** (us) | **Dispute / litigation** + **jurisdiction-aware law packs** + **devil's advocate** + **fact write-path isolation** | **Greek MVP**, extensible | Our differentiation |

**Our angle:** litigation-ready + jurisdiction-extensible. Nobody else ships law packs. The devil-advocate isolation rule is genuinely novel.

---

## 9. Multi-CLI Strategy (v0.1 → v0.3)

Nikai finding #1: SKILL.md is an open cross-platform standard. Plugin manifests are CLI-specific wrappers around the same skills directory.

| Version | CLIs | Strategy |
|---|---|---|
| **v0.1** | Claude Code only | Ship `.claude-plugin/plugin.json` + `skills/` + `commands/` (markdown). Greek MVP. Yestay is the first consumer. |
| **v0.2** | Claude Code + hooks | Add `hooks/hooks.json` (SessionStart — auto-load CASE_OVERVIEW; PreToolUse — block AI writes to PROVEN_FACTS_REGISTER via plugin instead of case-repo hook). Add `.mcp.json` with recommended Greek MCP servers (`greek-law-mcp`, `eur-lex-mcp`, `cerebra-legal-mcp`). |
| **v0.3** | + Codex + Gemini | Add `.codex-plugin/plugin.json` + `gemini-extension.json` + `AGENTS.md` + `GEMINI.md`. Convert `commands/*.md` → `commands/*.toml` with `{{args}}` for cross-CLI portability. Skills directory unchanged (SKILL.md is portable). |
| **v0.4+** | Community packs | Accept PRs for `law-packs/<country>/`. First candidates: Germany, France, UK, US. |

---

## 10. How Yestay Consumes the Plugin

Yestay becomes the **first consumer** — eat dogfood from day 1.

1. After `lex-harness v0.1` ships, install in yestay: `/plugin install lex-harness@<local-dir>` (local dev) or `/plugin install lex-harness@<marketplace>` (once published)
2. Yestay's existing `.claude/skills/legal-strategy/` and `.claude/skills/osint-investigation/` get **deleted** — superseded by plugin versions
3. Yestay's current `05_legal_research/law_vault/` becomes a **checked-in snapshot** of `law-packs/greece/` (so case-specific edits stay visible in yestay's git history, but the canonical source is the plugin)
4. Yestay's `CLAUDE.md` gets a new top-level section: `## Plugin: lex-harness v0.1.0` noting pinned version
5. When the plugin updates, yestay runs `/lex-harness:init --update-pack` to refresh `law_vault/` from the plugin source
6. If yestay needs case-specific workflow (not jurisdiction-specific), it lives in yestay only — never PR'd upstream
7. If yestay discovers something jurisdiction-general (e.g., a new Greek forum rule), it gets PR'd UP to `lex-harness/law-packs/greece/`

**Risk:** yestay diverges from the plugin if local edits are made carelessly. **Mitigation:** yestay's pre-commit hook (still case-level) blocks edits to `05_legal_research/law_pack/*` — any change there must happen upstream in the plugin.

---

## 11. Roadmap

| Version | Scope | Blocker to next version |
|---|---|---|
| **v0.1.0** | Plugin scaffold + 4 skills + 3 commands + Greek law pack (22 core + 3 modules: tenancy, tax_invoices, corporate) + MIT LICENSE + README + PR-01..PR-10 docs | Yestay installs it + successfully produces one Phase 3 demand letter end-to-end |
| **v0.2.0** | Hooks (SessionStart context loader, pre-commit T1 isolation via plugin), `.mcp.json` with recommended Greek MCP deps, more Greek modules (gdpr, consumer_protection, tort_damages, procedure_eirinodikio), 10 foundational concepts | Second real case (hypothetical or real) tests the `/init` reentrance + pack update flow |
| **v0.3.0** | Multi-CLI parity: `.codex-plugin/plugin.json` + `gemini-extension.json` + TOML commands + AGENTS.md + GEMINI.md | Successful install + skill invocation on all 3 CLIs (Claude Code + Codex + Gemini) |
| **v0.4.0+** | Community country packs (Germany, France, UK, US as first targets). ChromaDB case-law indexing as plugin-managed tool (deferred from yestay MVP). MAD-Judges reference workflow for high-stakes docs. | Open-ended — community-driven |

---

## 12. Security + Trust Model

Per nikai finding on security (5 risks from the Claude Code plugin ecosystem):

| Risk | Mitigation |
|---|---|
| Skill content trust | All skills reviewed in PRs; main branch protected; DCO sign-off required |
| MCP server trust | `.mcp.json` ships recommended servers as OPTIONAL; users explicitly enable. Document each server's maintainer + scope in `docs/SECURITY.md` |
| API key exposure | Plugin ships NO secrets. Keys live in user's env or case repo `.env` (gitignored). `docs/SECURITY.md` documents required env vars per MCP |
| Prompt injection via MCP | Verify-gate Stage 3b (holding characterisation) catches misgrounded outputs regardless of source. DA isolation rule catches sycophantic responses |
| Global vs project scope | Plugin declares all paths relative to `${CLAUDE_PLUGIN_ROOT}` or `<case-repo>`. No `~/.config/` writes, no global state |

v0.2 adds `excludeTools` configuration (Gemini pattern) to block destructive shell commands inside the plugin scope.

---

## 13. Decision Log

| # | Decision | Rationale |
|---|----------|-----------|
| PD1 | 3-layer architecture (plugin core / law packs / case repo) | Only model that supports multi-jurisdiction + multi-case cleanly; prevents case content bleeding into plugin |
| PD2 | Single `legal-strategy` skill, not multiple per-strategy skills | Strategy REASONING is universal; country + case data are inputs. One skill, three data sources |
| PD3 | 4 skills: legal-strategy, osint-investigation, document-production, devil-advocate | Round 5 simplification from 7 → 4. No new skills in plugin pivot. |
| PD4 | Greek MVP first, community packs later | Eat-your-own-dogfood: yestay validates the law-pack architecture before opening to contributors |
| PD5 | MIT license + DCO, no CLA | Lowest contribution friction; standard OSS pattern |
| PD6 | Claude Code v0.1, multi-CLI v0.3 | Ship value fast; multi-CLI is nice-to-have not must-have |
| PD7 | `lex-harness` as the plugin name | Short, descriptive (lex = law), slash commands read cleanly (`/lex-harness:init`) |
| PD8 | Repo at `~/Developer/projects/lex-harness` (separate sibling) | Cleanest separation from yestay during development; simplest mental model |
| PD9 | No custom MCP server in v0.1 | Existing MCPs (`greek-law-mcp`, `eur-lex-mcp`, `cerebra-legal-mcp`) cover the need. Build our own only if differentiated value emerges |
| PD10 | Ship tests/ with manual I/O pairs, not automated skill framework | Nikai confirmed skills are probabilistic; no deterministic test framework exists yet. Manual smoke tests are the state of the art |
| PD11 | `templates/case_skeleton/` in plugin, not in law pack | Folder structure (01_case_summary/, …) is universal across jurisdictions. Only content differs. |
| PD12 | `/init` is reentrant with `--update-pack` flag | Users must be able to update the law pack without rebuilding their case repo |
| PD13 | Repo on personal GitHub `neotherapper/lex-harness` | Personal account, not work account, for open-source ownership |
| PD14 | All external tools are OPTIONAL (PR-11 through PR-15) | User must be able to install the plugin and use the harness with zero external MCPs, zero Neo4j, zero ChromaDB, zero Chrome. Full-power tools are an opt-in upgrade, never a requirement. |
| PD15 | Gherkin scenarios drive acceptance tests (§7a) | Every user-facing scenario has an observable outcome. §7a is the test harness for v0.1 completion. |
| PD16 | Dual-path workflows (tool-available + tool-unavailable) are mandatory for every external-tool integration | PR-11 compliance requires documented fallback. Both paths produce functionally equivalent outputs — the with-tool path is faster, the without-tool path is manual. |

---

## 14. Cross-Reference Map

| If you need… | Read… |
|---|---|
| The 14 harness requirements | `docs/specs/AI-LEGAL-HARNESS-REQUIREMENTS.md` + `docs/specs/requirements/REQ-XX-*.md` (yestay) |
| Plugin requirements PR-01..PR-10 | §7 of this doc + `<plugin>/docs/PLUGIN_REQUIREMENTS.md` |
| Skill ecosystem architecture | `docs/architecture/skill-ecosystem.md` (yestay) + `<plugin>/docs/ARCHITECTURE.md` |
| Law pack contract | `<plugin>/docs/JURISDICTION_PACK_SPEC.md` + `<plugin>/law-packs/_schema.md` |
| Official Claude Code plugin docs | https://code.claude.com/docs/en/plugins + https://code.claude.com/docs/en/plugins-reference |
| Nikai skill/plugin research | `nikai/knowledge/ai-tools/coding-assistants/claude-code-skills-mcp-setup-guide.md` (canonical SKILL.md anatomy) + `nikai/knowledge/ai-tools/coding-assistants/openai-codex-cli-plugins-guide.md` + `nikai/knowledge/ai-tools/coding-assistants/gemini-cli-extensions-guide.md` |
| Greek MCP servers | `nikai/knowledge/ai-tools/mcp/servers/greek-law-mcp.md` + `eur-lex-mcp.md` + `cerebra-legal-mcp.md` |
| Existing community legal skills (differentiation) | `nikai/knowledge/ai-tools/coding-assistants/claude-legal-skill.md` + `nikai/knowledge/verticals/legaltech/legalzoom-claude-connector.md` |
| Yestay unified harness spec (superseded) | `docs/superpowers/specs/2026-04-06-ai-harness-unified-design.md` |
| Legal corpus map (Greek content source) | `09_ai_research/LEGAL_CORPUS_MAP.md` (yestay) — this is where law pack content comes from |

---

## 15. Out of Scope (WON'T for v0.1)

| Item | Why deferred |
|---|---|
| Multi-CLI manifests (Codex, Gemini) | v0.3 — ship Claude Code working first |
| SessionStart hooks | v0.2 — requires CASE_OVERVIEW auto-loading convention |
| Recommended MCP servers in `.mcp.json` | v0.2 — ship manually configurable first |
| Per-element LRS + MAD-Judges | v0.4+ — Polish wave from yestay spec |
| ChromaDB case-law indexing | v0.4+ — need ≥30 precedents in Greek pack |
| Non-Greek law packs | v0.4+ — community contributions |
| Custom MCP server (legal-vault-server) | Never (use existing community servers) |
| Voice/video evidence intake | Never (out of harness scope) |
| AI legal advice for the public | Never (not a SaaS; single-user single-case tool) |
| E-filing integration | Never (filing done by retained lawyer) |

---

## 16. Definition of Done for v0.1

**The plugin is "done" when:**

1. Repo exists at `github.com/neotherapper/lex-harness` with MIT LICENSE and README
2. `.claude-plugin/plugin.json` validates against Claude Code plugin schema
3. All 4 skills load without error in Claude Code (`claude --plugin-dir ./lex-harness`)
4. All 3 commands appear in `/lex-harness:*` autocomplete
5. `/lex-harness:init greece` scaffolds a complete case skeleton in an empty directory (tested by instantiating into `/tmp/test-case/`)
6. `/lex-harness:fact` appends a valid entry to `PENDING_FACTS.md`
7. `/lex-harness:devil SA-31` dispatches devil-advocate and produces a DA review file
8. Greek law pack has 22 core articles + 3 modules (tenancy, tax_invoices, corporate), all with verbatim text + sha256
9. CI grep check passes (no country names / statute IDs in `skills/`)
10. Yestay successfully installs the plugin and produces one Phase 3 demand letter end-to-end
11. Draft footer block contains PF codes, law articles, evidence items, DA review refs — all resolvable
12. The zero-MCP scenario in §7a ("legal-strategy skill runs with zero MCPs installed") passes end-to-end on a fresh install — user has ONLY Claude Code, no other software, and can still produce a Phase 3 demand letter via manual fallback paths
13. `docs/TOOL_OPTIONALITY.md` exists and documents every external tool + its fallback
14. Repo is live at `github.com/neotherapper/lex-harness` with MIT LICENSE + README + CONTRIBUTING.md

---

**Status:** draft. Awaiting George's review before transitioning to writing-plans for the `lex-harness v0.1` implementation plan.
