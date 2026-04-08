---
description: Fetch verbatim text for a Greek law article by article ID
argument-hint: [article-id]
allowed-tools: Bash(uv:*)
---

Fetching law article $1...

!`uv run ${CLAUDE_PLUGIN_ROOT}/scripts/laws.py fetch "$1"`

Report the fetched text. If the output starts with `[UNVERIFIED`, explain:
- All configured sources failed to return text
- The article may need manual download from et.gr or kodiko.gr
- The user should check `law-packs/greece/laws-manifest.yaml` for the article's source URLs
