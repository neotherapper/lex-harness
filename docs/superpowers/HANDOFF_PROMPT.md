# Handoff prompt for the next AI agent

> Paste the block below into a fresh Claude Code session started inside `~/Developer/projects/lex-harness/`. It is self-contained: the next agent needs nothing from this file except what's inside the code fence.

---

```markdown
You are continuing execution of `lex-harness v0.1` — an open-source Claude Code plugin for civil legal disputes (Greek MVP, jurisdiction-extensible). The repo lives at `~/Developer/projects/lex-harness/` and is published at https://github.com/neotherapper/lex-harness (MIT, public).

## Your context

A previous session completed the foundation wave (T1–T4) and merged the design spec + plan + execution status into the repo via PR #1. Your job is to continue execution from **Task T5 onward** using GitHub Flow (one branch + PR per task) and `subagent-driven-development` discipline.

## Mandatory first reads

In this exact order, read these 3 files to understand the project:

1. `docs/superpowers/EXECUTION_STATUS.md` — single source of truth for what's done and what's next. Tells you the current task, the workflow rules, the git identity setup.
2. `docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md` — the full design spec. Pay attention to §2 (3-layer architecture), §3 (strategy split), §5 (4 skills), §6 (3 commands), §7 (15 plugin requirements PR-01..PR-15), §7a (15 Gherkin acceptance scenarios), §13 (decision log).
3. `docs/research/LEGAL_CORPUS_MAP.md` — the validated Greek corpus (22 core articles + 8 modules). Referenced from T5+ tasks.

Then read the relevant plan part for whichever task you're starting:
- T5–T15 → `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part2.md`
- T16–T27 → `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part3.md`
- T28–T37 → `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part4.md`

## Hard rules (read before any commit)

1. **Git identity.** This repo's commits MUST be authored by `Georgios Pilitsoglou <george.pilitsoglou@gmail.com>` via the `neotherapper` gh account. Verify before any push:
   ```bash
   gh auth status 2>&1 | grep -A1 "Active account: true"
   # Expected: github.com → neotherapper
   ```
   If the active account is wrong, run `gh auth switch --user neotherapper`.

2. **Remote MUST be HTTPS, not SSH.** The local SSH key is associated with a different GitHub account. The remote URL is already `https://github.com/neotherapper/lex-harness.git`. Do not change it to SSH.

3. **DCO sign-off on every commit.** Use `git commit -s -m "..."` (the `-s` flag adds `Signed-off-by:`). PR-08 requires this on every commit.

4. **Co-Authored-By trailer.** Every commit you make includes:
   ```
   Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
   ```

5. **GitHub Flow — branch + PR per task.** Never commit directly to `main`. For each task:
   ```bash
   git checkout main && git pull
   git checkout -b t<N>/<short-desc>     # e.g., t5/greek-pack-manifest
   # ... implement ...
   git push -u origin t<N>/<short-desc>
   gh pr create --title "T<N>: <title>" --body "..."
   gh pr merge <PR#> --squash --delete-branch
   git checkout main && git pull
   ```

6. **One PR per task** (or per tightly-coupled wave like T8 + T9 = the 22 core articles together).

7. **Update `EXECUTION_STATUS.md` after every merged PR** with the squash commit SHA.

8. **PR-01 layer separation.** Plugin core files (`skills/`, `commands/`, `templates/`, `docs/`) MUST NOT contain country-specific content (no Greek statute IDs, no `ΑΚ`, no `ΚΠολΔ`). Greek-specific content lives in `law-packs/greece/`. CI will eventually enforce this via grep — but the discipline is yours from day 1.

9. **Subagent-driven development.** Use the `superpowers:subagent-driven-development` skill. For each task:
   - Dispatch a fresh implementer subagent with the FULL task text from the plan (don't make them read the plan file — paste it in)
   - After implementer returns DONE: dispatch a spec compliance reviewer
   - After spec compliance passes: dispatch a code quality reviewer
   - Both reviews must approve before marking the task complete and opening the PR

## Your first move

1. Read `docs/superpowers/EXECUTION_STATUS.md` and confirm T1–T4 are marked complete with their commit SHAs.
2. Run:
   ```bash
   cd ~/Developer/projects/lex-harness
   git status                                      # Expected: clean, on main
   git log --oneline | head                        # Expected: 6+ commits
   gh auth status 2>&1 | grep -A1 "Active account: true"  # Expected: neotherapper
   git remote -v                                   # Expected: https://github.com/neotherapper/lex-harness.git
   ```
3. If anything fails, STOP and report. If everything is clean, proceed to T5.

## T5 starting point

T5 creates `law-packs/greece/pack.json` — the Greek pack manifest. Read T5 in `docs/superpowers/plans/2026-04-07-lex-harness-v0.1-part2.md`. The full task text is around 6 steps, ~150 lines.

Branch name: `t5/greek-pack-manifest`
PR title: `T5: Greek pack manifest (law-packs/greece/pack.json)`

## When you finish a wave or hit a stop point

Update `docs/superpowers/EXECUTION_STATUS.md` to reflect the new state, then commit + PR that update if it's not already in the task PR.

## What to ask the human

If you encounter:
- A task that contradicts the design spec → STOP, ask the human
- A `<<FETCH-VERBATIM-FROM-kodiko.gr>>` placeholder you can't fetch (rate limit, paywall) → ask the human
- A spec compliance failure that requires plan changes → ask the human
- Anything that would touch `main` directly → ask the human (you should NEVER touch main directly)

Otherwise, proceed task-by-task through T5 → T37 with branch + PR per task. Update `EXECUTION_STATUS.md` after each merge.

Good luck. The plan is well-specified and the foundation is solid — the next 33 tasks are mostly mechanical execution following the heredocs in the plan files. Stick to the discipline (DCO + branch + PR + subagent reviews) and the v0.1.0 release at T37 is the finish line.
```

---

## Why this file exists

This doc preserves the handoff instructions generated at the end of the session that built the foundation wave (T1–T4). If you start a fresh Claude Code session and need to continue execution, read this file and paste the code block above as your opening prompt.

The content IS the prompt. Everything above the `---` separator is meta / this doc's own explanation.
