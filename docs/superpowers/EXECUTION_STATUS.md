# lex-harness v0.1 — Execution Status

> **Single source of truth for plan execution progress.** Update this file after every task completion. Read it before starting a new session.

**Last updated:** 2026-04-08
**Current wave:** Scripts layer + Knowledge base ✅ COMPLETE
**Next task:** T11 — `skills/legal-strategy/SKILL.md` (original plan)

---

## Plan source

The plan lives in this repo at `docs/superpowers/plans/`:

- `2026-04-07-lex-harness-v0.1.md` — part 1: T0 read-only prep + T1 init + T2 plugin.json + T3 docs + T4 law pack contract
- `2026-04-07-lex-harness-v0.1-part2.md` — T5–T15 (Greek pack content + skill body + reference files)
- `2026-04-07-lex-harness-v0.1-part3.md` — T16–T27 (3 more skills + 3 commands + templates + git hook)
- `2026-04-07-lex-harness-v0.1-part4.md` — T28–T37 (modules + scripts + tests + CI + release)

The design spec lives at `docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md`.
The validated Greek corpus map lives at `docs/research/LEGAL_CORPUS_MAP.md` (referenced from T5+).

> **Note:** the plan files were originally written in the yestay project (`~/Developer/projects/yestay/docs/superpowers/`) and then copied here. Any references inside the plan to `~/Developer/projects/yestay/...` are HISTORICAL — when the plan instructs you to read a file, the file IS the one in this `lex-harness` repo. If a plan task says "read `~/Developer/projects/yestay/docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md`", that's the same file as `docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md` in this repo.

---

## Progress

### Foundation wave — COMPLETE ✅

| Task | Status | Commit | Notes |
|---|---|---|---|
| T0 | ✅ DONE | n/a | Read-only prep — no commit |
| T1 | ✅ DONE | `a276b32` | Initial commit + .gitignore |
| T1-fix | ✅ DONE | `d2cfed9` | Removed no-op `~/.codex/skills/` pattern + added `.claude/settings.local.json` (code-quality fix) |
| T2 | ✅ DONE | `36b3ca3` | `.claude-plugin/plugin.json` |
| T3 | ✅ DONE | `bc3a5a6` | LICENSE (MIT) + README + CHANGELOG + CONTRIBUTING + CODE_OF_CONDUCT |
| T4 | ✅ DONE | `8c0d104` | `law-packs/_schema.md` + `law-packs/README.md` + `docs/JURISDICTION_PACK_SPEC.md` |

After T4 the foundation wave is complete. The repo is on GitHub at https://github.com/neotherapper/lex-harness, default branch `main`, branch protection enabled (PRs required).

### Greek pack content wave — IN PROGRESS

| Task | Status | Branch / PR | Notes |
|---|---|---|---|
| T5 | ✅ DONE | PR #3 → `9c8899b` | `law-packs/greece/pack.json` (executed by a parallel session) |
| T6 | ✅ DONE | PR #5 → `56321c1` | `law-packs/greece/MODULE_INDEX.md` |
| T7 | ✅ DONE | PR #6 → `2ab90e5` | `forums.yaml` + `limitation_periods.yaml` + `playbook.yaml` + `glossary.md` |
| T8 | ✅ DONE | PR #7 → `4a85934` | Greek core articles part 1 (10 of 22): AK_173 → AK_330 |
| T9 | ✅ DONE | PR #7 → `4a85934` | Greek core articles part 2 (12 of 22): AK_440-452 + AK_602/904/914/932 + KPolD + Syntagma |
| T10 | ✅ DONE | PR #8 → `2d38a28` | Greek tenancy module (8 articles + case_law_inline) |

### Scripts + knowledge-base design wave — COMPLETE ✅

| Task | Status | PR | Notes |
|---|---|---|---|
| T11-scripts | ✅ DONE | PR #9 → `1164548` | Scripts layer: `jurisdiction.yaml`, Fire+UV CLI, BaseFetcher/registry/facade/settings, Greek fetchers (kodiko/et_gr/gslegal/hellenicparliament), shared EU fetchers (eur_lex/n_lex), `/lex-harness:setup` + `/lex-harness:fetch` commands, `lint_knowledge.py`, integration test scaffold. 24 unit tests passing. Design spec: `docs/superpowers/specs/2026-04-08-scripts-knowledge-base-design.md`. Plan: `docs/superpowers/plans/2026-04-08-scripts-layer.md`. |
| T12-knowledge | ✅ DONE | PR #10 → `510ba36` | Knowledge base: 15 docs in `docs/knowledge/` — LEGAL_AI_FRAMEWORK, REQUIREMENTS, greece/CORPUS_MAP, COURT_AUTHORITY, LAW_SOURCES, 8 source profiles (et_gr/kodiko/areiospagos/nomiki_vivliothiki/isocrates_dsanet/lawspot/eur_lex/n_lex), consumer_protection module. All case-specific content stripped; linter passes 15/15. |

### Skill body wave — NOT STARTED

| Task | Status | Notes |
|---|---|---|
| T11 | ⏳ NOT STARTED | `skills/legal-strategy/SKILL.md` (jurisdiction-agnostic port from yestay) |
| T11b | ⏳ NOT STARTED | `skills/legal-strategy/references/tool-detection.md` (PR-12 implementation) |
| T12 | ⏳ NOT STARTED | `references/knowledge-vault.md` |
| T13 | ⏳ NOT STARTED | `references/strategy-reasoning.md` + `settlement-math.md` |
| T14 | ⏳ NOT STARTED | `references/verify-gate.md` (consolidated 9-stage gate) |
| T15 | ⏳ NOT STARTED | `references/atomic-decomposition.md` |

### Skills + commands wave — NOT STARTED

