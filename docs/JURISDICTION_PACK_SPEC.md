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
