---
description: Set up the lex-harness Python environment (run once after installing the plugin)
allowed-tools: Bash(uv:*), Bash(python:*)
---

Setting up lex-harness scripts environment using uv...

!`uv sync --directory ${CLAUDE_PLUGIN_ROOT}/scripts --extra dev`

Verify the environment:
!`uv run --directory ${CLAUDE_PLUGIN_ROOT}/scripts python -c "import fire, httpx, yaml, fitz; print('lex-harness: all dependencies OK')"`

Show available commands:
!`uv run --directory ${CLAUDE_PLUGIN_ROOT}/scripts python ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py --help`

Report the result to the user. If successful, explain they can now use:
- `/lex-harness:fetch <article-id>` to fetch a law article
- `uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py status` to check the jurisdiction status
