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