| Task | Status | Notes |
|---|---|---|
| T16 | ⏳ NOT STARTED | `skills/osint-investigation/SKILL.md` (port from yestay) |
| T17 | ⏳ NOT STARTED | `skills/document-production/SKILL.md` + footer block schema |
| T18 | ⏳ NOT STARTED | `skills/devil-advocate/SKILL.md` + isolation rule |
| T19 | ⏳ NOT STARTED | `commands/init.md` |
| T20 | ⏳ NOT STARTED | `commands/fact.md` |
| T21 | ⏳ NOT STARTED | `commands/devil.md` |

### Templates wave — NOT STARTED

| Task | Status | Notes |
|---|---|---|
| T22 | ⏳ NOT STARTED | `templates/case_skeleton/` (10 directories with READMEs) |
| T23 | ⏳ NOT STARTED | `templates/PROVEN_FACTS_REGISTER.md` + `templates/PENDING_FACTS.md` |
| T24 | ⏳ NOT STARTED | `templates/DEADLINE_REGISTER.md` + `templates/CURRENT_STATUS.md` |
| T25 | ⏳ NOT STARTED | `templates/CLAUDE.md` |
| T26 | ⏳ NOT STARTED | `templates/pre-commit` git hook + `scripts/install-githooks.sh` |
| T27 | ⏳ NOT STARTED | `templates/phase3_civil_demand_skeleton.md` + Greek instantiation |

### More Greek modules + tooling wave — NOT STARTED

| Task | Status | Notes |
|---|---|---|
| T28 | ⏳ NOT STARTED | Greek `tax_invoices` module (5 articles) |
| T29 | ⏳ NOT STARTED | Greek `corporate` module (3 articles) |
| T30 | ⏳ NOT STARTED | Codex skills bootstrap script |
| T31 | ⏳ NOT STARTED | `validate-pack.sh` |
| T32 | ⏳ NOT STARTED | Manual smoke test checklists |

### Documentation + CI + release wave — NOT STARTED

| Task | Status | Notes |
|---|---|---|
| T33 | ⏳ NOT STARTED | `docs/ARCHITECTURE.md` |
| T34 | ⏳ NOT STARTED | `docs/PLUGIN_REQUIREMENTS.md` + `docs/ROADMAP.md` |
| T35 | ⏳ NOT STARTED | `docs/TOOL_OPTIONALITY.md` + `docs/SECURITY.md` |
| T36 | ⏳ NOT STARTED | GitHub Actions workflow + issue/PR templates |
| T37 | ⏳ NOT STARTED | v0.1.0 release with stop-go gate |

---

## Workflow rules

**All future work uses GitHub Flow:**

1. Branch off `main`: `git checkout -b <task-id>/<short-desc>` (e.g., `t5/greek-pack-manifest`)
2. Implement the task per the plan
3. Commit with DCO sign-off + Co-Authored-By trailer:
   - `git commit -s -m "$(cat <<'EOF' ... Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com> ... EOF )"`
4. Push: `git push -u origin <branch-name>`
5. Open PR: `gh pr create --title "T5: Greek pack manifest" --body "..."`
6. Self-review the PR
7. Merge via squash (recommended) or merge commit
8. Delete the branch
9. Update this EXECUTION_STATUS.md with the merged commit SHA

**One PR per task** keeps history clean and reviewable. Multiple related tasks in one wave (e.g., T8 + T9 = 22 articles) MAY be combined into one PR if they're tightly coupled.

**Branch naming convention:**
- `t<N>/<short-description>` for plan tasks (e.g., `t5/greek-pack-manifest`)
- `chore/<description>` for housekeeping (e.g., `chore/import-specs-and-plans`)
- `fix/<description>` for bug fixes
- `docs/<description>` for doc-only changes

---

## Git identity

- gh active account: `neotherapper`
- git user.name: `Georgios Pilitsoglou`
- git user.email: `george.pilitsoglou@gmail.com`
- Repo remote: `https://github.com/neotherapper/lex-harness.git` (HTTPS, uses gh CLI stored credentials)

**Critical:** Do NOT push using SSH. The local SSH key is associated with the `GeorgiosPilitsoglou` GitHub account, NOT `neotherapper`. The remote MUST stay on HTTPS so gh CLI's stored auth is used.

To verify before any push:
```bash
gh auth status 2>&1 | grep -A1 "Active account: true"
# Expected: github.com → neotherapper
```

If the active account is anything other than `neotherapper`, run:
```bash
gh auth switch --user neotherapper
```

---

## Optional MCP tools used during execution

None of these are required by the plugin itself (PR-11), but they speed up execution:

- **chrome-devtools** — for fetching Greek law text from kodiko.gr / lawspot.gr / search.et.gr / areiospagos.gr
- **WebFetch** — fallback when Chrome MCP is unavailable (slower but always works)

---

## How to find context

| If you need… | Read… |
|---|---|
| What this plugin is | `README.md` |
| The full design + 15 PR requirements | `docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md` |
| The 22 core Greek articles + 8 modules | `docs/research/LEGAL_CORPUS_MAP.md` |
| Plan A foundation tasks (T0–T4) | `docs/superpowers/plans/2026-04-07-lex-harness-v0.1.md` |
| Plan A Greek pack + skill body tasks (T5–T15) | `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part2.md` |
| Plan A skills/commands/templates tasks (T16–T27) | `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part3.md` |
| Plan A modules/scripts/tests/release tasks (T28–T37) | `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part4.md` |
| Skill ecosystem architecture | `docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md` §2 + §6 |
| Law pack contract | `docs/JURISDICTION_PACK_SPEC.md` + `law-packs/_schema.md` |
| Tool optionality fallback matrix | (created in T35) `docs/TOOL_OPTIONALITY.md` |
