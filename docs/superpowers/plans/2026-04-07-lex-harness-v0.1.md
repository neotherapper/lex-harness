# lex-harness v0.1 Implementation Plan (Plan A)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `lex-harness v0.1.0` — a public Claude Code plugin on `github.com/neotherapper/lex-harness` containing 4 jurisdiction-agnostic skills, 3 slash commands, a Greek law pack (22 core articles + 3 modules), templates, git pre-commit hook, Codex bootstrap script, MIT license. Yestay can install it after release (Plan B).

**Architecture:** New repo at `~/Developer/projects/lex-harness`. Three layers per the design spec: plugin core (skills/commands/templates) is jurisdiction-agnostic; `law-packs/greece/` is jurisdiction-specific; case repos are layer 3. All external tools (Chrome MCP, Neo4j, ChromaDB, Dikaio.ai) are OPTIONAL — every workflow has a documented fallback. No new Python — markdown + 2 bash scripts + 1 git hook.

**Tech Stack:** Markdown (everything), YAML frontmatter, JSON manifest, bash (git hook + Codex bootstrap), git pre-commit hook. NO Python. NO MCP servers in v0.1. Tested manually via Claude Code `claude --plugin-dir` flag.

**Source design doc:** `~/Developer/projects/yestay/docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md`

**Source corpus map:** `~/Developer/projects/yestay/09_ai_research/LEGAL_CORPUS_MAP.md`

**Plan B (depends on this):** `~/Developer/projects/yestay/docs/superpowers/plans/2026-04-07-yestay-adopts-lex-harness.md` (installs the released plugin in yestay)

---

## Pre-flight checks

```bash
ls ~/Developer/projects/lex-harness 2>&1
```

Expected: `No such file or directory`. If it exists, stop and ask George.

```bash
gh auth status
```

Expected: authenticated as `neotherapper` (or whichever account George uses). If not, run `gh auth login` first.

```bash
ls ~/Developer/projects/yestay/docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md
ls ~/Developer/projects/yestay/09_ai_research/LEGAL_CORPUS_MAP.md
```

Expected: both exist.

---

## File structure

This is the canonical layout the plan creates. Every task references files relative to `~/Developer/projects/lex-harness/`.

