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
