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