```
lex-harness/
├── .claude-plugin/
│   └── plugin.json                               # T2
├── .gitignore                                    # T1
├── README.md                                     # T3
├── LICENSE                                       # T3 (MIT)
├── CHANGELOG.md                                  # T3
├── CONTRIBUTING.md                               # T3
├── CODE_OF_CONDUCT.md                            # T3
│
├── skills/
│   ├── legal-strategy/
│   │   ├── SKILL.md                              # T11
│   │   └── references/
│   │       ├── knowledge-vault.md                # T12
│   │       ├── strategy-reasoning.md             # T13
│   │       ├── verify-gate.md                    # T14
│   │       ├── atomic-decomposition.md           # T15
│   │       └── settlement-math.md                # T13 (inline as 1-pager)
│   ├── osint-investigation/
│   │   ├── SKILL.md                              # T16
│   │   └── references/
│   │       └── chain-of-custody.md               # T16
│   ├── document-production/
│   │   ├── SKILL.md                              # T17
│   │   └── references/
│   │       └── footer-block-schema.md            # T17
│   └── devil-advocate/
│       ├── SKILL.md                              # T18
│       └── references/
│           └── isolation-rule.md                 # T18
│
├── commands/
│   ├── init.md                                   # T19
│   ├── fact.md                                   # T20
│   └── devil.md                                  # T21
│
├── templates/
│   ├── case_skeleton/                            # T22
│   │   ├── 01_case_summary/README.md
│   │   ├── 02_contracts/README.md
│   │   ├── 03_correspondence/README.md
│   │   ├── 04_evidence/README.md
│   │   ├── 04_evidence/testimony/README.md
│   │   ├── 05_legal_research/README.md
│   │   ├── 06_claims_and_defenses/README.md
│   │   ├── 07_strategy/README.md
│   │   ├── 08_drafts/README.md
│   │   └── 09_ai_research/README.md
│   ├── PROVEN_FACTS_REGISTER.md                  # T23
│   ├── PENDING_FACTS.md                          # T23
│   ├── DEADLINE_REGISTER.md                      # T24
│   ├── CURRENT_STATUS.md                         # T24
│   ├── CLAUDE.md                                 # T25
│   ├── pre-commit                                # T26
│   ├── footer_block.md                           # T17
│   └── phase3_civil_demand_skeleton.md           # T27 (jurisdiction-agnostic skeleton; Greek text in law-pack)
│
├── law-packs/
│   ├── _schema.md                                # T4
│   ├── README.md                                 # T4
│   └── greece/
│       ├── pack.json                             # T5
│       ├── MODULE_INDEX.md                       # T6
│       ├── forums.yaml                           # T7
│       ├── limitation_periods.yaml               # T7
│       ├── playbook.yaml                         # T7
│       ├── glossary.md                           # T7
│       ├── core/                                 # T8 + T9 (22 articles)
│       │   └── AK_*.md, KPolD_*.md, Syntagma_25.md
│       ├── modules/
│       │   ├── tenancy/                          # T10
│       │   ├── tax_invoices/                     # T28
│       │   └── corporate/                        # T29
│       └── templates/
│           └── phase3_civil_demand.md            # T27 (Greek instantiation)
│
├── scripts/
│   ├── install-githooks.sh                       # T26
│   ├── bootstrap-codex-skills.sh                 # T30
│   └── validate-pack.sh                          # T31 (CI helper)
│
├── tests/
│   ├── README.md                                 # T32
│   ├── greece/
│   │   └── load_pack.test.md                     # T32
│   └── plugin_structure.test.md                  # T32
│
├── docs/
│   ├── ARCHITECTURE.md                           # T33
│   ├── JURISDICTION_PACK_SPEC.md                 # T4 (formal contract)
│   ├── PLUGIN_REQUIREMENTS.md                    # T34 (PR-01..PR-15)
│   ├── TOOL_OPTIONALITY.md                       # T35 (PR-13 fallback matrix)
│   ├── ROADMAP.md                                # T34
│   └── SECURITY.md                               # T35
│
└── .github/
    ├── workflows/
    │   └── validate-pack.yml                     # T36 (CI)
    ├── ISSUE_TEMPLATE/
    │   ├── bug_report.md                         # T36
    │   └── new_country_pack.md                   # T36
    └── PULL_REQUEST_TEMPLATE.md                  # T36
```

---

## Build order (3 waves)

**Wave 1 — Repo + plugin scaffold (T1–T6):** init the repo, plugin.json, README + LICENSE, law pack contract, Greek pack.json, MODULE_INDEX.

**Wave 2 — Greek law pack content (T7–T10, T28–T29):** forums + limitation + playbook + glossary, 22 core articles, 3 modules.

**Wave 3 — Plugin functionality (T11–T31):** skills (legal-strategy, osint-investigation, document-production, devil-advocate), commands (init, fact, devil), templates (case_skeleton, PROVEN_FACTS, DEADLINE_REGISTER, CLAUDE.md, pre-commit hook, footer block, demand letter skeleton), bootstrap scripts.

**Wave 4 — Tests + docs + CI + release (T32–T37):** smoke tests, ARCHITECTURE.md, PR docs, GitHub workflow, v0.1.0 tag + GitHub release.

Total: 37 tasks. ~5–7 days focused work. All markdown + 3 bash scripts + 1 git hook + 1 GitHub workflow.

---

## Task 0: Read the design spec + corpus map

**Files:** none (read-only)

- [ ] **Step 1: Read the design spec**

Read `/Users/georgiospilitsoglou/Developer/projects/yestay/docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md` in full. Pay attention to:
- §2 3-Layer Architecture (what goes where)
- §3 Strategy split (universal reasoning + jurisdiction rules + case content)
- §4 Plugin Structure (canonical layout)
- §5 The 4 skills (trigger spec descriptions ≤1024 chars)
- §6 The 3 slash commands
- §7 PR-01 through PR-15 (plugin requirements)
- §7a Gherkin scenarios (15 scenarios — these are the acceptance tests)
- §13 Decision log PD1–PD16

- [ ] **Step 2: Read the corpus map**

Read `/Users/georgiospilitsoglou/Developer/projects/yestay/09_ai_research/LEGAL_CORPUS_MAP.md` in full. This is the source of truth for the 22 core articles + 3 MVP modules (tenancy, tax_invoices, corporate). Note the source URLs (kodiko.gr, lawspot.gr, search.et.gr, areiospagos.gr).

