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
