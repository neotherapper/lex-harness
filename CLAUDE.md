# CLAUDE.md

> Automatic orientation file for Claude Code sessions opening `~/Developer/projects/lex-harness/`. Read this first.

## What is this repo?

This is **lex-harness** — an open-source Claude Code plugin for civil legal disputes. Greek civil law is the MVP jurisdiction; the architecture supports community-contributed packs for any country. Published at https://github.com/neotherapper/lex-harness (MIT).

The plugin has 3 layers:

1. **Plugin core** (jurisdiction-agnostic) — `skills/`, `commands/`, `templates/`, `docs/`, `law-packs/_schema.md`
2. **Law packs** (jurisdiction-specific, case-agnostic) — `law-packs/<country>/` (Greek MVP only today)
3. **Case repo** (case-specific) — lives in YOUR repo, not here; `/lex-harness:init` scaffolds it

## Current state

The **foundation wave (T1–T4) is complete**:

- ✅ T1 — repo + `.gitignore`
- ✅ T2 — `.claude-plugin/plugin.json`
- ✅ T3 — README + LICENSE (MIT) + CHANGELOG + CONTRIBUTING + CODE_OF_CONDUCT
- ✅ T4 — Law pack contract (`law-packs/_schema.md` + `docs/JURISDICTION_PACK_SPEC.md`)

The **next task is T5**: create `law-packs/greece/pack.json` (the Greek pack manifest).

## Mandatory first reads for a fresh session

Before doing ANY work, read these in order:

1. **`docs/superpowers/EXECUTION_STATUS.md`** — single source of truth for plan progress. Tells you exactly which tasks are done, which is next, and the workflow rules.
2. **`docs/superpowers/HANDOFF_PROMPT.md`** — the paste-ready prompt for resuming execution. If you're a fresh AI agent starting a new session, paste the prompt from that file as your opening instruction.
3. **`docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md`** — the full design spec (3 layers, 4 skills, 3 commands, 15 plugin requirements, 15 Gherkin scenarios).

Then the plan part matching your target task:
- T5–T15 → `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part2.md`
- T16–T27 → `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part3.md`
- T28–T37 → `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part4.md`

## Hard workflow rules

**Never commit directly to `main`.** Branch protection is enabled; PRs are required.

For every task:
```bash
git checkout main && git pull
git checkout -b t<N>/<short-desc>
# ... implement task per the plan ...
git commit -s -m "$(cat <<'EOF'
<subject>

<body>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
git push -u origin t<N>/<short-desc>
gh pr create --title "T<N>: <title>" --body "..."
gh pr merge <PR#> --squash --delete-branch
git checkout main && git pull
# Update EXECUTION_STATUS.md with the merged SHA in a follow-up PR or within the task PR
```

**DCO sign-off on every commit** (`-s` flag) — required by PR-08.
**`Co-Authored-By: Claude` trailer** on every AI commit.
**One PR per task** (or per tightly-coupled wave).
**Update `docs/superpowers/EXECUTION_STATUS.md`** after every merged PR.

## Git identity

Verify before any push:

```bash
gh auth status 2>&1 | grep -A1 "Active account: true"
# Expected: github.com → neotherapper

git remote -v
# Expected: https://github.com/neotherapper/lex-harness.git (HTTPS, NOT SSH)
```

If the active account is not `neotherapper`, run `gh auth switch --user neotherapper`.

**Never switch the remote to SSH.** The local SSH key is associated with a different GitHub account. HTTPS is required so the gh CLI's stored credentials (which are neotherapper's) are used.

## PR-01 layer separation (critical)

Plugin core files (`skills/`, `commands/`, `templates/`, `docs/`) MUST NOT contain country-specific content (no Greek statute IDs, no `ΑΚ`, no `ΚΠολΔ`). Country-specific content lives in `law-packs/<country>/`. Any PR touching `skills/` or `commands/` with country-specific terms should be rejected at review.

## Execution discipline

Use the `superpowers:subagent-driven-development` skill. For each task:

1. Dispatch a fresh implementer subagent with the FULL task text from the plan (paste it into the dispatch, don't ask the subagent to read the plan file).
2. After the implementer returns DONE, dispatch a spec compliance reviewer.
3. After spec compliance passes, dispatch a code quality reviewer.
4. Both reviews must approve before opening the PR.

## What to ask the human

Stop and ask if you encounter:

- A task that contradicts the design spec
- A `<<FETCH-VERBATIM-FROM-kodiko.gr>>` placeholder you can't fetch
- A spec compliance failure that requires plan changes
- Anything that would touch `main` directly

## Author + contact

Georgios Pilitsoglou — [@neotherapper](https://github.com/neotherapper)

Built for [yestay](https://github.com/yestay) (a specific Greek rental dispute) and extracted as a reusable plugin for anyone fighting civil disputes with Claude Code.