- [ ] **Step 3: Read the existing legal-strategy skill in yestay**

Read `/Users/georgiospilitsoglou/Developer/projects/yestay/.claude/skills/legal-strategy/SKILL.md` (top 200 lines) and `/Users/georgiospilitsoglou/Developer/projects/yestay/.claude/skills/osint-investigation/SKILL.md` (top 200 lines). These are the existing skills that get ported into the plugin. Note their existing structure but DO NOT copy verbatim — the plugin versions must be jurisdiction-agnostic per PR-01 + PR-03.

- [ ] **Step 4: Verify the expected directory does not yet exist**

```bash
ls ~/Developer/projects/lex-harness 2>&1
```

Expected: `No such file or directory`. If it exists, STOP and ask George before proceeding.

---

## Task 1: Create the repo + .gitignore

**Files:**
- Create: `~/Developer/projects/lex-harness/.gitignore`
- Create: `~/Developer/projects/lex-harness/` (the directory itself)

- [ ] **Step 1: Create the directory and initialise git**

```bash
mkdir -p ~/Developer/projects/lex-harness
cd ~/Developer/projects/lex-harness
git init -b main
```

Expected: `Initialized empty Git repository in /Users/georgiospilitsoglou/Developer/projects/lex-harness/.git/`

- [ ] **Step 2: Configure git user (verify it's the personal account)**

```bash
git config user.name "Georgios Pilitsoglou"
git config user.email "<your-personal-email>"
git config user.name && git config user.email
```

Replace `<your-personal-email>` with the personal email tied to the `neotherapper` GitHub account. Verify both lines print after the second command.

- [ ] **Step 3: Write `.gitignore`**

```bash
cat > .gitignore <<'EOF'
# OS / editor
.DS_Store
*.swp
.idea/
.vscode/

# Test artefacts
tests/**/output/
tests/**/*.tmp

# Local plugin install symlinks (consumers create these per machine)
.claude/skills/
~/.codex/skills/

# Secrets — should never be committed
.env
.env.local
*.secret

# Build artefacts
node_modules/
dist/
EOF
```

- [ ] **Step 4: Stage and commit**

```bash
git add .gitignore
git commit -s -m "$(cat <<'EOF'
chore: initial commit — empty repo with .gitignore (T1)

Sets up the lex-harness repo at ~/Developer/projects/lex-harness.
Personal git config; .gitignore covers OS, editor, secrets, and
test output.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds.

---

## Task 2: Create plugin.json

**Files:**
- Create: `~/Developer/projects/lex-harness/.claude-plugin/plugin.json`

- [ ] **Step 1: Create the directory**

```bash
mkdir -p .claude-plugin
```

- [ ] **Step 2: Write plugin.json**

```bash
cat > .claude-plugin/plugin.json <<'EOF'
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
EOF
```

- [ ] **Step 3: Validate JSON**

```bash
python3 -c "import json; json.load(open('.claude-plugin/plugin.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 4: Verify required fields**

```bash
python3 <<'PY'
import json
m = json.load(open('.claude-plugin/plugin.json'))
required = ["name", "version", "description", "author", "license", "repository"]
missing = [k for k in required if k not in m]
assert not missing, f"missing fields: {missing}"
assert m["name"] == "lex-harness"
assert m["license"] == "MIT"
print("manifest OK")
PY
```

Expected: `manifest OK`

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/plugin.json
git commit -s -m "$(cat <<'EOF'
feat(plugin): add .claude-plugin/plugin.json (T2)

Plugin manifest with name, version (0.1.0), description, author,
homepage, repository, MIT license, and keywords for marketplace
discovery. Validated against Claude Code plugin schema.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 3: README, LICENSE, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT

**Files:**
- Create: `~/Developer/projects/lex-harness/README.md`
- Create: `~/Developer/projects/lex-harness/LICENSE`
- Create: `~/Developer/projects/lex-harness/CHANGELOG.md`
- Create: `~/Developer/projects/lex-harness/CONTRIBUTING.md`
- Create: `~/Developer/projects/lex-harness/CODE_OF_CONDUCT.md`

- [ ] **Step 1: Write LICENSE (MIT)**

```bash
YEAR=$(date +%Y)
cat > LICENSE <<EOF
MIT License

Copyright (c) ${YEAR} Georgios Pilitsoglou

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

- [ ] **Step 2: Write README.md**

```bash
cat > README.md <<'EOF'
# lex-harness

> Open-source AI legal harness for civil disputes. Verbatim citations, fact integrity, devil's advocate review, jurisdiction-aware law packs. Ships with Greek law pack; extensible to any country.

**Status:** v0.1.0 — early MVP. Greek civil law (rental + consumer + corporate). Yestay is the reference case.

## What is this?

A Claude Code plugin that turns Claude into a disciplined legal research + drafting agent for civil disputes. It combines:

- **4 skills** that auto-trigger on legal tasks: `legal-strategy`, `osint-investigation`, `document-production`, `devil-advocate`
- **3 slash commands**: `/lex-harness:init`, `/lex-harness:fact`, `/lex-harness:devil`
- **Jurisdiction-aware law packs**: Greek MVP today; community contributions for any country
- **Fact write-path isolation** via a git pre-commit hook (AI cannot pollute T1 facts)
- **Verbatim citation gate**: every law citation must come from the loaded vault — no hallucinated statutes
- **Devil's advocate** in isolated subagent context: catches sycophantic reasoning before it ships

## Why?

LLMs hallucinate Greek law. The dominant failure mode is "real law applied to wrong context" (e.g., Art. 612A AK is spousal succession, not tenant damage). This plugin makes that mechanically impossible: the verify-gate refuses to emit a citation that didn't come from a vault file loaded in the current session. Every fact in your case has one write path (human) and many read paths (markdown, Neo4j, ChromaDB). AI agents propose facts to a queue; humans approve.

## Install (Claude Code)

```bash
# From the official marketplace (when published)
/plugin install lex-harness@<marketplace>

# From local directory (during development or self-hosting)
claude --plugin-dir /path/to/lex-harness
```

After installation, in any directory, run:

```
/lex-harness:init greece
```

This scaffolds a complete case repository with the Greek law pack, git hooks, and starter templates. Takes about 60 seconds.

## Optional tools

The plugin works with **zero external dependencies** beyond Claude Code itself. The following are OPTIONAL upgrades:

| Tool | What it adds | Without it |
|---|---|---|
| Chrome DevTools MCP | Live web evidence capture (JS-rendered pages) | Manual WebFetch / paste |
| Neo4j MCP | Multi-hop fact relationship queries | Markdown grep |
| ChromaDB | Semantic case-law search across volume | Inline summaries in module files |
| Dikaio.ai MCP | Automated Greek law citation verification | Manual verification via kodiko.gr |
| `greek-law-mcp` | 21,000+ Greek statutes as MCP | Vault articles only |
| `eur-lex-mcp` | EU law + CELEX retrieval | Manual EUR-Lex web fetch |

See `docs/TOOL_OPTIONALITY.md` for the full fallback matrix.

## Contributing a country pack

Greek civil law is the MVP. To add another jurisdiction (Germany, France, UK, US, etc.):

1. Read `docs/JURISDICTION_PACK_SPEC.md`
2. Fork this repo
3. Create `law-packs/<your-country>/` matching the schema
4. Run `./scripts/validate-pack.sh <your-country>` until it passes
5. Open a PR

Full walkthrough in `CONTRIBUTING.md`.

## Architecture

3 layers:

1. **Plugin core** (jurisdiction-agnostic) — skills, commands, templates, git hook, schemas
2. **Law packs** (jurisdiction-specific, case-agnostic) — `law-packs/greece/`, `law-packs/germany/`, …
3. **Case repo** (case-specific) — `01_case_summary/`, `02_contracts/`, etc. — lives in YOUR repo

The plugin ships layers 1 + 2. Your case repo is layer 3.

See `docs/ARCHITECTURE.md` for the full design.

## Differentiation

Other Claude legal skills exist (`evolsb/claude-legal-skill`, `zubair-trabzada/ai-legal-claude`) — they focus on US contract review (CUAD-grounded). lex-harness focuses on **dispute and litigation** with **jurisdiction-aware law packs**. Nobody else does packs.

## License

MIT. See LICENSE.

## Author

Georgios Pilitsoglou ([@neotherapper](https://github.com/neotherapper))

Built initially for [yestay](https://github.com/neotherapper/yestay) — a Greek rental deposit dispute — and extracted into a reusable plugin for others fighting civil disputes.
EOF
```

- [ ] **Step 3: Write CHANGELOG.md**

```bash
cat > CHANGELOG.md <<'EOF'
# Changelog

All notable changes to lex-harness will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] — 2026-04-07

### Added
- Initial plugin scaffold with `.claude-plugin/plugin.json`
- 4 skills: `legal-strategy`, `osint-investigation`, `document-production`, `devil-advocate`
- 3 slash commands: `/lex-harness:init`, `/lex-harness:fact`, `/lex-harness:devil`
- Greek law pack (`law-packs/greece/`) with 22 core articles + 3 modules (tenancy, tax_invoices, corporate)
- Templates for case skeleton, PROVEN_FACTS_REGISTER, PENDING_FACTS, DEADLINE_REGISTER, CLAUDE.md
- Git pre-commit hook for T1 write-path isolation (Co-Authored-By trailer detection)
- Codex skill bootstrap script
- Plugin requirements PR-01 through PR-15 (including tool-optionality discipline)
- Documentation: ARCHITECTURE, JURISDICTION_PACK_SPEC, PLUGIN_REQUIREMENTS, TOOL_OPTIONALITY, ROADMAP, SECURITY
- 15 Gherkin acceptance scenarios driving the test plan
- MIT LICENSE
- README, CONTRIBUTING, CODE_OF_CONDUCT
EOF
```

- [ ] **Step 4: Write CONTRIBUTING.md**

```bash
cat > CONTRIBUTING.md <<'EOF'
# Contributing to lex-harness

Thanks for your interest! This document explains how to contribute, especially how to add a new country's law pack.

## Quick links

- [Bug reports](https://github.com/neotherapper/lex-harness/issues/new?template=bug_report.md)
- [New country pack proposal](https://github.com/neotherapper/lex-harness/issues/new?template=new_country_pack.md)
- [Plugin requirements](docs/PLUGIN_REQUIREMENTS.md)
- [Jurisdiction pack contract](docs/JURISDICTION_PACK_SPEC.md)

## Adding a new country pack

The MVP supports Greece. To add another jurisdiction (e.g., Germany, France, UK, US):

### Step 1 — Read the contract

Read `docs/JURISDICTION_PACK_SPEC.md` thoroughly. It defines what files a pack MUST contain and what each one is responsible for.

### Step 2 — Fork + branch

```bash
gh repo fork neotherapper/lex-harness --clone
cd lex-harness
git checkout -b add-pack-<country>
```

### Step 3 — Create the pack directory

```bash
mkdir -p law-packs/<country>/{core,modules,case_law,templates,foundational_concepts}
```

### Step 4 — Write `pack.json`

Copy `law-packs/greece/pack.json` as a starting point and replace the country-specific values. Required fields: `name`, `version`, `language`, `default_modules`, `mcp_servers`, `forum_rules_file`, `limitation_periods_file`, `playbook_file`.

### Step 5 — Populate the pack

Minimum viable pack:

- `MODULE_INDEX.md` — task → modules routing table
- `forums.yaml` — forum precondition rules (statutory_blocking vs strategic_recommended)
- `limitation_periods.yaml` — statutory deadlines
- `playbook.yaml` — common plays for this jurisdiction
- `glossary.md` — legal terms in the local language + EN translation
- `core/*.md` — always-loaded statute articles (verbatim text + frontmatter)
- `modules/<module>/*.md` — task-specific module articles
- `templates/<doc-type>.md` — local-language draft templates

Each statute file MUST have frontmatter: `article_id`, `short_name`, `source_primary`, `source_verification`, `effective_date`, `repeal_date`, `sha256`, `translation_status`, `last_verified`.

### Step 6 — Validate

```bash
./scripts/validate-pack.sh <country>
```

Expected output: `✅ Pack <country> is valid`

If validation fails, the script prints exactly which file or field is missing.

### Step 7 — Open a PR

```bash
git add law-packs/<country>/
git commit -s -m "feat(pack): add <country> law pack (closes #<issue-number>)"
git push origin add-pack-<country>
gh pr create --title "Add <country> law pack" --body "..."
```

The `-s` flag adds a Developer Certificate of Origin sign-off, which is required by PR-08.

CI will run `validate-pack.sh` automatically. Once it passes and a maintainer reviews, the PR can be merged.

## DCO sign-off (PR-08)

All commits MUST be signed off with the Developer Certificate of Origin. Use `git commit -s` to add the sign-off line automatically. We do not require a CLA — DCO is sufficient.

## Layer separation rule (PR-01)

The most important rule: **plugin code (skills, commands, templates) MUST NOT contain country-specific content.** A skill that says "Art. 592 ΑΚ" is broken — that's Greek-specific and belongs in `law-packs/greece/modules/tenancy/AK_592.md`. The skill should reference articles by abstract concept ("the operative wear-and-tear exemption article") and let the active law pack provide the actual citation.

CI runs a grep check on every PR to enforce this. If your PR touches `skills/` and adds a country name, statute ID, or procedural term, CI will fail.

## Code of conduct

See `CODE_OF_CONDUCT.md`.

## Reporting bugs

Use the bug report template. Include: plugin version, OS, exact reproduction steps, expected vs. actual behavior, any error messages, and which optional tools (Chrome MCP, Neo4j, etc.) were enabled.
EOF
```

- [ ] **Step 5: Write CODE_OF_CONDUCT.md**

```bash
cat > CODE_OF_CONDUCT.md <<'EOF'
# Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/) version 2.1.

## Our standards

In short: be excellent to each other. Differences in opinion (especially about legal interpretation) are expected and welcome — disrespect, harassment, or personal attacks are not.

## Reporting

Report violations by emailing the maintainer ([@neotherapper](https://github.com/neotherapper)) or by opening a confidential issue on GitHub.

## Enforcement

The maintainer has full authority to remove comments, commits, code, issues, and other contributions that violate this Code of Conduct, and may ban temporarily or permanently any contributor for behavior they deem inappropriate.
EOF
```

- [ ] **Step 6: Verify all 5 files**

```bash
ls README.md LICENSE CHANGELOG.md CONTRIBUTING.md CODE_OF_CONDUCT.md
wc -l README.md LICENSE CHANGELOG.md CONTRIBUTING.md CODE_OF_CONDUCT.md
```

Expected: all 5 files listed; sizes roughly README ~80 lines, LICENSE ~21 lines, CHANGELOG ~25 lines, CONTRIBUTING ~100 lines, CODE_OF_CONDUCT ~15 lines.

- [ ] **Step 7: Commit**

```bash
git add README.md LICENSE CHANGELOG.md CONTRIBUTING.md CODE_OF_CONDUCT.md
git commit -s -m "$(cat <<'EOF'
docs: README, LICENSE (MIT), CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT (T3)

README explains what lex-harness is, how to install, optional tools,
contribution path, differentiation from existing community legal skills.

CONTRIBUTING walks through adding a country pack in 7 steps + DCO + the
PR-01 layer separation rule.

LICENSE is MIT. CODE_OF_CONDUCT references Contributor Covenant 2.1.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 4: Law pack contract (`law-packs/_schema.md` + `docs/JURISDICTION_PACK_SPEC.md`)

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/_schema.md`
- Create: `~/Developer/projects/lex-harness/law-packs/README.md`
- Create: `~/Developer/projects/lex-harness/docs/JURISDICTION_PACK_SPEC.md`

These define what a country pack MUST contain. PR-02 + PR-07 reference these as the formal contract.

- [ ] **Step 1: Create directories**

```bash
mkdir -p law-packs docs
```

- [ ] **Step 2: Write `law-packs/README.md`**

```bash
cat > law-packs/README.md <<'EOF'
# Law packs

This directory contains jurisdiction-specific law packs. Each subdirectory is one country.

## Available packs

| Country | Status | Pack |
|---|---|---|
| Greece | v0.1.0 (MVP) | [`greece/`](greece/) |

## Adding a country

See `../CONTRIBUTING.md` and `../docs/JURISDICTION_PACK_SPEC.md` for the full contract.

The minimum viable pack contains:
- `pack.json` (required, validates against the schema in `_schema.md`)
- `MODULE_INDEX.md` (routing table)
- `forums.yaml` (forum precondition rules)
- `limitation_periods.yaml` (statutory deadlines)
- `playbook.yaml` (common plays for this jurisdiction)
- `glossary.md` (legal terminology)
- `core/` directory with always-loaded statute files
- `modules/` directory with at least one task-specific module

Run `../scripts/validate-pack.sh <country>` to check a pack against the schema.
EOF
```

- [ ] **Step 3: Write `law-packs/_schema.md` (the contract documentation)**

```bash
cat > law-packs/_schema.md <<'EOF'
# Law pack schema

Every pack in `law-packs/<country>/` MUST satisfy this contract. The plugin REFUSES to load a pack that fails validation.

## Required files

```
law-packs/<country>/
├── pack.json                          REQUIRED
├── MODULE_INDEX.md                    REQUIRED
├── forums.yaml                        REQUIRED
├── limitation_periods.yaml            REQUIRED
├── playbook.yaml                      REQUIRED
├── glossary.md                        REQUIRED
├── core/                              REQUIRED (≥1 file)
│   └── <article-id>.md
├── modules/                           REQUIRED (≥1 subdirectory)
│   └── <module-name>/
│       └── <article-id>.md
└── templates/                         OPTIONAL
    └── <doc-type>.md
```

## `pack.json` schema

```json
{
  "name": "<country>",
  "version": "<semver>",
  "language": "<ISO 639-1 code, e.g. el, en, de, fr>",
  "country_code": "<ISO 3166-1 alpha-2, e.g. GR, DE, FR>",
  "default_modules": ["<module-name>", ...],
  "mcp_servers": [
    {"name": "<server-name>", "purpose": "<one-line>", "required": false}
  ],
  "forum_rules_file": "forums.yaml",
  "limitation_periods_file": "limitation_periods.yaml",
  "playbook_file": "playbook.yaml",
  "glossary_file": "glossary.md",
  "maintainer": {"name": "<name>", "url": "<github-or-website>"}
}
```

All listed MCP servers MUST have `required: false` (PR-11 — all external tools are optional).

## Statute file frontmatter

Every file in `core/` and `modules/<m>/` MUST have YAML frontmatter:

```yaml
---
article_id: <unique-id>             # e.g., AK_592, KPolD_338, BGB_535
short_name: "<one-line description>"
source_primary: <URL>               # official gazette / government source
source_verification: <URL>          # cross-verification source
effective_date: <YYYY-MM-DD>
repeal_date: <YYYY-MM-DD>           # null if still in force
sha256: <16-char hex prefix>        # of the verbatim text section
translation_status: el-only | en-translated | machine-translated
last_verified: <YYYY-MM-DD>
---
```

## `forums.yaml` schema

```yaml
forums:
  - id: <forum-id>                  # e.g., civil-court, consumer-ombudsman
    name: <human-readable name>
    precondition_type: none | strategic_recommended | statutory_blocking
    must_complete_first: [<other-forum-id>, ...]   # empty array if none
    notes: <free text>
```

The plugin uses this to enforce the forum precondition gate (statutory_blocking forums REFUSE drafts that lack the prerequisite).

## `limitation_periods.yaml` schema

```yaml
limitations:
  - id: <unique-id>
    description: <human-readable>
    statute: <article-id>           # references a file in core/ or modules/
    period_days: <integer>
    accrual_event: <description of when the clock starts>
    interruption_methods: [<method>, ...]
```

## `playbook.yaml` schema

```yaml
plays:
  - id: <unique-id>
    name: <short name>
    forum: <forum-id>
    description: <one paragraph>
    requires_state: <description or null>
    blocked_by: [<other-play-id>, ...]
    typical_cost: <free text or null>
    typical_duration: <free text or null>
```

## Validation

Run `./scripts/validate-pack.sh <country>` to check a pack. The script:

1. Confirms `pack.json` exists and validates against the schema above
2. Confirms all required files exist
3. Confirms each statute file has the required frontmatter
4. Confirms `forums.yaml`, `limitation_periods.yaml`, `playbook.yaml` parse as valid YAML
5. Confirms no plugin core files (skills/, commands/) reference country-specific terms (PR-01 grep check)

CI runs this on every PR.
EOF
```

- [ ] **Step 4: Write `docs/JURISDICTION_PACK_SPEC.md`**

```bash
cat > docs/JURISDICTION_PACK_SPEC.md <<'EOF'
# Jurisdiction Pack Specification

> Formal contract for `law-packs/<country>/` directories. Authoritative source for the plugin's pack loader and the validation script.

## Status

This document is **normative**. Changes to the schema require a major version bump per PR-05 (semver discipline).

## See also

- `law-packs/_schema.md` — the file-level schema (what fields each file must have)
- `docs/PLUGIN_REQUIREMENTS.md` — PR-02 (law pack contract), PR-07 (contribution path)
- `CONTRIBUTING.md` — step-by-step walkthrough for adding a pack

## Why a pack contract?

Without a strict contract, country packs would drift in shape and the skills couldn't reliably load them. The contract guarantees that:

1. Every pack ships the same set of files in the same locations
2. The plugin's skills can read any pack the same way
3. CI can validate a pack mechanically (no human review needed for structure)
4. Contributors know exactly what to ship

## The 3-layer rule (PR-01 + PR-03)

A pack contains **only** jurisdiction content. It contains:

✅ Statute text (verbatim)
✅ Case law summaries (verbatim quotes from court decisions)
✅ Procedural rules (which forums exist, what their preconditions are)
✅ Limitation periods
✅ Common plays for this jurisdiction
✅ Local-language draft templates
✅ Foundational concepts in the local legal system

A pack does NOT contain:

❌ Case-specific content (PF codes, party names, specific drafts) — that's layer 3
❌ Skill logic, workflow descriptions, or reasoning patterns — that's layer 1 (plugin core)
❌ Hardcoded references to other countries — packs are independent

The plugin's `legal-strategy` skill reads:
- Universal reasoning workflow from `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/strategy-reasoning.md` (layer 1)
- Jurisdiction rules from `<case-repo>/05_legal_research/law_pack/forums.yaml` and friends — the case-repo snapshot placed by `/lex-harness:init` (layer 2)
- Case content from `<case-repo>/06_claims_and_defenses/` and friends (layer 3)

## Versioning

Each pack has its own `version` field in `pack.json`, separate from the plugin version. A pack can be updated without bumping the plugin version. The plugin version represents the LOADER and the SCHEMA — when those change, the plugin major version bumps; when only pack content changes, the pack version bumps.

## Validation flow

When `legal-strategy` activates, it:

1. Reads the case repo's `05_legal_research/law_pack/pack.json` to determine the active jurisdiction
2. Validates the pack against this schema (or uses the cached validation result)
3. If validation fails, the skill HALTS with `[INVALID-PACK]` and lists the failures
4. If validation passes, the skill loads `core/` and proceeds

The validation is also exposed as `./scripts/validate-pack.sh <country>` for CI and contributors.

## Greek MVP as the reference implementation

`law-packs/greece/` is the reference implementation. New contributors should read it before writing their own pack — it's a complete working example that satisfies every contract clause.
EOF
```

- [ ] **Step 5: Verify**

```bash
ls law-packs/_schema.md law-packs/README.md docs/JURISDICTION_PACK_SPEC.md
wc -l law-packs/_schema.md law-packs/README.md docs/JURISDICTION_PACK_SPEC.md
```

Expected: 3 files exist; sizes roughly _schema.md ~120 lines, README.md ~25 lines, JURISDICTION_PACK_SPEC.md ~80 lines.

- [ ] **Step 6: Commit**

```bash
git add law-packs/_schema.md law-packs/README.md docs/JURISDICTION_PACK_SPEC.md
git commit -s -m "$(cat <<'EOF'
docs(spec): law pack contract (T4 / PR-02 / PR-07)

- law-packs/README.md: directory overview + available packs table
- law-packs/_schema.md: file-level schema (pack.json structure, statute
  frontmatter, forums.yaml / limitation_periods.yaml / playbook.yaml)
- docs/JURISDICTION_PACK_SPEC.md: normative specification + 3-layer rule
  + validation flow + greek MVP as reference implementation

The plugin REFUSES to load a pack that fails this schema. CI runs
validate-pack.sh on every PR.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

**Plan A continues in subsequent files** — Tasks 5–37 cover Greek pack content (T5–T10, T28–T29), the 4 skills (T11–T18), 3 commands (T19–T21), templates (T22–T27), bootstrap scripts (T26, T30, T31), tests (T32), docs (T33–T35), CI + release (T36–T37).

To keep this plan file readable, the remaining tasks are split into a continuation file: `2026-04-07-lex-harness-v0.1-part2.md`. The task numbering continues from T5.

The continuation file is created in the next task batch. Plan B (`2026-04-07-yestay-adopts-lex-harness.md`) is written after Plan A is complete.
