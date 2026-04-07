# lex-harness v0.1 Implementation Plan — Part 3

> Continuation of `2026-04-07-lex-harness-v0.1.md` part 3 — Tasks T16 through T27.

This file picks up where part 2 left off (after T15 — `atomic-decomposition.md`). It covers:

- **T16**: `osint-investigation` skill (ported from yestay, jurisdiction-agnostic)
- **T17**: `document-production` skill + footer block schema + footer block template
- **T18**: `devil-advocate` skill + isolation rule
- **T19**: `/lex-harness:init` slash command
- **T20**: `/lex-harness:fact` slash command
- **T21**: `/lex-harness:devil` slash command
- **T22**: `templates/case_skeleton/` (10 directories with READMEs)
- **T23**: `templates/PROVEN_FACTS_REGISTER.md` + `templates/PENDING_FACTS.md`
- **T24**: `templates/DEADLINE_REGISTER.md` + `templates/CURRENT_STATUS.md`
- **T25**: `templates/CLAUDE.md` (case-agnostic project instructions)
- **T26**: `templates/pre-commit` git hook + `scripts/install-githooks.sh`
- **T27**: `templates/phase3_civil_demand_skeleton.md` + `law-packs/greece/templates/phase3_civil_demand.md`

All work happens in `~/Developer/projects/lex-harness/`. All commits use the personal git config from T1, sign-off (`-s`) per PR-08, and a `Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>` trailer.

---

## Task 16: `osint-investigation` skill (port from yestay, jurisdiction-agnostic)

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/osint-investigation/SKILL.md`
- Create: `~/Developer/projects/lex-harness/skills/osint-investigation/references/chain-of-custody.md`

This task ports the existing yestay `osint-investigation` skill into the plugin. The body must be **jurisdiction-agnostic** per PR-01 and PR-03 — no `ΓΕΜΗ`, no `ΑΑΔΕ`, no `ΑΚ`, no `ΚΠολΔ`. Country-specific database access patterns belong in the active law pack (`law-packs/<country>/osint_databases.md`), not in this skill.

The frontmatter is **v1.1** per round-4 R4-5: `writes_to:` MUST declare `04_evidence/testimony/` so first-party witness statements are captured under the same chain-of-custody discipline as OSINT findings.

The description MUST be ≤1024 chars per Codex hard limit (design spec §5.2).

- [ ] **Step 1: Create the skill directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p skills/osint-investigation/references
```

- [ ] **Step 2: Write `skills/osint-investigation/SKILL.md`**

```bash
cat > skills/osint-investigation/SKILL.md <<'EOF'
---
name: osint-investigation
version: "1.1"
description: >-
  Use when collecting public evidence (OSINT) for a legal case, preserving
  web content before it disappears, capturing witness statements into
  04_evidence/testimony/, grading evidence admissibility (Admiralty A1-F5),
  producing OSINT Finding Reports (OFR), investigating corporate records
  via the active law pack's database list, preserving screenshots with
  SHA-256 + RFC3161 timestamps, or building the chain of custody for
  documentary evidence before filing. Also captures first-party testimony
  (non-OSINT) with the same chain of custody discipline. Proposes facts to
  PENDING_FACTS.md — never writes PROVEN_FACTS_REGISTER directly.
optional_tools:
  - chrome-devtools-mcp     # full-fidelity JS-rendered captures (fallback: WebFetch + manual paste)
  - neo4j-memory            # entity/relation graph (fallback: markdown PROVEN_FACTS only)
  - eur-lex-mcp             # EU-level corporate / regulatory lookup (fallback: manual fetch)
writes_to:
  - "<case-repo>/04_evidence/osint/"
  - "<case-repo>/04_evidence/testimony/"
  - "<case-repo>/04_evidence/CHAIN_OF_CUSTODY.log"
  - "<case-repo>/06_claims_and_defenses/PENDING_FACTS.md"
reads_from:
  - "<case-repo>/01_case_summary/CASE_OVERVIEW.md"
  - "<case-repo>/05_legal_research/law_pack/osint_databases.md"
  - "${CLAUDE_PLUGIN_ROOT}/skills/osint-investigation/references/"
handoff_to:
  - legal-strategy
---

# OSINT Investigation Skill

> Open-source intelligence + first-party testimony capture for legal cases. Jurisdiction-agnostic — country-specific database access lives in the active law pack.

## When this skill activates

Read the description above. Triggers include: collecting public evidence, preserving a web page before it disappears, capturing a witness statement, grading source reliability, building chain of custody before any formal filing.

## The Five-Phase Intelligence Cycle

Every investigation follows this cycle. No phase may be skipped.

```
PLANNING --> COLLECTION --> PROCESSING --> ANALYSIS --> DISSEMINATION
   ^                                                          |
   +------------ feedback (new gaps discovered) ---------------+
```

### Phase 1: PLANNING

1. Define the specific question (e.g., "Does the opposing party have prior complaints?")
2. Identify applicable sources from the active law pack's `osint_databases.md`
3. Prioritise by legal impact
4. Estimate collection effort
5. **Quality gate OG-1:** Requirements must trace to a specific argument file in `06_claims_and_defenses/` or `07_strategy/`

### Phase 2: COLLECTION

1. Navigate to each source. Prefer chrome-devtools MCP if available; otherwise WebFetch; otherwise manual user paste.
2. Capture raw data (screenshots, downloads, API responses, page text)
3. **Immediately hash every collected item:** `shasum -a 256 <file>`
4. Log hash in `<case-repo>/04_evidence/CHAIN_OF_CUSTODY.log`
5. Submit to RFC3161 timestamp service (see `references/chain-of-custody.md`)
6. Create a public web archive snapshot for any deletable content
7. Store under `<case-repo>/04_evidence/osint/<YYYY-MM-DD>_<source-slug>_<hash-prefix>/`
8. **Quality gate OG-2:** Every item must have SHA-256 + timestamp before proceeding

### Phase 3: PROCESSING

1. OCR image-only documents
2. Extract EXIF metadata from photos
3. Parse PDF creation/modification dates
4. Normalise all dates to ISO 8601
5. Grade each source using the Admiralty Code (see `references/chain-of-custody.md` §5)
6. **Quality gate OG-3:** Every source graded A1–F6

### Phase 4: ANALYSIS

1. Assess what each item proves or disproves
2. Identify corroboration patterns (2+ independent sources required for PROVEN status)
3. Map entity relationships (person → company → property → event)
4. Detect timeline anomalies
5. Compare findings to existing PROVEN_FACTS_REGISTER — flag contradictions
6. **Quality gate OG-4:** Every factual claim backed by 2+ independent sources for PROVEN; single-source = AVAILABLE

### Phase 5: DISSEMINATION

1. Append a proposal entry to `<case-repo>/06_claims_and_defenses/PENDING_FACTS.md` for each new fact
2. Update `<case-repo>/04_evidence/EVIDENCE_INDEX.md` with new evidence item IDs
3. (Optional) create entities + relations if neo4j-memory is available
4. Flag affected argument files for `legal-strategy` review via handoff
5. Generate an OSINT Finding Report (OFR) per the format in §6
6. **Quality gate OG-5:** All downstream files updated
7. **Quality gate OG-6:** Preservation sweep complete

> **NEVER write to `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` directly.** AI commits to that file are blocked by the git pre-commit hook (T1 write-path isolation). Always propose via `PENDING_FACTS.md`.

---

## Six Investigation Modes

The exact databases used depend on the jurisdiction. Read `<case-repo>/05_legal_research/law_pack/osint_databases.md` for the country-specific source list. The MODES are universal:

| Mode | What it covers | When to use |
|------|----------------|-------------|
| CORPORATE | Business registry, beneficial ownership, board, gazette filings | Verify ownership chains, restructurings, director roles |
| PROPERTY | Land registry, listing sites, map/satellite, building permits | Re-listing price evidence, ownership chain, lawful use |
| SOCIAL | Public review platforms, professional networks, social media | Pattern of complaints, employee tenure, reputation |
| FORENSIC | Domain WHOIS, certificate transparency, email headers, document XMP, image EXIF | Document authenticity, manipulation detection |
| GOV-DB | Government databases listed in the active law pack's `osint_databases.md` | Official decisions, regulatory filings, court records |
| PRESERVE | All target web properties relevant to the case | Before any formal demand, complaint, or filing |

---

## Chain of Custody Rule (mandatory)

Every collected item MUST receive all three:

1. **SHA-256 hash** of the raw bytes — logged in `<case-repo>/04_evidence/CHAIN_OF_CUSTODY.log`
2. **RFC3161 timestamp** from a qualified TSA — see `references/chain-of-custody.md`
3. **Public web archive snapshot** for any web content that could be deleted

See `references/chain-of-custody.md` for the full step-by-step protocol.

---

## Admiralty Code grading

Every source is graded on two axes: reliability (A–F) and information confidence (1–6).

- Minimum **A3 or B2** required for PROVEN status
- Single source at any grade = AVAILABLE only
- See `references/chain-of-custody.md` §5 for the full matrix

---

## OSINT Finding Report (OFR) format

Every investigation produces an OFR in this YAML structure:

```yaml
id: OFR-YYYY-MM-DD-NNN
date: YYYY-MM-DD
mode: CORPORATE | PROPERTY | SOCIAL | FORENSIC | GOV-DB | PRESERVE
trigger: "Description of evidence gap or investigation trigger"
triggered_by: <argument-id>
findings:
  - id: F-001
    description: "What was discovered"
    source_url: "https://..."
    admiralty_grade: B2
    sha256: "<full hash>"
    timestamp_proof: "<TSA receipt path>"
    archive_url: "<archive snapshot URL>"
    proposed_pf_id: PF-XXX
    affected_files:
      - <argument-file-path>
quality_gates_passed:
  - OG-1
  - OG-2
  - OG-3
  - OG-4
  - OG-5
  - OG-6
handoff_to: legal-strategy
action_required: "What the strategy skill should do with this finding"
```

OFR files are stored in `<case-repo>/04_evidence/osint/` and consumed by `legal-strategy` for argument updates.

---

## First-party testimony capture (non-OSINT, same discipline)

Witness statements the user collects directly from people are NOT public OSINT — but they require the same chain-of-custody discipline so they survive evidentiary challenge.

Capture them under `<case-repo>/04_evidence/testimony/<witness-slug>_<YYYY-MM-DD>.md` with this minimum metadata:

```yaml
---
witness_name: <full name>
witness_role: <relationship to the case>
date_taken: YYYY-MM-DD
location: <where the statement was given>
collected_by: <who interviewed>
language: <language of the statement>
sha256: <hash of the verbatim text section below>
admiralty_grade: <grade of the witness as a source>
attached_files:
  - <recording, signed PDF, etc.>
---

# Statement (verbatim)

<the witness's exact words; no paraphrasing>
```

Then:

1. Hash the file: `shasum -a 256 <file>` → log to `CHAIN_OF_CUSTODY.log`
2. RFC3161 timestamp the hash
3. Append a proposal to `PENDING_FACTS.md` (category T — Testimony)

---

## Quality gates summary

| Gate | Name | Requirement |
|------|------|-------------|
| OG-1 | Requirements traceable | Investigation traces to a specific argument file |
| OG-2 | Chain of custody complete | SHA-256 + RFC3161 timestamp for every item |
| OG-3 | Source graded | Admiralty Code grade assigned |
| OG-4 | Corroboration threshold | 2+ independent sources for PROVEN |
| OG-5 | Dissemination complete | PENDING_FACTS, EVIDENCE_INDEX updated |
| OG-6 | Preservation sweep complete | All web content archived |

---

## Tool optionality (PR-11 / PR-12 / PR-13)

This skill works with ZERO MCP servers installed.

| Optional tool | Used for | Fallback if unavailable |
|---|---|---|
| chrome-devtools-mcp | JS-rendered page capture | WebFetch (HTML only) → manual user paste |
| neo4j-memory | Entity/relation graph | Markdown PROVEN_FACTS_REGISTER only |
| eur-lex-mcp | EU-level lookups | Manual fetch from eur-lex.europa.eu |

If a tool is unavailable, log `[TOOL-UNAVAILABLE:<tool-name>]` in the session brief. NEVER block the workflow.

---

## Reference files (lazy-loaded)

| File | Purpose |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/osint-investigation/references/chain-of-custody.md` | SHA-256 + RFC3161 + archive snapshot protocol + Admiralty Code matrix |

---

## Handoff to legal-strategy

When OSINT closes a gap or surfaces a contradiction, hand off to `legal-strategy` with:

- The OFR ID
- The proposed PF IDs (in PENDING_FACTS)
- The affected argument files
- The action requested (ABSORB / REVIEW / DROP-ARGUMENT)
EOF
```

- [ ] **Step 3: Verify the skill description is ≤1024 chars**

```bash
python3 - <<'PY'
import re, sys
with open('skills/osint-investigation/SKILL.md') as f:
    content = f.read()
m = re.search(r'description:\s*>-\n((?:  .*\n)+)', content)
if not m:
    sys.exit("description block not found")
desc = ' '.join(line.strip() for line in m.group(1).splitlines())
print(f"description length: {len(desc)} chars")
assert len(desc) <= 1024, f"too long: {len(desc)} > 1024"
print("OK")
PY
```

Expected: prints a length ≤ 1024 followed by `OK`.

- [ ] **Step 4: Verify the skill body has NO jurisdiction-specific content (PR-01 / PR-03)**

```bash
python3 - <<'PY'
import sys
banned = [
    'Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'ΓΕΜΗ', 'ΑΑΔΕ', 'GEMI', 'AADE',
    'Art. 612A', 'Άρειος Πάγος', 'kodiko.gr', 'lawspot.gr', 'dsanet.gr',
    'ktimanet', 'Diavgeia',
]
with open('skills/osint-investigation/SKILL.md') as f:
    content = f.read()
hits = [w for w in banned if w in content]
if hits:
    sys.exit(f"PR-01 violation — banned terms in skill body: {hits}")
print("OK — skill body is jurisdiction-agnostic")
PY
```

Expected: `OK — skill body is jurisdiction-agnostic`.

- [ ] **Step 5: Write `references/chain-of-custody.md`**

```bash
cat > skills/osint-investigation/references/chain-of-custody.md <<'EOF'
# Chain of Custody Protocol

> Lazy-loaded reference for the `osint-investigation` skill. Read this when capturing any new evidence item — OSINT or first-party testimony.

## Goal

Make every evidence item independently verifiable years after capture, by anyone, without trusting the user's word that the file is unmodified.

Three pieces of proof:

1. **Cryptographic hash** — proves the bytes haven't changed since capture
2. **Trusted timestamp** — proves the file existed on a specific date
3. **Independent archive snapshot** — proves the source content existed (for web evidence)

---

## §1. SHA-256 hashing

Every file under `<case-repo>/04_evidence/` MUST have a SHA-256 hash recorded in `<case-repo>/04_evidence/CHAIN_OF_CUSTODY.log`.

```bash
shasum -a 256 <path-to-file>
```

Append the output to the log with a timestamp:

```bash
{
  echo "## $(date -u +%Y-%m-%dT%H:%M:%SZ) — <description>"
  shasum -a 256 <path-to-file>
  echo
} >> <case-repo>/04_evidence/CHAIN_OF_CUSTODY.log
```

The log is append-only. Never edit prior entries.

---

## §2. RFC3161 trusted timestamps

A SHA-256 hash alone proves nothing about WHEN the file existed. RFC3161 timestamping fixes this — a Time Stamping Authority (TSA) signs `(hash, timestamp)` cryptographically.

### Free TSAs

| TSA | URL | Notes |
|---|---|---|
| FreeTSA | `https://freetsa.org/tsr` | Free, public, RFC3161, no rate limit for personal use |
| DigiCert | `http://timestamp.digicert.com` | Free, public, widely trusted |
| Sectigo | `http://timestamp.sectigo.com` | Free, public |

### Procedure (using OpenSSL)

```bash
# 1. Compute the hash and create a TSQ
openssl ts -query -data <path-to-file> -no_nonce -sha256 -cert -out request.tsq

# 2. Submit to a TSA (curl)
curl -s -H "Content-Type: application/timestamp-query" \
     --data-binary @request.tsq \
     https://freetsa.org/tsr > response.tsr

# 3. Store the TSR alongside the original file
mv response.tsr <path-to-file>.tsr

# 4. Verify any time later
openssl ts -verify -data <path-to-file> -in <path-to-file>.tsr \
           -CAfile <freetsa-cacert.pem>
```

### Qualified TSAs (jurisdiction-specific)

Some jurisdictions accept only "qualified" trust service providers under their local digital signature law. The active law pack's `osint_databases.md` lists qualified TSAs for that country. For pre-litigation evidence preservation, FreeTSA is sufficient.

---

## §3. Public web archive snapshots

Web evidence is volatile. Always create an INDEPENDENT snapshot in a public archive before relying on the URL.

### Primary archives

| Archive | URL pattern | Notes |
|---|---|---|
| archive.ph (archive.today) | `https://archive.ph/<URL>` | Captures full DOM including JS-rendered content |
| Internet Archive Wayback Machine | `https://web.archive.org/save/<URL>` | Largest archive; respects robots.txt |
| Webrecorder.net | `https://webrecorder.net/` | High-fidelity captures including video/audio |

### Procedure

1. Submit the URL to BOTH archive.ph and web.archive.org (redundancy)
2. Wait for the archived URL to resolve (usually <60s)
3. Capture the archived URL as a string in the OFR `findings[].archive_url` field
4. Take a screenshot of the archive page itself as a secondary proof

If both archives refuse, the OFR finding gets `admiralty_grade` capped at C3.

---

## §4. Capture workflow (combined)

For one piece of web evidence:

```bash
# 1. Capture the page (chrome-devtools MCP if available, else WebFetch)
#    Save the rendered HTML, a screenshot, and any downloaded artefacts to
#    <case-repo>/04_evidence/osint/<YYYY-MM-DD>_<slug>/

# 2. Hash everything in the directory
find <dir> -type f -exec shasum -a 256 {} \; >> <case-repo>/04_evidence/CHAIN_OF_CUSTODY.log

# 3. Concatenate the hashes into a single manifest file and timestamp THAT
shasum -a 256 <dir>/* | sort > <dir>/MANIFEST.txt
openssl ts -query -data <dir>/MANIFEST.txt -no_nonce -sha256 -cert -out <dir>/MANIFEST.tsq
curl -s -H "Content-Type: application/timestamp-query" \
     --data-binary @<dir>/MANIFEST.tsq \
     https://freetsa.org/tsr > <dir>/MANIFEST.tsr

# 4. Submit to archive.ph and web.archive.org for the original URL

# 5. Append a chain-of-custody log entry referencing all of the above
```

The MANIFEST.txt + MANIFEST.tsr pair lets a third party verify the entire directory in one shot.

---

## §5. Admiralty Code grading matrix

NATO STANAG 2511 standard for evaluating raw intelligence. Two independent axes — source reliability and information credibility.

### Reliability (the source)

| Grade | Reliability | Description |
|---|---|---|
| **A** | Completely reliable | Official primary source; government registry; court decision |
| **B** | Usually reliable | Established news outlet; corporate annual report |
| **C** | Fairly reliable | Trade publication; industry blog with named author |
| **D** | Not usually reliable | Anonymous user-generated content |
| **E** | Unreliable | Known biased source; competitor blog |
| **F** | Cannot be judged | Source unknown |

### Credibility (the information)

| Grade | Credibility | Description |
|---|---|---|
| **1** | Confirmed | Independently verified by ≥2 other sources of grade A or B |
| **2** | Probably true | Logically consistent; one corroboration |
| **3** | Possibly true | Plausible but uncorroborated |
| **4** | Doubtful | Contradicts other known facts |
| **5** | Improbable | Strongly contradicts other facts |
| **6** | Cannot be judged | No basis for assessment |

### Combined grade

**A1** = gold standard. **B2** = practical minimum for PROVEN status. Anything below **C3** stays AVAILABLE only.

---

## §6. Common mistakes to avoid

1. **Hashing the rendered page instead of the raw HTML.** Hash the raw HTTP response body.
2. **Submitting to archive.ph from inside Tor or a VPN.** Use a clean residential connection.
3. **Forgetting to timestamp.** A hash without a TSR proves nothing about WHEN.
4. **Editing CHAIN_OF_CUSTODY.log.** It's append-only.
5. **Trusting EXIF dates.** EXIF can be forged. Only hashes + TSRs are tamper-evident.
6. **Skipping the manifest step.** A directory manifest + one TSR is faster and equally strong.

---

## §7. When this protocol is NOT enough

For evidence requiring qualified trust services in a court that demands them, the active law pack's `osint_databases.md` lists country-specific qualified TSAs. For evidence requiring notarisation or apostille, no protocol substitutes — those require physical presence with a notary.
EOF
```

- [ ] **Step 6: Verify both files exist**

```bash
ls skills/osint-investigation/SKILL.md skills/osint-investigation/references/chain-of-custody.md
wc -l skills/osint-investigation/SKILL.md skills/osint-investigation/references/chain-of-custody.md
```

Expected: both files exist.

- [ ] **Step 7: Commit**

```bash
git add skills/osint-investigation/
git commit -s -m "$(cat <<'EOF'
feat(skills): osint-investigation skill v1.1 (T16)

Ports the existing yestay osint-investigation skill into the plugin
as a jurisdiction-agnostic v1.1:

- SKILL.md description ≤1024 chars per Codex hard limit (PR-15)
- writes_to declares 04_evidence/testimony/ (round-4 R4-5)
- Body contains zero jurisdiction-specific content (PR-01 / PR-03)
- optional_tools field declares chrome-devtools-mcp, neo4j-memory,
  eur-lex-mcp as optional with documented fallbacks (PR-11)
- references/chain-of-custody.md ports the SHA-256 + RFC3161 +
  archive snapshot protocol with FreeTSA as the default free TSA

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Expected: commit succeeds with a DCO sign-off line and the AI trailer.

---

## Task 17: `document-production` skill + footer block schema + footer block template

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/document-production/SKILL.md`
- Create: `~/Developer/projects/lex-harness/skills/document-production/references/footer-block-schema.md`
- Create: `~/Developer/projects/lex-harness/templates/footer_block.md`

`document-production` is a NEW skill (not ported from yestay). It owns writes to `08_drafts/`. It is the only skill that releases formal legal documents.

The skill enforces the **mandatory footer block** on every released draft. Per design decision **D44** (round 4), the footer has exactly **4 fields** — the earlier 6-field version was rejected as over-engineered:

```yaml
footer_block:
  pf_ids: [PF-A29, PF-A30, PF-G07]
  law_articles: [<article-id>, ...]
  evidence_items: [E-101, E-102]
  da_review_refs: [DA_SA31_2026-04-07.md]
```

The skill must be JURISDICTION-AGNOSTIC. It loads templates from the active law pack at runtime (`05_legal_research/law_pack/templates/`).

- [ ] **Step 1: Create the skill directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p skills/document-production/references
```

- [ ] **Step 2: Write `skills/document-production/SKILL.md`**

```bash
cat > skills/document-production/SKILL.md <<'EOF'
---
name: document-production
version: "1.0"
description: >-
  Use when producing any formal legal document that will leave the case
  workspace — demand letters, civil complaints, regulatory filings,
  consumer protection complaints, data protection authority filings,
  criminal referrals, formal email responses, settlement proposals, or
  any document the user is about to send to the opposing party, a court,
  a regulator, or a third-party authority. Loads templates from the
  active law pack, runs the 9-stage verify-gate before release, enforces
  the mandatory 4-field draft footer block (pf_ids, law_articles,
  evidence_items, da_review_refs), and dispatches devil-advocate per
  high-risk element. OWNS writes to 08_drafts/. Never releases a draft
  that fails the gate. Never paraphrases statutes in the legal basis
  section.
optional_tools:
  - dikaio-ai-mcp           # citation auto-verification (fallback: manual law-pack source URL lookup)
writes_to:
  - "<case-repo>/08_drafts/"
reads_from:
  - "<case-repo>/06_claims_and_defenses/"
  - "<case-repo>/07_strategy/"
  - "<case-repo>/04_evidence/"
  - "<case-repo>/05_legal_research/law_pack/templates/"
  - "${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/verify-gate.md"
  - "${CLAUDE_PLUGIN_ROOT}/skills/document-production/references/footer-block-schema.md"
  - "${CLAUDE_PLUGIN_ROOT}/templates/footer_block.md"
  - "${CLAUDE_PLUGIN_ROOT}/templates/phase3_civil_demand_skeleton.md"
handoff_to:
  - devil-advocate
---

# Document Production Skill

> The ONLY skill that writes to `08_drafts/`. Every formal document that leaves the workspace passes through this skill.

## When this skill activates

Triggers: drafting any document the user will send to a real recipient — opposing party, court, regulator, ombudsman, criminal authority, data protection authority, settlement counterparty. NOT for internal notes or strategy memos (those belong to `legal-strategy`).

## Hard rules (non-negotiable)

1. **OWNS 08_drafts/.** No other skill writes there.
2. **Never paraphrase statutes.** Legal basis sections quote verbatim text from the active law pack.
3. **Verify-gate is mandatory.** Every draft passes the 9-stage gate.
4. **Footer block is mandatory.** Every draft ends with the 4-field footer block.
5. **High-risk elements get devil-advocate.** Any compound argument with ≥3 elements OR settlement value >50% of total claim gets dispatched to `devil-advocate` BEFORE release.
6. **Layer separation.** This skill body contains NO country-specific content.

---

## The 6-step production pipeline

```
LOAD --> POPULATE --> VERIFY --> DEVIL --> FOOTER --> RELEASE
```

### Step 1: LOAD

1. Determine the document type the user is requesting
2. Read `<case-repo>/05_legal_research/law_pack/pack.json` to identify the active jurisdiction
3. Load the matching template from `<case-repo>/05_legal_research/law_pack/templates/<doc-type>.md`
4. If no template exists, fall back to `${CLAUDE_PLUGIN_ROOT}/templates/phase3_civil_demand_skeleton.md` and warn the user
5. Read the case content the draft will reference
6. Read `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` to resolve every PF ID

### Step 2: POPULATE

1. Walk the template's placeholder slots (`<<...>>` markers)
2. For each statute placeholder, fetch the verbatim text from the active law pack
3. Confirm the SHA-256 in the article file's frontmatter matches the verbatim section. If not, HALT with `[STATUTE-DRIFT]`
4. For each PF placeholder, look up the entry in PROVEN_FACTS_REGISTER
5. For each evidence placeholder, look up the entry in EVIDENCE_INDEX

### Step 3: VERIFY

Run the 9-stage verify-gate from `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/verify-gate.md`. If ANY stage fails, the draft is BLOCKED.

### Step 4: DEVIL

Decide whether to dispatch `devil-advocate`:

| Trigger | Dispatch DA? |
|---|---|
| Compound argument with ≥3 elements | YES |
| Settlement value >50% of total claim | YES |
| First time this argument is being formalised | YES |
| Routine follow-up using a previously DA-reviewed argument | OPTIONAL |
| Pure procedural document | NO |

If YES, dispatch via the Task tool with the **isolation payload**. Read the verdict:

- **SOUND** → proceed to Step 5
- **NEEDS-WORK** → revise the draft and re-run from Step 3
- **DROP** → halt; ask the user whether to drop the argument

### Step 5: FOOTER

Append the mandatory 4-field footer block. Use `${CLAUDE_PLUGIN_ROOT}/templates/footer_block.md` as the template. Populate:

- `pf_ids` — every PF ID inlined in the body
- `law_articles` — every article ID inlined in the legal basis section
- `evidence_items` — every E ID referenced in the body
- `da_review_refs` — the DA review filename(s) considered (empty array if no DA)

### Step 6: RELEASE

1. Save the draft to `<case-repo>/08_drafts/<doc-type>_<argument-id>_<YYYY-MM-DD>.md`
2. Update `<case-repo>/CURRENT_STATUS.md` with the new draft path
3. Print to the user: file path + DA verdict + next step
4. NEVER auto-send anything.

---

## Hand off when

| If the user asks for | Hand off to |
|---|---|
| Strategic decision about which forum to use | `legal-strategy` |
| Adversarial review of a specific argument | `devil-advocate` |
| New evidence to support the draft | `osint-investigation` |
| Adding a fact the draft needs | `legal-strategy` (routes to `/lex-harness:fact`) |

---

## Tool optionality (PR-11)

This skill works with ZERO MCP servers installed.

| Optional tool | Used for | Fallback |
|---|---|---|
| dikaio-ai-mcp | Automated citation verification | Manual lookup at the active law pack's `source_primary` URL |

If unavailable, log `[TOOL-UNAVAILABLE:dikaio-ai-mcp]` and add a manual-verification line to the footer's `manual_verification_required` field.

---

## Reference files (lazy-loaded)

| File | Purpose |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/document-production/references/footer-block-schema.md` | Mandatory 4-field footer block contract |
| `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/verify-gate.md` | The 9-stage gate |
| `${CLAUDE_PLUGIN_ROOT}/templates/footer_block.md` | The literal markdown template |
| `${CLAUDE_PLUGIN_ROOT}/templates/phase3_civil_demand_skeleton.md` | Jurisdiction-agnostic fallback skeleton |
EOF
```

- [ ] **Step 3: Verify the description is ≤1024 chars**

```bash
python3 - <<'PY'
import re, sys
with open('skills/document-production/SKILL.md') as f:
    content = f.read()
m = re.search(r'description:\s*>-\n((?:  .*\n)+)', content)
desc = ' '.join(line.strip() for line in m.group(1).splitlines())
print(f"description length: {len(desc)} chars")
assert len(desc) <= 1024, f"too long: {len(desc)}"
print("OK")
PY
```

Expected: ≤1024 followed by `OK`.

- [ ] **Step 4: Verify no jurisdiction-specific content**

```bash
python3 - <<'PY'
import sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'ΓΕΜΗ', 'ΑΑΔΕ', 'kodiko.gr',
          'lawspot.gr', 'Άρειος Πάγος', 'Eirinodikio', 'Art. 612A']
with open('skills/document-production/SKILL.md') as f:
    content = f.read()
hits = [w for w in banned if w in content]
if hits:
    sys.exit(f"PR-01 violation: {hits}")
print("OK")
PY
```

Expected: `OK`.

- [ ] **Step 5: Write `references/footer-block-schema.md`**

```bash
cat > skills/document-production/references/footer-block-schema.md <<'EOF'
# Footer Block Schema (4-field, mandatory)

> The contract for the mandatory footer block on every formal document released by `document-production`. Per design decision D44 (round 4), this is the **4-field version**.

## Why a footer block at all

A retained lawyer reviewing a draft needs to verify the citation chain in ≤2 minutes (REQ-07-004). Without a footer block, they have to grep the body for every PF ID, every article, every evidence item.

The footer is a single source of truth that lists every external reference the draft makes. The lawyer can pick 5 random items and trace them in <2 min.

## The 4 fields

| Field | Type | Required | Description |
|---|---|---|---|
| `pf_ids` | array of PF ID strings | YES (≥1) | Every PF code the body relies on. Resolves to entries in `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md`. |
| `law_articles` | array of article ID strings | YES (≥1) | Every statute article the legal basis section cites. Resolves to the active law pack's `core/` or `modules/`. |
| `evidence_items` | array of evidence ID strings | OPTIONAL | Every E code the body references. Resolves to entries in `04_evidence/EVIDENCE_INDEX.md`. |
| `da_review_refs` | array of DA review filename strings | OPTIONAL | Devil's advocate review files considered. Resolves to `07_strategy/da_reviews/`. |

## Format (literal)

```yaml
---
footer_block:
  pf_ids:
    - PF-A29
    - PF-A30
    - PF-G07
  law_articles:
    - <article-id-1>
    - <article-id-2>
  evidence_items:
    - E-101
    - E-102
  da_review_refs:
    - DA_<argument-id>_<date>.md
verify_gate:
  passed: true
  date: <YYYY-MM-DD>
  failures: []
manual_verification_required:
  - <free-text item>
---
```

The block goes at the END of the draft, not the start.

## Validation rules

A draft is REJECTED at gate Stage 9 if:

1. The footer block is missing entirely
2. `pf_ids` is empty
3. `law_articles` is empty
4. Any PF ID in `pf_ids` does not resolve
5. Any article ID in `law_articles` does not resolve
6. Any evidence item in `evidence_items` does not resolve
7. Any DA review ref in `da_review_refs` does not resolve
8. `verify_gate.passed` is false

## Why not 6 fields (rejected design)

The earlier draft had two extra fields: `forum_target` and `next_action`. Both were dropped:

- `forum_target` is already implicit in the document type. Adding the field encouraged users to contradict themselves.
- `next_action` is workflow state, not citation provenance. It belongs in CURRENT_STATUS.md.

## Examples

### Minimal

```yaml
---
footer_block:
  pf_ids:
    - PF-A01
  law_articles:
    - <example-article-id>
  evidence_items: []
  da_review_refs: []
verify_gate:
  passed: true
  date: 2026-04-08
  failures: []
manual_verification_required: []
---
```

### Full

```yaml
---
footer_block:
  pf_ids:
    - PF-A29
    - PF-A30
    - PF-G07
    - PF-F57
  law_articles:
    - <art-1>
    - <art-2>
  evidence_items:
    - E-101
    - E-102
  da_review_refs:
    - DA_SA31_2026-04-07.md
verify_gate:
  passed: true
  date: 2026-04-08
  failures: []
manual_verification_required:
  - "Manual verification at the active law pack's source_primary URL"
---
```
EOF
```

- [ ] **Step 6: Write `templates/footer_block.md`**

```bash
mkdir -p templates
cat > templates/footer_block.md <<'EOF'
<!--
  Mandatory draft footer block (4-field version per D44).
  See ${CLAUDE_PLUGIN_ROOT}/skills/document-production/references/footer-block-schema.md
  for the full contract. Replace the placeholders before release.
-->

---

```yaml
---
footer_block:
  pf_ids:
    - <PF-ID-1>
    - <PF-ID-2>
  law_articles:
    - <article-id-1>
    - <article-id-2>
  evidence_items:
    - <E-ID-1>
  da_review_refs:
    - <DA-review-filename.md>
verify_gate:
  passed: <true|false>
  date: <YYYY-MM-DD>
  failures: []
manual_verification_required: []
---
```
EOF
```

- [ ] **Step 7: Verify all 3 files**

```bash
ls skills/document-production/SKILL.md \
   skills/document-production/references/footer-block-schema.md \
   templates/footer_block.md
wc -l skills/document-production/SKILL.md \
      skills/document-production/references/footer-block-schema.md \
      templates/footer_block.md
```

Expected: 3 files exist.

- [ ] **Step 8: Commit**

```bash
git add skills/document-production/ templates/footer_block.md
git commit -s -m "$(cat <<'EOF'
feat(skills): document-production v1.0 + 4-field footer block (T17)

New skill that owns writes to 08_drafts/. Enforces the mandatory
4-field footer block per design decision D44.

- SKILL.md description ≤1024 chars (Codex hard limit)
- 6-step production pipeline: LOAD → POPULATE → VERIFY → DEVIL →
  FOOTER → RELEASE
- Loads templates from the active law pack at runtime
- Dispatches devil-advocate per the high-risk trigger table
- Body contains zero jurisdiction-specific content (PR-01 / PR-03)
- references/footer-block-schema.md documents the 4-field contract
- templates/footer_block.md is the literal markdown template

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 18: `devil-advocate` skill + isolation rule

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/devil-advocate/SKILL.md`
- Create: `~/Developer/projects/lex-harness/skills/devil-advocate/references/isolation-rule.md`

`devil-advocate` is the most opinionated skill in the plugin. Per design spec §5.4, it exists to provide **adversarial review** of strategic arguments — but the review is only useful if the reviewer has NO prior session context. A session-aware devil's advocate collapses into sycophantic agreement ("yes, that argument is strong") because it has absorbed the user's framing.

The isolation rule is the whole point of the skill: it refuses to run if it detects strategy memos, prior DA reviews, or case theory in its dispatch payload. It emits `[ISOLATION-BREACH]` and halts.

The skill is invoked either:
1. Via `/lex-harness:devil <argument-id>` (the slash command in T21), or
2. Via handoff from `document-production` Step 4 when a high-risk element triggers DA review

Either way, the **dispatcher** MUST build a minimal payload containing ONLY:
- The raw argument text
- The verbatim PF entries it relies on
- The verbatim statute text for each cited article
- The forum + stakes
- The output file path

Nothing else. No "here's the case theory." No "this argument is important." No "this was reviewed last week by X." Bare facts + bare law.

- [ ] **Step 1: Create the skill directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p skills/devil-advocate/references
```

- [ ] **Step 2: Write `skills/devil-advocate/SKILL.md`**

```bash
cat > skills/devil-advocate/SKILL.md <<'EOF'
---
name: devil-advocate
version: "1.0"
description: >-
  Use when adversarially reviewing a strategic argument, claim, or
  compound-argument element (CH/CC/SA files, or specific elements).
  MUST be dispatched as a fresh subagent with NO inherited session
  context — only the raw argument text, the verbatim facts, the cited
  statutes, and the forum + stakes. The isolation is the whole point:
  a session-aware DA collapses into sycophantic agreement. Refuses with
  [ISOLATION-BREACH] if it detects strategy memos, prior DA reviews, or
  case theory in its dispatch payload. Outputs a per-argument DA review
  file with counter-arguments rated HIGH/MEDIUM/LOW, holes in the
  factual chain, and a verdict (SOUND / NEEDS-WORK / DROP).
optional_tools: []
writes_to:
  - "<case-repo>/07_strategy/da_reviews/"
reads_from: []
handoff_to: []
---

# Devil's Advocate Skill

> Adversarial review that is only useful in isolation. No prior context. No shared workspace. No memory of the last round.

## When this skill activates

Triggers: the user asks for an adversarial review of a specific argument; `document-production` hands off for high-risk element review; `/lex-harness:devil <argument-id>` is invoked. Never activate without a dispatch payload.

## The isolation rule (hard)

This skill REFUSES to run if its dispatch payload contains any of:

- Strategy memos (files under `07_strategy/`)
- Prior DA review files (files under `07_strategy/da_reviews/`)
- Case theory documents (`CASE_THEORY.md`, `LEGAL_PLAYBOOK.md`)
- Settlement economics (`SETTLEMENT_ECONOMICS.md`)
- Any prose from the user that frames the argument as "strong" or "weak"
- Any references to the case's previous outcomes
- Any mention of the user's personal opinion of the argument

If detected, the skill emits:

```
[ISOLATION-BREACH] detected: <list of contaminating items>
REASON: a session-aware devil's advocate collapses to sycophantic agreement.
The dispatcher must rebuild the payload with ONLY raw argument text + verbatim PFs + verbatim statutes + forum + stakes.
```

…and HALTS. Full stop. No partial review. No "I'll try anyway."

See `references/isolation-rule.md` for the full isolation contract + the acceptable payload schema.

---

## The acceptable payload schema

The dispatcher MUST provide exactly this structure — nothing more, nothing less:

```yaml
argument_id: <e.g. SA-31 or CH1 or CC3>
argument_text: |
  <the raw prose of the argument, with no strategic framing>
facts:
  - pf_id: PF-A01
    category: A
    text: "<verbatim fact text from PROVEN_FACTS_REGISTER>"
    source: "<source field from the register>"
    grade: A1
  - pf_id: PF-A02
    ...
laws:
  - article_id: <id>
    verbatim_text: |
      <the exact statute text from the active law pack's core/ or modules/>
    sha256: <16-char hex prefix from frontmatter>
    source_primary: <URL>
forum: <civil court | consumer ombudsman | data protection authority | criminal | settlement>
stakes: <monetary value or one-line description>
output_path: <case-repo>/07_strategy/da_reviews/DA_<argument-id>_<YYYY-MM-DD>.md
```

If any required field is missing, emit `[INCOMPLETE-PAYLOAD]` and halt.

---

## The review workflow

### Step 1: Read the payload into memory

Do NOT open any other file. Do NOT read `CURRENT_STATUS.md`. Do NOT search the case repo. You have exactly what the dispatcher provided.

### Step 2: Generate counter-arguments

For each cited law article, ask: **what is the strongest attack?**

- Does the article apply to the stated facts? Check the holding characterisation.
- Are there ≥2 appellate decisions that limit or distinguish the article?
- Does the argument misread the article's scope?
- Are there procedural defenses (limitation period, forum selection, standing) that defeat the argument before the merits?
- Does the opposing party have a plausible factual counter-narrative consistent with the same facts?

Generate at least **3** counter-arguments. Rate each:

| Rating | Meaning |
|---|---|
| **HIGH** | Likely to defeat the argument if raised by competent opposing counsel |
| **MEDIUM** | Weakens the argument; may require additional facts or law to rebut |
| **LOW** | Noted but unlikely to succeed |

### Step 3: Holes in the factual chain

For each PF cited:

- Is the source field actually capable of proving the fact at the stated grade?
- Is the fact the only plausible reading of the source, or are there alternatives?
- Is the fact temporally consistent with the other facts (no impossible sequences)?
- Is the fact internally consistent (no contradictions with prior facts in the same register)?

Flag any hole as **[HOLE]** with a one-sentence description.

### Step 4: Verdict

Emit exactly one of:

- **SOUND** — no HIGH counter-arguments, no [HOLE] items. The argument survives adversarial review.
- **NEEDS-WORK** — 1–2 HIGH counter-arguments OR 1–2 [HOLE] items. The argument is salvageable but requires revision.
- **DROP** — 3+ HIGH counter-arguments OR 3+ [HOLE] items OR any fatal procedural defect. The argument should not be used.

The verdict MUST have a 2–3 sentence rationale.

### Step 5: Write the review file

Write the output to the path the dispatcher provided (`output_path`). Use the DA review format below. Do NOT update any other file. Do NOT modify any existing DA review.

---

## DA review file format

```markdown
---
argument_id: <e.g. SA-31>
date: YYYY-MM-DD
reviewer: devil-advocate v1.0
isolation_verified: true
payload_hash: <sha256 of the received payload>
verdict: SOUND | NEEDS-WORK | DROP
---

# DA review: <argument-id>

## Payload received (for audit)

- PFs: <list>
- Laws: <list>
- Forum: <forum>
- Stakes: <stakes>

## Counter-arguments

### CA-1 (<HIGH|MEDIUM|LOW>)

<statement of the counter-argument, 2–3 sentences>

**Why it matters:** <1 sentence>
**What would defeat it:** <1 sentence, or "nothing">

### CA-2 (<rating>)

...

### CA-3 (<rating>)

...

## Holes in the factual chain

- **[HOLE]** <description of the hole, referencing the PF ID>

## Verdict

**<SOUND | NEEDS-WORK | DROP>** — <2–3 sentence rationale>

## Recommended next action

<1–2 sentences — what the dispatcher should do with this review>
```

---

## What this skill NEVER does

- Read case files outside the payload
- Reference prior DA reviews
- Acknowledge strategic framing from the dispatcher
- Soften counter-arguments because the dispatcher said the argument was "important"
- Produce "balanced" reviews (the point is adversarial, not balanced)
- Write to any file other than `output_path`

---

## Reference files (lazy-loaded)

| File | Purpose |
|------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/devil-advocate/references/isolation-rule.md` | The full isolation contract + contamination detection algorithm + acceptable payload schema |
EOF
```

- [ ] **Step 3: Verify the description is ≤1024 chars**

```bash
python3 - <<'PY'
import re, sys
with open('skills/devil-advocate/SKILL.md') as f:
    content = f.read()
m = re.search(r'description:\s*>-\n((?:  .*\n)+)', content)
desc = ' '.join(line.strip() for line in m.group(1).splitlines())
print(f"description length: {len(desc)} chars")
assert len(desc) <= 1024, f"too long: {len(desc)}"
print("OK")
PY
```

Expected: ≤1024 followed by `OK`.

- [ ] **Step 4: Verify no jurisdiction-specific content**

```bash
python3 - <<'PY'
import sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'ΓΕΜΗ', 'ΑΑΔΕ', 'kodiko.gr',
          'lawspot.gr', 'Άρειος Πάγος', 'Eirinodikio', 'Art. 612A']
with open('skills/devil-advocate/SKILL.md') as f:
    content = f.read()
hits = [w for w in banned if w in content]
if hits:
    sys.exit(f"PR-01 violation: {hits}")
print("OK")
PY
```

Expected: `OK`.

- [ ] **Step 5: Write `references/isolation-rule.md`**

```bash
cat > skills/devil-advocate/references/isolation-rule.md <<'EOF'
# Devil's Advocate Isolation Rule

> The full contract for the isolation rule enforced by the `devil-advocate` skill. Read this when building a dispatch payload or when the skill halts with `[ISOLATION-BREACH]`.

## Why isolation

A session-aware devil's advocate is useless. If the reviewer has seen:

- The case theory
- Prior DA reviews of the same argument
- Strategic memos that frame this argument as "strong"
- The user's personal opinion of the argument

…then the reviewer has absorbed the user's framing. Counter-arguments get softened. "This is a good argument" becomes the baseline assumption. Adversarial review collapses into sycophantic agreement.

The isolation rule prevents this by requiring the dispatcher to rebuild the payload from scratch — strip all framing, all prior reviews, all strategic context. What remains is bare facts + bare law + the argument itself. The reviewer sees only what an opposing lawyer would see.

---

## Contamination detection algorithm

When the skill receives a payload, it runs these checks BEFORE reading the argument:

### Check 1: Strategic framing words in `argument_text`

Banned words/phrases inside `argument_text`:

- "strong argument"
- "weak argument"
- "winning argument"
- "our theory"
- "the case theory"
- "I believe"
- "We think"
- "This is our best shot"
- "dropped argument"
- "previously reviewed"
- "per our playbook"
- "per DECISION_LOG"

If any of these appear in `argument_text`, emit `[ISOLATION-BREACH] strategic framing in argument_text: <word>` and HALT.

### Check 2: Prior DA review references

Banned substrings anywhere in the payload:

- `07_strategy/da_reviews/`
- `DA_review`
- `prior devil's advocate`
- `last review`
- `re-review`
- `DECISION_LOG`

If any appear, emit `[ISOLATION-BREACH] prior DA context: <substring>` and HALT.

### Check 3: Case theory references

Banned substrings:

- `CASE_THEORY.md`
- `LEGAL_PLAYBOOK.md`
- `SETTLEMENT_ECONOMICS.md`
- `CURRENT_STATUS.md`
- `the theme of the case is`
- `our strategy is`

If any appear, emit `[ISOLATION-BREACH] strategic context: <substring>` and HALT.

### Check 4: User opinion leakage

Banned phrases in any payload field:

- "important"
- "critical"
- "must win"
- "urgent"
- "the user wants"
- "the lawyer thinks"

If any appear, emit `[ISOLATION-BREACH] user opinion leakage: <phrase>` and HALT.

### Check 5: Payload structural completeness

Required top-level fields:

- `argument_id` (string, non-empty)
- `argument_text` (string, non-empty, >50 chars)
- `facts` (array, ≥1 entry)
- `laws` (array, ≥1 entry)
- `forum` (string)
- `stakes` (string or number)
- `output_path` (string, ends with `.md`)

If any is missing, emit `[INCOMPLETE-PAYLOAD] missing: <field>` and HALT.

---

## Acceptable payload schema

```yaml
argument_id: SA-31
argument_text: |
  The opposing party has engaged in a pattern of conduct that, when taken
  as a whole, constitutes systematic bad faith. The conduct includes
  <element 1>, <element 2>, ..., <element N>. Each element individually
  may not rise to actionable bad faith, but the pattern is probative.
facts:
  - pf_id: PF-A29
    category: A
    text: "On <date>, the opposing party <did X>."
    source: "<source file path or URL>"
    grade: A1
  - pf_id: PF-A30
    category: A
    text: "On <date>, the opposing party <did Y>."
    source: "<source file path or URL>"
    grade: B2
laws:
  - article_id: <abstract-article-id>
    verbatim_text: |
      <exact statute text from the active law pack's core/ file>
    sha256: a1b2c3d4e5f60718
    source_primary: https://example.gov/law/<article>
forum: civil court
stakes: "€2,960 (principal) + procedural costs"
output_path: 07_strategy/da_reviews/DA_SA31_2026-04-08.md
```

## Examples of REJECTED payloads

### Example 1: strategic framing in argument_text

```yaml
argument_text: |
  This is the strongest argument in our case. The pattern of bad faith is
  undeniable and our case theory depends on it. Per the playbook...
```

Response: `[ISOLATION-BREACH] strategic framing in argument_text: strongest argument, our case theory, the playbook`

### Example 2: prior DA review referenced

```yaml
argument_text: |
  <argument text>
notes: |
  See the prior DA review from 2026-03-01 which rated this argument SOUND.
```

Response: `[ISOLATION-BREACH] prior DA context: prior DA review`

### Example 3: incomplete payload

```yaml
argument_id: SA-31
argument_text: "..."
facts: []
```

Response: `[INCOMPLETE-PAYLOAD] missing: laws, forum, stakes, output_path`

---

## How to build a valid payload

If you're the dispatcher (e.g., `/lex-harness:devil <id>` command or `document-production` Step 4):

1. Read the argument file from `06_claims_and_defenses/` or `07_strategy/`
2. Extract ONLY the argument prose — strip all strategic framing, all "this is important" language, all references to prior reviews
3. Extract the list of PF IDs it cites
4. For each PF ID, read the entry from `PROVEN_FACTS_REGISTER.md` and copy the text + source + grade
5. Extract the list of article IDs it cites
6. For each article ID, read the file from the active law pack and copy the verbatim text + sha256 + source_primary
7. Determine the forum and the stakes from the argument context
8. Compute `output_path` as `07_strategy/da_reviews/DA_<argument-id>_<YYYY-MM-DD>.md`
9. Dispatch via Task tool with the payload above

DO NOT include:

- Paths to strategy files
- Prior DA review content
- Case theory references
- Settlement numbers as framing
- Your personal opinion of the argument

---

## When the skill halts, what do you do?

If the skill returns `[ISOLATION-BREACH]`:

1. Read the breach reason
2. Rebuild the payload stripping the identified contamination
3. Re-dispatch

If the skill returns `[INCOMPLETE-PAYLOAD]`:

1. Read the missing fields list
2. Populate them from the argument + the active law pack
3. Re-dispatch

Never modify the skill to be "more forgiving." The isolation rule is the whole reason this skill exists.
EOF
```

- [ ] **Step 6: Verify both files**

```bash
ls skills/devil-advocate/SKILL.md skills/devil-advocate/references/isolation-rule.md
wc -l skills/devil-advocate/SKILL.md skills/devil-advocate/references/isolation-rule.md
```

Expected: 2 files exist.

- [ ] **Step 7: Commit**

```bash
git add skills/devil-advocate/
git commit -s -m "$(cat <<'EOF'
feat(skills): devil-advocate v1.0 + isolation rule (T18)

New skill that refuses to run without strict isolation. A session-aware
devil's advocate is useless — it absorbs the user's framing and produces
sycophantic agreement. This skill enforces an ISOLATION-BREACH halt if
its dispatch payload contains strategy memos, prior DA reviews, case
theory, or user opinion leakage.

- SKILL.md description ≤1024 chars (Codex hard limit)
- Refuses with [ISOLATION-BREACH] on contamination detection
- Refuses with [INCOMPLETE-PAYLOAD] on missing required fields
- Output format: per-argument DA review file (frontmatter + counter-
  arguments rated HIGH/MEDIUM/LOW + holes in factual chain + verdict
  SOUND/NEEDS-WORK/DROP + 2-3 sentence rationale)
- references/isolation-rule.md documents the 5-check contamination
  detection algorithm + acceptable payload schema + rejected-payload
  examples + dispatcher instructions
- reads_from: [] (the skill only reads the payload — nothing else)
- handoff_to: [] (the skill is a terminal — reviews are consumed by
  the dispatcher)
- Body contains zero jurisdiction-specific content (PR-01 / PR-03)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 19: `/lex-harness:init <jurisdiction>` slash command

**Files:**
- Create: `~/Developer/projects/lex-harness/commands/init.md`

The `/lex-harness:init` command is the first thing a new user runs. It scaffolds a complete case repository in the user's current working directory: folder structure, the active jurisdiction's law pack, git pre-commit hook, case metadata, and the limitation deadline.

Per PR-04, the command is **reentrant** — re-running with `--update-pack` refreshes the law pack without destroying case content.

Per design spec §6.1, the command:

1. Confirms the CWD is empty (or prompts)
2. Copies `${CLAUDE_PLUGIN_ROOT}/templates/case_skeleton/` into CWD
3. Copies `${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/` into `<cwd>/05_legal_research/law_pack/`
4. Copies `${CLAUDE_PLUGIN_ROOT}/templates/pre-commit` into `<cwd>/.githooks/pre-commit` and sets `core.hooksPath`
5. Prompts for case metadata (claimant, opposing party, amount, key dates)
6. Populates `01_case_summary/CASE_OVERVIEW.md` from the answers
7. Computes the limitation deadline from the jurisdiction's `limitation_periods.yaml` and appends it to `DEADLINE_REGISTER.md` as DL-01
8. Commits the scaffold with a HUMAN commit (no AI trailer — so the git hook allows it)
9. Prints next-steps

- [ ] **Step 1: Create the commands directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p commands
```

- [ ] **Step 2: Write `commands/init.md`**

```bash
cat > commands/init.md <<'EOF'
---
description: Scaffold a new legal case repo with the active jurisdiction's law pack, folder structure, git pre-commit hook, and initial metadata. Reentrant via --update-pack flag (PR-04).
argument-hint: <jurisdiction> [--update-pack]
---

# /lex-harness:init

Usage:

```
/lex-harness:init <jurisdiction>
/lex-harness:init <jurisdiction> --update-pack
```

Example:

```
/lex-harness:init greece
/lex-harness:init greece --update-pack
```

## What this command does

This command scaffolds a legal case repository in the current working directory. After running it, the user has a complete case skeleton ready for `/lex-harness:fact` and the `legal-strategy` skill.

The command is reentrant per PR-04. Re-running with `--update-pack` refreshes `05_legal_research/law_pack/` from the plugin without destroying case content.

## Action sequence

### Step 1: Parse arguments

1. Parse `<jurisdiction>` from `$1` (the first positional argument)
2. Parse `--update-pack` flag if present
3. If `<jurisdiction>` is missing, print:

   ```
   Usage: /lex-harness:init <jurisdiction> [--update-pack]
   Available jurisdictions: $(ls ${CLAUDE_PLUGIN_ROOT}/law-packs/ | grep -v '^_\|^README')
   ```

   and halt.

4. Verify `${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/` exists. If not, print:

   ```
   Error: no law pack for '<jurisdiction>' at ${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/
   Available: $(ls ${CLAUDE_PLUGIN_ROOT}/law-packs/ | grep -v '^_\|^README')
   See CONTRIBUTING.md for how to add a jurisdiction pack.
   ```

   and halt.

### Step 2: Check CWD state

1. Read the current directory. If it's the user's home directory or `/`, halt with:

   ```
   Error: refusing to init in $HOME or /. cd to an empty directory first.
   ```

2. If `--update-pack` is set:
   - Verify `<cwd>/01_case_summary/CASE_OVERVIEW.md` exists (this is the marker for an initialised case repo)
   - If it doesn't exist, halt with "Error: --update-pack requires an existing case repo. Run /lex-harness:init <jurisdiction> first."
   - Skip to Step 6 (update the law pack only)
3. If `--update-pack` is NOT set:
   - Count files in CWD. If non-empty, prompt: "Directory <cwd> is not empty. Continue? (y/N)"
   - If the user answers anything other than `y`, halt.

### Step 3: Copy the case skeleton

Use bash to copy the skeleton:

```bash
cp -R "${CLAUDE_PLUGIN_ROOT}/templates/case_skeleton/." "."
```

This creates `01_case_summary/` through `09_ai_research/` plus the top-level files (`CURRENT_STATUS.md`, `CLAUDE.md`, etc.) in CWD.

### Step 4: Copy the law pack

```bash
mkdir -p "05_legal_research/law_pack"
cp -R "${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/." "05_legal_research/law_pack/"
```

### Step 5: Install the git pre-commit hook

```bash
git init -b main 2>/dev/null || true
mkdir -p .githooks
cp "${CLAUDE_PLUGIN_ROOT}/templates/pre-commit" ".githooks/pre-commit"
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
```

Verify:

```bash
git config --get core.hooksPath
ls -la .githooks/pre-commit
```

Expected: prints `.githooks` and shows an executable pre-commit file.

### Step 6: Prompt for case metadata

Prompt the user (one question per line, wait for each answer):

1. "Claimant / your party name:"
2. "Opposing party name:"
3. "Claimant role in dispute (tenant, consumer, employee, creditor, plaintiff, ...):"
4. "Dispute subject (one line, e.g. 'rental deposit dispute', 'employment termination'):"
5. "Monetary amount at stake (e.g. €2,960 or N/A):"
6. "Accrual event date (when did the cause of action arise?) YYYY-MM-DD:"
7. "Key departure / termination / breach date (if different) YYYY-MM-DD or N/A:"
8. "Forum preference for next step (civil-court / consumer-ombudsman / data-protection-authority / criminal / not-sure):"

Store each answer in a local variable.

### Step 7: Populate CASE_OVERVIEW.md

Read the template at `01_case_summary/CASE_OVERVIEW.md` (copied from the case skeleton in Step 3). Replace the placeholders:

- `<<CLAIMANT>>` → claimant name
- `<<OPPOSING_PARTY>>` → opposing party name
- `<<CLAIMANT_ROLE>>` → claimant role
- `<<DISPUTE_SUBJECT>>` → dispute subject
- `<<AMOUNT>>` → monetary amount
- `<<ACCRUAL_EVENT_DATE>>` → accrual event date
- `<<BREACH_DATE>>` → breach/termination date
- `<<JURISDICTION>>` → the `<jurisdiction>` argument
- `<<PACK_VERSION>>` → read from `05_legal_research/law_pack/pack.json` → `.version`
- `<<INIT_DATE>>` → today in ISO format

### Step 8: Compute limitation deadlines → DEADLINE_REGISTER.md

1. Read `05_legal_research/law_pack/limitation_periods.yaml`
2. Find the entry that matches the dispute subject (e.g., "rental deposit" → the rental-related limitation; "employment" → the employment limitation)
3. If no match, prompt the user: "Could not auto-match dispute subject to a limitation period. Please pick one from the list:" and show the available `limitations[].id` options
4. Compute the deadline: `accrual_event_date + period_days`
5. Read the template `DEADLINE_REGISTER.md` and replace the DL-01 placeholder block with:

   ```markdown
   ## DL-01 — Statutory limitation period

   - **Source article:** <statute id from the matched entry>
   - **Period:** <period_days> days from <accrual_event>
   - **Accrual event date:** <user-supplied date>
   - **Deadline:** <computed date>
   - **Days remaining:** <computed> (re-compute every session)
   - **Interruption methods:** <list from limitation_periods.yaml>
   - **Status:** open
   ```

### Step 9: Populate CURRENT_STATUS.md

Replace the placeholders in `CURRENT_STATUS.md` with:

- Phase: "Phase 1 — Initialisation"
- Last action: "Case initialised via /lex-harness:init <jurisdiction>"
- Next action: "Review CASE_OVERVIEW.md + add facts via /lex-harness:fact"
- Critical deadlines: "DL-01 (<computed date>, <days remaining> days)"

### Step 10: Commit as a HUMAN commit (no AI trailer)

The git hook from Step 5 blocks AI-trailered commits to `PROVEN_FACTS_REGISTER.md`. The init commit touches PROVEN_FACTS_REGISTER.md (the empty template), so it MUST be a human commit:

```bash
git add .
git commit -s -m "$(cat <<'MSG'
Initialise case repo via lex-harness

- Jurisdiction: <jurisdiction>
- Law pack version: <pack version>
- Limitation deadline (DL-01): <deadline>
MSG
)"
```

NO `Co-Authored-By: Claude` trailer. The hook will reject it if you add one. This is the ONLY way to get the empty PROVEN_FACTS_REGISTER.md into the initial commit.

### Step 11: Print next-steps

Print exactly this to the user:

```
lex-harness init complete.

Jurisdiction: <jurisdiction> (pack v<version>)
Case repo:    <cwd>
Limitation:   DL-01 — <deadline> (<days> days remaining)

Next steps:
  1. Review 01_case_summary/CASE_OVERVIEW.md and fill any N/A fields
  2. Add facts via /lex-harness:fact (appends to PENDING_FACTS.md)
  3. Ask the legal-strategy skill: "what's my next move?"
  4. Read CLAUDE.md for the project-specific conventions

Reentrant update:
  /lex-harness:init <jurisdiction> --update-pack

Refreshes 05_legal_research/law_pack/ without touching case content.
```

---

## --update-pack mode (Step 6 alternate path)

When `--update-pack` is set, skip Steps 2-5, 6-11. Instead:

1. Confirm `<cwd>/01_case_summary/CASE_OVERVIEW.md` exists
2. Back up the current law pack: `mv 05_legal_research/law_pack 05_legal_research/law_pack.bak.$(date +%s)`
3. Copy the new law pack: `cp -R "${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/." "05_legal_research/law_pack/"`
4. Compare old and new pack.json versions. Append to `CHANGELOG.md` (if present) or create one:

   ```markdown
   ## <date> — law pack update

   - Pack: <jurisdiction>
   - Old version: <old>
   - New version: <new>
   - Backup: <backup-path>
   ```

5. Scan the case repo for references to any law pack files that were moved or renamed. Flag them as `[REQUIRES-REVIEW]` and list in a summary.
6. Print:

   ```
   Law pack updated.
   Old: <old-version>
   New: <new-version>
   Backup: <backup-path>
   Files flagged [REQUIRES-REVIEW]: <count>
   ```

7. Do NOT commit — let the user review changes first.

---

## Error handling

| Error | Response |
|---|---|
| No jurisdiction argument | Print usage + available packs; halt |
| Unknown jurisdiction | Print error + available packs; halt |
| CWD is $HOME or / | Refuse |
| CWD not empty and user declines | Halt |
| Law pack fails schema validation | Halt with validation errors |
| Git hook install fails | Halt with git error |
| User answers missing for required metadata | Re-prompt (up to 3 times, then halt) |
| Limitation period auto-match fails | Prompt user to pick from list |

---

## Idempotency

Running `/lex-harness:init greece` twice in a row:

- First run: full scaffold, human commit
- Second run: detects the non-empty CWD, prompts "continue? (y/N)". If user answers `n`, halts with no changes. If `y`, overwrites the skeleton (which is idempotent — the files are the same) but DOES NOT re-prompt for metadata (detects existing `CASE_OVERVIEW.md` and preserves it).

Running `/lex-harness:init greece --update-pack` twice in a row:

- First run: refreshes law pack, creates backup
- Second run: refreshes law pack again, creates another backup (timestamp differs)
- Both are safe — case content is never touched.
EOF
```

- [ ] **Step 3: Verify the command file**

```bash
ls commands/init.md
wc -l commands/init.md
head -5 commands/init.md
```

Expected: file exists, ~220 lines, frontmatter starts with `---` and `description:`.

- [ ] **Step 4: Verify the description length (soft limit, ~250 chars for commands)**

```bash
python3 - <<'PY'
import re
with open('commands/init.md') as f:
    content = f.read()
m = re.search(r'description:\s*(.+)', content)
desc = m.group(1).strip()
print(f"description length: {len(desc)} chars")
print(f"description: {desc}")
PY
```

Expected: description ≤250 chars (commands don't have a hard limit but keep them short).

- [ ] **Step 5: Commit**

```bash
git add commands/init.md
git commit -s -m "$(cat <<'EOF'
feat(commands): /lex-harness:init <jurisdiction> (T19)

Scaffolds a new legal case repo with the active jurisdiction's law
pack, folder structure, git pre-commit hook, and initial metadata.

- Reentrant via --update-pack flag (PR-04): refreshes law pack
  without destroying case content
- 11-step action sequence: parse args, check CWD, copy skeleton,
  copy law pack, install git hook, prompt metadata, populate
  CASE_OVERVIEW, compute limitation deadline, populate
  CURRENT_STATUS, human commit (no AI trailer so the git hook
  allows PROVEN_FACTS_REGISTER.md in the initial commit), print
  next-steps
- Alternate --update-pack path: backup old pack, copy new pack,
  compare versions, flag moved files [REQUIRES-REVIEW], no commit
- Error handling table + idempotency notes

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 20: `/lex-harness:fact` slash command

**Files:**
- Create: `~/Developer/projects/lex-harness/commands/fact.md`

The `/lex-harness:fact` command is the AI's propose-a-fact entry point. It prompts for category + source + fact text, generates the next PF ID, and appends a YAML entry to `06_claims_and_defenses/PENDING_FACTS.md`.

**Critical rule:** the command MUST append to `PENDING_FACTS.md`, NEVER to `PROVEN_FACTS_REGISTER.md`. The git pre-commit hook blocks AI commits to PROVEN_FACTS_REGISTER (T1 write-path isolation, D19, D30). The AI proposes; a separate human commit (without the `Co-Authored-By: Claude` trailer) promotes.

The 11 categories per the design spec §7a and the schema in T23:

| Category | Meaning |
|---|---|
| **A** | Admitted / uncontroverted facts |
| **B** | Behaviour / conduct |
| **C** | Correspondence |
| **D** | Documents (contracts, invoices, statutes as applied) |
| **E** | Evidence (physical, photo, file) |
| **F** | Forensic (accounting, invoice anomalies) |
| **G** | GDPR / data protection admissions |
| **H** | Hearsay-ish (secondhand, useful only with corroboration) |
| **P** | Proven (photos with EXIF, hashed + timestamped) |
| **T** | Testimony (first-party witness statements) |
| **N** | Negative facts (absence is evidence) |

- [ ] **Step 1: Write `commands/fact.md`**

```bash
cat > commands/fact.md <<'EOF'
---
description: Append a proposed fact to PENDING_FACTS.md with correct schema (category, source, text). The AI proposes; a human reviews and promotes to PROVEN_FACTS_REGISTER in a separate commit.
argument-hint: (interactive)
---

# /lex-harness:fact

Usage:

```
/lex-harness:fact
```

No arguments. The command is interactive.

## What this command does

Appends a proposed fact to `06_claims_and_defenses/PENDING_FACTS.md`. It does NOT write to `PROVEN_FACTS_REGISTER.md` — that file is protected by the git pre-commit hook (T1 write-path isolation). A human reviews and promotes in a separate commit WITHOUT the `Co-Authored-By: Claude` trailer.

## Why propose, not write

The architecture rule (D19 / D30) is that AI may propose facts but never write them to the authoritative register. A session-aware AI will happily fabricate facts, misread sources, or confuse categories. The human-review gate prevents this at the git layer.

If the AI tries to commit a change to `PROVEN_FACTS_REGISTER.md` with the `Co-Authored-By: Claude` trailer, the git hook rejects the commit with `[T1-WRITE-VIOLATION]`. The AI's only safe write target is `PENDING_FACTS.md`.

## Action sequence

### Step 1: Confirm the case repo is initialised

Check that `06_claims_and_defenses/PENDING_FACTS.md` exists. If not, print:

```
Error: no PENDING_FACTS.md found. Run /lex-harness:init <jurisdiction> first.
```

and halt.

### Step 2: Prompt for category

Present the category table to the user:

```
Pick a category for this fact:

  A — Admitted / uncontroverted facts
  B — Behaviour / conduct
  C — Correspondence (email, letter, WhatsApp)
  D — Documents (contracts, invoices, statutes as applied)
  E — Evidence (physical, photo, file)
  F — Forensic (accounting, invoice anomalies)
  G — GDPR / data protection admissions
  H — Hearsay-ish (use only with corroboration)
  P — Proven (photos with EXIF, hashed + timestamped)
  T — Testimony (first-party witness statements)
  N — Negative facts (absence is evidence)

Category:
```

Wait for the user's answer. Accept a single letter (case-insensitive). Reject anything else and re-prompt.

### Step 3: Prompt for source

Prompt:

```
Source (file path, URL, or human-readable reference):
```

Wait for the answer. The source MUST be:

- A file path (relative to the case repo root), OR
- A URL (http:// or https://), OR
- A human-readable reference with enough specificity to locate the source (e.g., "WhatsApp message from X on 2026-03-01 at 14:22")

If the input is empty, re-prompt.

### Step 4: Prompt for the fact text

Prompt:

```
Fact text (one factual claim, no strategic framing):
```

Wait for the answer. The text must:

- Be a single factual claim
- Be ≥10 characters
- NOT contain strategic framing words ("strong", "weak", "critical", "important", "our", "we believe")

If the text contains any framing word, warn and re-prompt.

### Step 5: Generate the next PF ID

1. Read `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` and scan for all `PF-<category><number>` IDs
2. Read `06_claims_and_defenses/PENDING_FACTS.md` and scan for all `PF-<category><number>` IDs
3. Find the highest number for the selected category (e.g., PF-C45 → 45)
4. Increment: the next ID is `PF-<category><number+1>` (e.g., PF-C46)
5. If no IDs exist for the category, start at 01 (e.g., PF-C01)

### Step 6: Append to PENDING_FACTS.md

Append this block to `06_claims_and_defenses/PENDING_FACTS.md`:

```yaml
---
- id: <PF-ID>
  category: <letter>
  text: |
    <fact text>
  source: <source>
  status: pending
  proposed_by: AI (via /lex-harness:fact)
  proposed_date: <YYYY-MM-DD>
  reviewer: null
  reviewed_date: null
  promoted_to_register: false
---
```

Use the current UTC date for `proposed_date`.

### Step 7: Print confirmation

```
Proposed fact <PF-ID> appended to 06_claims_and_defenses/PENDING_FACTS.md

Category: <letter>
Text:     <fact text>
Source:   <source>

IMPORTANT: This is a PROPOSAL only. A human reviewer must:
  1. Verify the fact against the source
  2. Move the entry from PENDING_FACTS.md to PROVEN_FACTS_REGISTER.md
  3. Commit the promotion WITHOUT a Co-Authored-By: Claude trailer
     (the git pre-commit hook blocks AI commits to PROVEN_FACTS_REGISTER.md)

The AI cannot promote its own facts. That's by design (D19 / D30).
```

---

## Why AI cannot promote

The whole point of the T1 isolation rule is that the AI's ability to propose facts is decoupled from the authority to certify them. An AI that can write to PROVEN_FACTS_REGISTER can (and will, sooner or later) introduce:

- Hallucinated facts
- Misread sources
- Wrong category assignments
- Facts that contradict existing register entries

The git hook makes this architecturally impossible. The AI writes to PENDING_FACTS. A human reads the entry, verifies the source, and makes a separate commit to PROVEN_FACTS_REGISTER. That human commit has no AI trailer, so the hook allows it.

---

## Example session

```
User: /lex-harness:fact

AI: Pick a category for this fact:
    A — Admitted / uncontroverted facts
    B — Behaviour / conduct
    C — Correspondence
    D — Documents
    E — Evidence
    F — Forensic
    G — GDPR / data protection admissions
    H — Hearsay-ish
    P — Proven
    T — Testimony
    N — Negative facts
    Category:

User: C

AI: Source (file path, URL, or human-readable reference):

User: 03_correspondence/emails/05_deposit_return.md#L42

AI: Fact text (one factual claim, no strategic framing):

User: The opposing party sent an email on 2026-01-29 stating "the deposit will be refunded after the inspection report is finalised"

AI: Proposed fact PF-C48 appended to 06_claims_and_defenses/PENDING_FACTS.md

    Category: C
    Text:     The opposing party sent an email on 2026-01-29 stating "the deposit will be refunded after the inspection report is finalised"
    Source:   03_correspondence/emails/05_deposit_return.md#L42

    IMPORTANT: This is a PROPOSAL only. A human reviewer must:
      1. Verify the fact against the source
      2. Move the entry from PENDING_FACTS.md to PROVEN_FACTS_REGISTER.md
      3. Commit the promotion WITHOUT a Co-Authored-By: Claude trailer
```
EOF
```

- [ ] **Step 2: Verify the file**

```bash
ls commands/fact.md
wc -l commands/fact.md
head -5 commands/fact.md
```

Expected: file exists; ~160 lines.

- [ ] **Step 3: Commit**

```bash
git add commands/fact.md
git commit -s -m "$(cat <<'EOF'
feat(commands): /lex-harness:fact (T20)

Interactive command to append a proposed fact to PENDING_FACTS.md.
The AI proposes; a human reviews and promotes to
PROVEN_FACTS_REGISTER.md in a separate commit WITHOUT the
Co-Authored-By: Claude trailer (the git pre-commit hook rejects
AI-trailered commits to PROVEN_FACTS_REGISTER).

- 7-step action sequence: confirm init, prompt category, prompt
  source, prompt fact text, generate next PF ID, append YAML to
  PENDING_FACTS.md, print confirmation
- 11 categories (A-H, P, T, N) matching PROVEN_FACTS_REGISTER schema
- Rejects fact text containing strategic framing words
- Writes ONLY to PENDING_FACTS.md — never to PROVEN_FACTS_REGISTER
- Example session in the command body

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 21: `/lex-harness:devil <argument-id>` slash command

**Files:**
- Create: `~/Developer/projects/lex-harness/commands/devil.md`

The `/lex-harness:devil` command dispatches the `devil-advocate` skill on a specific argument. Per design spec §6.3, it:

1. Locates the argument file in `07_strategy/` or `06_claims_and_defenses/`
2. Extracts the argument text + referenced PF IDs + cited law articles
3. Fetches verbatim text for each cited law from the active law pack
4. Builds the isolation payload: `{argument, facts, laws, forum, stakes, output_path}`
5. Dispatches `devil-advocate` via the Task tool with the payload
6. Saves the result to `07_strategy/da_reviews/DA_<argument-id>_<YYYY-MM-DD>.md`
7. Updates `07_strategy/core/DECISION_LOG.md` with the DA outcome

The key role of this command is **payload sanitisation** — it must strip strategic framing before passing to the devil-advocate skill. Otherwise the skill halts with `[ISOLATION-BREACH]`.

- [ ] **Step 1: Write `commands/devil.md`**

```bash
cat > commands/devil.md <<'EOF'
---
description: Dispatch devil-advocate skill on a specific argument (CH/CC/SA file or element) in isolated subagent context with only raw facts + cited law + argument text. No session state inheritance.
argument-hint: <argument-id>
---

# /lex-harness:devil

Usage:

```
/lex-harness:devil <argument-id>
```

Examples:

```
/lex-harness:devil SA-31
/lex-harness:devil SA-31-E01
/lex-harness:devil CC3
/lex-harness:devil CH1
```

## What this command does

Dispatches the `devil-advocate` skill in an isolated subagent context. The skill produces a DA review file with counter-arguments, holes in the factual chain, and a verdict (SOUND / NEEDS-WORK / DROP).

This command is the CORRECT way to invoke devil-advocate. Calling the skill directly without this command risks feeding it a contaminated payload — prior session context, strategic framing, case theory references. The skill will halt with `[ISOLATION-BREACH]`.

The command's job is **payload sanitisation**: extract bare facts + bare law + bare argument text, strip all framing, build the payload, dispatch via the Task tool.

## Action sequence

### Step 1: Parse the argument ID

1. Read `$1` (the argument ID argument)
2. If missing, print:

   ```
   Usage: /lex-harness:devil <argument-id>

   Examples:
     /lex-harness:devil SA-31
     /lex-harness:devil CH1
     /lex-harness:devil CC3
   ```

   and halt.

3. Normalise the ID (uppercase, strip whitespace)

### Step 2: Locate the argument file

Search these locations in order:

1. `07_strategy/<ARGUMENT-ID>.md` (e.g., `07_strategy/SA-31.md`)
2. `07_strategy/<ARGUMENT-ID>_*.md` (e.g., `07_strategy/SA31_SYSTEMATIC_BAD_FAITH.md`)
3. `06_claims_and_defenses/<ARGUMENT-ID>.md` (e.g., `06_claims_and_defenses/CH1.md`)
4. `06_claims_and_defenses/<ARGUMENT-ID>_*.md`

If none found, print:

```
Error: argument file for <argument-id> not found.
Searched:
  - 07_strategy/<ARGUMENT-ID>.md
  - 07_strategy/<ARGUMENT-ID>_*.md
  - 06_claims_and_defenses/<ARGUMENT-ID>.md
  - 06_claims_and_defenses/<ARGUMENT-ID>_*.md
```

and halt.

### Step 3: Extract the argument text

Read the located file. Extract:

- The argument body (the main prose section — typically between the first H2 and the "Proven Facts" or "Citations" section)
- Strip all strategic framing:
  - Remove any line containing "strong", "weak", "critical", "important", "our theory", "we believe", "the theme is"
  - Remove any reference to `DECISION_LOG`, `CASE_THEORY`, `LEGAL_PLAYBOOK`, `SETTLEMENT_ECONOMICS`
  - Remove any reference to prior DA reviews (`DA_*.md`, "previously reviewed", "last review")
  - Remove author annotations like "TODO", "FIXME", "[verify]"
- The result is the sanitised `argument_text` for the payload

### Step 4: Extract PF references

Scan the argument file for all `PF-<letter><number>` patterns. For each unique PF ID:

1. Look up the entry in `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md`
2. Extract: `id`, `category`, `text`, `source`, `grade`
3. Append to the payload's `facts:` array

If any PF ID is not found in the register, add it to a warning list and continue.

### Step 5: Extract law article references

Scan the argument file for citations to law pack articles. The format depends on the argument file's style — typically:

- `<article-id>` in brackets or parentheses
- A line starting with `Legal basis:` followed by article IDs
- A section header titled `## Legal basis` or `## Statutes cited`

For each unique article ID:

1. Locate the file in `05_legal_research/law_pack/core/<id>.md` or `05_legal_research/law_pack/modules/<module>/<id>.md`
2. Read the frontmatter to get `sha256` and `source_primary`
3. Extract the verbatim text section (typically under a `## Verbatim text` H2)
4. Append to the payload's `laws:` array

If any article is not found in the law pack, HALT with an error: "Article <id> not found in active law pack. Either fix the citation or add the article to the law pack."

### Step 6: Determine forum + stakes

1. Look for a `forum:` field in the argument file's frontmatter. If present, use it.
2. Otherwise, look for a section header like `## Forum` or `## Target forum`. Extract the value.
3. Otherwise, default to `civil court` and emit a warning.
4. For stakes, look for a `stakes:` or `amount:` field in frontmatter, or a line like "Amount at stake: €X" in the body. If not found, read `07_strategy/core/SETTLEMENT_ECONOMICS.md` for the total claim and use that. If that file is absent, use "unspecified".

### Step 7: Compute output path

```
output_path = 07_strategy/da_reviews/DA_<ARGUMENT-ID>_<YYYY-MM-DD>.md
```

If the file already exists for today, append `_v2`, `_v3`, etc. until unique.

### Step 8: Build the payload

Construct the YAML payload per the schema in `skills/devil-advocate/references/isolation-rule.md`:

```yaml
argument_id: <normalised id>
argument_text: |
  <sanitised body>
facts:
  - pf_id: <id>
    category: <letter>
    text: "<verbatim text>"
    source: "<source>"
    grade: <grade>
laws:
  - article_id: <id>
    verbatim_text: |
      <verbatim>
    sha256: <hex>
    source_primary: <url>
forum: <forum>
stakes: <stakes>
output_path: <path>
```

### Step 9: Dispatch devil-advocate via Task tool

Call the Task tool with:

- `subagent_type`: `general-purpose` (or the specific `devil-advocate` agent type if the plugin registered one)
- `description`: "DA review of <argument-id>"
- `prompt`: the serialised payload above + the instruction "Invoke the devil-advocate skill with this payload and write the review to `<output_path>`."

Wait for the subagent to complete.

### Step 10: Read and verify the DA review file

1. Read the file at `output_path`
2. Verify the frontmatter has `isolation_verified: true`
3. Verify the verdict is one of `SOUND`, `NEEDS-WORK`, `DROP`
4. If the file doesn't exist or lacks the required frontmatter, print an error and halt

### Step 11: Update DECISION_LOG.md

Append an entry to `07_strategy/core/DECISION_LOG.md`:

```markdown
## DL-<next-number> — DA review of <argument-id>

- **Date:** <YYYY-MM-DD>
- **Argument:** <argument-id>
- **Verdict:** <verdict>
- **DA review file:** <output_path>
- **Action:** <from the DA review's "Recommended next action" section>
```

### Step 12: Print summary

```
Devil-advocate review complete.

Argument:   <argument-id>
Verdict:    <verdict>
Review:     <output_path>
DECISION_LOG entry: DL-<number>

Recommended next action:
<action from the review>
```

---

## Payload sanitisation checklist

Before dispatching, the command MUST verify the payload contains NONE of:

- [x] References to `07_strategy/da_reviews/`
- [x] References to `CASE_THEORY`, `LEGAL_PLAYBOOK`, `DECISION_LOG`, `SETTLEMENT_ECONOMICS`
- [x] Strategic framing words: "strong", "weak", "winning", "our theory", "we believe", "critical", "important"
- [x] References to prior DA reviews
- [x] User-opinion phrases: "I think", "in my view", "the user wants"
- [x] Author annotations: "TODO", "FIXME", "[verify]"

If any slip through, the devil-advocate skill will halt with `[ISOLATION-BREACH]`. The fix is to rebuild the payload more aggressively.

---

## Error handling

| Error | Response |
|---|---|
| No argument ID given | Print usage; halt |
| Argument file not found | Print search paths; halt |
| PF ID not in register | Warning, continue (log in payload) |
| Article ID not in law pack | HALT — fix the citation or add the article |
| DA subagent returns without a file | Print error; halt |
| DA file has `isolation_verified: false` | Print error; halt |
| DA file has no verdict | Print error; halt |

---

## Example session

```
User: /lex-harness:devil CH1

AI: Locating argument file...
    Found: 06_claims_and_defenses/CH1_cleaning_268.md

    Extracting argument text (sanitised)...
    Extracting 5 PF references...
    Extracting 3 law article references...
    Building isolation payload...
    Dispatching devil-advocate subagent...

    [subagent runs in isolation]

    DA review complete.

    Argument:   CH1
    Verdict:    NEEDS-WORK
    Review:     07_strategy/da_reviews/DA_CH1_2026-04-08.md
    DECISION_LOG entry: DL-47

    Recommended next action:
    Revise CH1 to address CA-1 (HIGH): the cleaning fee is within the
    contractual cap. Without evidence of excess, the argument is
    vulnerable to a summary dismissal.
```
EOF
```

- [ ] **Step 2: Verify the file**

```bash
ls commands/devil.md
wc -l commands/devil.md
```

Expected: file exists; ~220 lines.

- [ ] **Step 3: Commit**

```bash
git add commands/devil.md
git commit -s -m "$(cat <<'EOF'
feat(commands): /lex-harness:devil <argument-id> (T21)

Dispatches devil-advocate skill in isolated subagent context on a
specific argument. The command's primary role is payload sanitisation
— strip all strategic framing before passing to the skill, otherwise
the skill halts with [ISOLATION-BREACH].

- 12-step action sequence: parse ID, locate file, extract sanitised
  argument text, extract PF references, extract law articles, fetch
  verbatim law text, determine forum+stakes, compute output path,
  build payload, dispatch via Task tool, read+verify DA review,
  update DECISION_LOG, print summary
- Payload sanitisation checklist (6 categories of banned content)
- Error handling table covers missing files, missing PFs, missing
  articles, subagent failures, isolation breaches
- Example session shows a NEEDS-WORK verdict and the recommended
  next action

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 22: `templates/case_skeleton/` (10 directories with READMEs)

**Files:**
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/01_case_summary/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/02_contracts/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/03_correspondence/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/04_evidence/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/04_evidence/testimony/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/05_legal_research/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/06_claims_and_defenses/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/07_strategy/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/08_drafts/README.md`
- Create: `~/Developer/projects/lex-harness/templates/case_skeleton/09_ai_research/README.md`

The case skeleton is copied verbatim into a new case repo by `/lex-harness:init`. Every directory has a README explaining what goes in it. The READMEs must be JURISDICTION-AGNOSTIC — no Greek terms, no country-specific law references.

- [ ] **Step 1: Create all 10 directories**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p templates/case_skeleton/01_case_summary
mkdir -p templates/case_skeleton/02_contracts
mkdir -p templates/case_skeleton/03_correspondence
mkdir -p templates/case_skeleton/04_evidence/testimony
mkdir -p templates/case_skeleton/05_legal_research
mkdir -p templates/case_skeleton/06_claims_and_defenses
mkdir -p templates/case_skeleton/07_strategy/core
mkdir -p templates/case_skeleton/07_strategy/da_reviews
mkdir -p templates/case_skeleton/08_drafts
mkdir -p templates/case_skeleton/09_ai_research
```

- [ ] **Step 2: Write `01_case_summary/README.md`**

```bash
cat > templates/case_skeleton/01_case_summary/README.md <<'EOF'
# 01_case_summary

> Single source of truth for the case overview. Keep this directory small and authoritative.

## What goes here

- `CASE_OVERVIEW.md` — parties, dispute subject, amount at stake, key dates, active jurisdiction, active law pack version. Generated by `/lex-harness:init`. One file, ≤200 lines.
- `CHARGES_OVERVIEW.md` — one-page summary of every claim and counterclaim, with links into `06_claims_and_defenses/`.
- `TIMELINE.md` — master chronological timeline of every dated event in the case. One line per event. Links to source files in `02_contracts/`, `03_correspondence/`, `04_evidence/`.

## What does NOT go here

- Argument drafts (→ `06_claims_and_defenses/` or `07_strategy/`)
- Source documents (→ `02_contracts/`, `03_correspondence/`, `04_evidence/`)
- Legal research (→ `05_legal_research/`)
- Finished drafts ready to send (→ `08_drafts/`)

## Editing rules

- `CASE_OVERVIEW.md` is updated when a fundamental case fact changes (party name, jurisdiction, amount). It is NOT a changelog — history lives in git.
- `TIMELINE.md` is append-only. When a new event is confirmed, add it in chronological order. Never delete entries — mark them `[SUPERSEDED]` with a reference to the new entry.
EOF
```

- [ ] **Step 3: Write `02_contracts/README.md`**

```bash
cat > templates/case_skeleton/02_contracts/README.md <<'EOF'
# 02_contracts

> Every signed agreement, extension, amendment, addendum, and side letter.

## What goes here

- Original contracts (PDFs, scans, photos)
- Extensions, renewals, amendments
- Side letters and addenda
- General terms and conditions attached to the contract
- Any document the opposing party tries to rely on as contractual

## Naming

Use: `<doc-type>_<party>_<YYYY-MM-DD>.<ext>`

Examples:
- `contract_main_2023-05-01.pdf`
- `extension_1_2024-05-01.pdf`
- `amendment_clause7_2025-02-14.pdf`

## Chain of custody

Every file in this directory MUST be listed in `04_evidence/CHAIN_OF_CUSTODY.log` with its SHA-256 hash. Use the `osint-investigation` skill's chain-of-custody protocol.
EOF
```

- [ ] **Step 4: Write `03_correspondence/README.md`**

```bash
cat > templates/case_skeleton/03_correspondence/README.md <<'EOF'
# 03_correspondence

> All communication between the parties.

## What goes here

- Email threads (exported as markdown + raw source)
- WhatsApp exports (text + attachments)
- Phone call logs (written up from memory soon after the call)
- Physical letters (scanned)
- Meeting notes from face-to-face discussions

## Structure

```
03_correspondence/
├── emails/
│   ├── 01_<topic>.md
│   ├── 02_<topic>.md
│   └── raw/                    # raw JSON/MIME for audit
├── whatsapp/
│   ├── <chat-name>.md
│   └── attachments/
├── phone_calls.md              # append-only log
└── meetings.md                 # append-only log
```

## Editing rules

- Emails, WhatsApp, and letters are source documents — never edit them. Add annotations in a separate file in `06_claims_and_defenses/` or `07_strategy/`.
- `phone_calls.md` and `meetings.md` are append-only. Every entry has a date, a participant list, and a brief summary. Do not edit past entries.
EOF
```

- [ ] **Step 5: Write `04_evidence/README.md`**

```bash
cat > templates/case_skeleton/04_evidence/README.md <<'EOF'
# 04_evidence

> All physical and documentary evidence — everything that is not a contract or correspondence.

## What goes here

- Photos (with EXIF preserved)
- Invoices, receipts, billing statements
- Screenshots of websites (with SHA-256 + RFC3161 timestamp)
- OSINT findings (under `osint/`)
- First-party witness testimony (under `testimony/`)
- EVIDENCE_INDEX.md — master index of every item, with an E-XXX identifier

## Structure

```
04_evidence/
├── EVIDENCE_INDEX.md           # master index: E-001 ... E-NNN
├── CHAIN_OF_CUSTODY.log        # append-only log of SHA-256 + timestamp for every file
├── photos/
├── invoices/
├── osint/                      # OSINT finding reports + captured content
└── testimony/                  # first-party witness statements
```

## Chain of custody

Every file under `04_evidence/` MUST have:

1. A SHA-256 hash logged in `CHAIN_OF_CUSTODY.log`
2. An RFC3161 trusted timestamp (see the `osint-investigation` skill's `references/chain-of-custody.md`)
3. An entry in `EVIDENCE_INDEX.md` with its E-XXX identifier

Files without all three are UNREGISTERED and MUST NOT be cited in any formal document.
EOF
```

- [ ] **Step 6: Write `04_evidence/testimony/README.md`**

```bash
cat > templates/case_skeleton/04_evidence/testimony/README.md <<'EOF'
# 04_evidence/testimony

> First-party witness statements. NOT public OSINT — these are statements collected directly from people (the claimant, family members, third-party witnesses).

## Why a separate directory

Testimony is not public OSINT but requires the same chain-of-custody discipline so it survives evidentiary challenge. The `osint-investigation` skill writes here per its v1.1 frontmatter (round-4 R4-5).

## What goes here

- Written witness statements (markdown + signed PDF if available)
- Transcripts of recorded interviews
- Declarations / affidavits
- Contemporaneous notes from conversations with witnesses

## Naming

`<witness-slug>_<YYYY-MM-DD>.md` — e.g. `jane_doe_2026-04-08.md`

## Required metadata

Every file MUST have this frontmatter:

```yaml
---
witness_name: <full name>
witness_role: <relationship to the case>
date_taken: YYYY-MM-DD
location: <where the statement was given>
collected_by: <who interviewed>
language: <language of the statement>
sha256: <hash of the verbatim text section below>
admiralty_grade: <grade of the witness as a source>
attached_files:
  - <recording, signed PDF, etc.>
---

# Statement (verbatim)

<the witness's exact words; no paraphrasing>
```

## Chain of custody

1. Save the statement file
2. Hash it: `shasum -a 256 <file>` → log in `04_evidence/CHAIN_OF_CUSTODY.log`
3. RFC3161 timestamp the hash (see `osint-investigation` skill)
4. Append a proposal to `06_claims_and_defenses/PENDING_FACTS.md` (category T — Testimony)
5. A human reviewer promotes the proposed PF to `PROVEN_FACTS_REGISTER.md` in a separate commit
EOF
```

- [ ] **Step 7: Write `05_legal_research/README.md`**

```bash
cat > templates/case_skeleton/05_legal_research/README.md <<'EOF'
# 05_legal_research

> Case-specific legal research. The law pack goes under `law_pack/` — copied from the plugin by `/lex-harness:init`.

## Structure

```
05_legal_research/
├── law_pack/                   # copied from ${CLAUDE_PLUGIN_ROOT}/law-packs/<jurisdiction>/ by /lex-harness:init
│   ├── pack.json
│   ├── MODULE_INDEX.md
│   ├── forums.yaml
│   ├── limitation_periods.yaml
│   ├── playbook.yaml
│   ├── glossary.md
│   ├── core/                   # always-loaded statute files
│   ├── modules/                # task-specific modules
│   ├── case_law/
│   ├── templates/              # localised draft templates
│   └── osint_databases.md      # country-specific databases for the osint-investigation skill
├── case_notes/                 # case-specific research notes that don't belong in the pack
└── README.md
```

## What goes in `law_pack/`

NOTHING you edit by hand. This is a CHECKED-IN SNAPSHOT of the plugin's `law-packs/<jurisdiction>/` directory. Update it with:

```
/lex-harness:init <jurisdiction> --update-pack
```

If you find a bug in the pack or a missing statute, fix it UPSTREAM in the plugin repo and run `--update-pack`. Never hand-edit files under `law_pack/`.

## What goes in `case_notes/`

Case-specific research that is NOT generally applicable. Examples:

- A specific court's local rules you discovered
- A judge's tendencies (public record only)
- A regulatory body's unwritten procedures
- Research on a specific opposing party's history

If the research is generally applicable to the jurisdiction (e.g., "this court has a 6-week average wait time"), PR it upstream to the law pack instead.
EOF
```

- [ ] **Step 8: Write `06_claims_and_defenses/README.md`**

```bash
cat > templates/case_skeleton/06_claims_and_defenses/README.md <<'EOF'
# 06_claims_and_defenses

> Per-charge defense files, per-counterclaim offense files, cross-cutting issues, and the proven facts register.

## Structure

```
06_claims_and_defenses/
├── PROVEN_FACTS_REGISTER.md    # authoritative fact register (T1 — AI cannot write directly)
├── PENDING_FACTS.md            # AI propose queue (AI writes here; human promotes)
├── BURDEN_OF_PROOF_MATRIX.md   # per-argument burden analysis
├── CROSS_CUTTING_ISSUES.md     # issues that affect multiple arguments
├── COUNTERCLAIMS.md            # hub summarising all counterclaims
├── CH1_<slug>.md               # charge/defense file 1
├── CH2_<slug>.md               # charge/defense file 2
├── ...
├── CC1_<slug>.md               # counterclaim file 1
├── CC2_<slug>.md               # counterclaim file 2
└── ...
```

## Naming convention

- `CH<N>_<slug>.md` — a charge or defense against a charge from the opposing party
- `CC<N>_<slug>.md` — a counterclaim the user is asserting
- `SA<N>_<slug>.md` — a strategic argument (usually lives in `07_strategy/`, but cross-referenced here)

## PROVEN_FACTS_REGISTER.md

The T1 file. AI-generated commits to this file are BLOCKED by the git pre-commit hook. The AI proposes new facts via `PENDING_FACTS.md`; a human promotes them in a separate commit WITHOUT the `Co-Authored-By: Claude` trailer.

See `PENDING_FACTS.md` for the propose-queue workflow and `/lex-harness:fact` for the interactive command.

## CH / CC file structure

Every CH and CC file has this standard layout:

```markdown
---
id: CH1
type: defense
status: active | dropped | downgraded
forum: <forum>
amount: <amount>
---

# CH1 — <title>

## Quick reference

<one paragraph — the argument in plain language>

## Argument index

1. <short title of argument 1>
2. <short title of argument 2>

## Proven facts

- PF-A01 — <brief>
- PF-A02 — <brief>

## Legal basis

- <article-id> — <one-line>

## Devil's advocate status

- <verdict from most recent DA review>
- <link to DA review file>

## Open questions

- <Q1>
- <Q2>
```
EOF
```

- [ ] **Step 9: Write `07_strategy/README.md`**

```bash
cat > templates/case_skeleton/07_strategy/README.md <<'EOF'
# 07_strategy

> Strategic arguments, case theory, decision log, devil's advocate reviews.

## Structure

```
07_strategy/
├── core/
│   ├── CASE_THEORY.md              # theme, legal theory, factual theory, risk assessment
│   ├── LEGAL_PLAYBOOK.md           # list of plays available for this case
│   ├── DECISION_LOG.md             # dropped/downgraded/corrected arguments
│   ├── SETTLEMENT_ECONOMICS.md     # ZOPA, BATNA, expected value
│   └── DEVILS_ADVOCATE_INDEX.md    # registry of all DA review files
├── da_reviews/                     # per-argument DA review files (DA_<id>_<date>.md)
├── extraction/                     # pressure extraction briefs, fact extraction plans
├── forensic/                       # forensic accounting, structured fact patterns
├── escalation/                     # escalation path planning (forums, timing)
├── SA1_<slug>.md                   # strategic argument 1
├── SA2_<slug>.md                   # strategic argument 2
└── ...
```

## Relationship to 06_claims_and_defenses

- `06_claims_and_defenses/` contains PER-CHARGE defense files (CH) and PER-COUNTERCLAIM offense files (CC). Each is a standalone argument file.
- `07_strategy/` contains CROSS-ARGUMENT strategic reasoning. An SA file may tie together elements from multiple CH/CC files (e.g., a "pattern of bad faith" argument that relies on elements from CH1, CH2, CC3, and CC5).

## DECISION_LOG.md — the most important file in this directory

Every dropped, downgraded, or corrected argument gets an entry here. Format:

```markdown
## DL-<N> — <title>

- **Date:** YYYY-MM-DD
- **Action:** DROPPED | DOWNGRADED | CORRECTED | DA-REVIEW
- **Argument:** <argument-id or brief>
- **Reason:** <one paragraph>
- **Supersedes:** <any prior DL entries>
```

**Dropped arguments stay dropped.** The legal-strategy skill is required to check DECISION_LOG before proposing any argument. Proposing a previously dropped argument is a P0 bug.

## da_reviews/ — devil's advocate reviews

One file per DA run. Naming: `DA_<argument-id>_<YYYY-MM-DD>.md`. The format is enforced by the `devil-advocate` skill — see `skills/devil-advocate/SKILL.md` in the plugin.

Never hand-edit a DA review. They are subagent outputs and their audit value depends on being untouched.
EOF
```

- [ ] **Step 10: Write `08_drafts/README.md`**

```bash
cat > templates/case_skeleton/08_drafts/README.md <<'EOF'
# 08_drafts

> Formal documents ready (or being prepared) to send. OWNED by the `document-production` skill.

## What goes here

- Demand letters
- Civil complaints
- Regulatory filings
- Data protection authority complaints
- Consumer ombudsman complaints
- Criminal referrals
- Formal email responses to the opposing party
- Settlement proposals

## Naming

`<doc-type>_<argument-id>_<YYYY-MM-DD>.md`

Examples:
- `demand_letter_CH1_2026-04-08.md`
- `civil_complaint_SA31_2026-05-15.md`
- `settlement_proposal_2026-06-01.md`

## Ownership

The `document-production` skill OWNS writes to this directory. Other skills do not write here — they hand off.

## Mandatory footer block

Every file in `08_drafts/` MUST end with the 4-field footer block per `skills/document-production/references/footer-block-schema.md`:

```yaml
footer_block:
  pf_ids: [...]
  law_articles: [...]
  evidence_items: [...]
  da_review_refs: [...]
verify_gate:
  passed: true
  date: <YYYY-MM-DD>
  failures: []
```

A draft without the footer block is REJECTED by the verify-gate Stage 9.

## Review before release

A draft in this directory is NOT automatically released. The user reviews the draft (ideally with a retained lawyer) and releases it manually to the recipient. The skills never auto-send.
EOF
```

- [ ] **Step 11: Write `09_ai_research/README.md`**

```bash
cat > templates/case_skeleton/09_ai_research/README.md <<'EOF'
# 09_ai_research

> AI research library — case-specific notes on AI tooling, legal research queries, and model outputs that informed the case.

## What goes here

- `research_queue.md` — open questions the legal-strategy skill has queued for further research
- `INDEX.md` — index of AI research files
- `<topic>.md` — per-topic notes

## What does NOT go here

- Legal research results (→ `05_legal_research/case_notes/`)
- Evidence discovered via OSINT (→ `04_evidence/osint/`)
- Strategic arguments (→ `07_strategy/`)
- Draft documents (→ `08_drafts/`)

## research_queue.md format

```markdown
## Q-<N> — <question>

- **Raised:** YYYY-MM-DD
- **Raised by:** <skill or user>
- **Trigger:** <what made this question arise>
- **Status:** open | in-progress | answered | dropped
- **Answer:** <when resolved>
```

The `legal-strategy` skill writes to this file when it identifies a gap that needs further research.
EOF
```

- [ ] **Step 12: Verify all 10 README files**

```bash
ls templates/case_skeleton/*/README.md templates/case_skeleton/04_evidence/testimony/README.md
wc -l templates/case_skeleton/*/README.md templates/case_skeleton/04_evidence/testimony/README.md
```

Expected: 10 README files exist.

- [ ] **Step 13: Verify no jurisdiction-specific content**

```bash
python3 - <<'PY'
import os, sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'ΓΕΜΗ', 'ΑΑΔΕ', 'Yestay',
          'VIAMAR', 'kodiko.gr', 'lawspot.gr', 'Άρειος Πάγος',
          'Eirinodikio', 'Pilitsoglou']
root = 'templates/case_skeleton'
hits = []
for dirpath, _, files in os.walk(root):
    for f in files:
        if f.endswith('.md'):
            p = os.path.join(dirpath, f)
            with open(p) as fh:
                content = fh.read()
            for w in banned:
                if w in content:
                    hits.append(f"{p}: {w}")
if hits:
    sys.exit("PR-01 violation:\n" + "\n".join(hits))
print("OK — case skeleton is jurisdiction-agnostic")
PY
```

Expected: `OK — case skeleton is jurisdiction-agnostic`.

- [ ] **Step 14: Commit**

```bash
git add templates/case_skeleton/
git commit -s -m "$(cat <<'EOF'
feat(templates): case_skeleton — 10 directories with READMEs (T22)

Empty case skeleton that /lex-harness:init copies into a new case
repo. All 10 directories (01_case_summary through 09_ai_research,
plus 04_evidence/testimony) have READMEs explaining:

- What files belong in that directory
- Naming conventions
- Chain-of-custody requirements (where applicable)
- Ownership (which skill writes there)
- What does NOT belong in that directory

All READMEs are JURISDICTION-AGNOSTIC per PR-01 / PR-03. No Greek
terms, no country-specific law references, no yestay case content.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 23: `templates/PROVEN_FACTS_REGISTER.md` + `templates/PENDING_FACTS.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/templates/PROVEN_FACTS_REGISTER.md`
- Create: `~/Developer/projects/lex-harness/templates/PENDING_FACTS.md`

Both files are SCHEMA HEADERS with no entries. They document all 11 categories (A–H, P, T, N) and the entry format. When `/lex-harness:init` copies them into a new case repo, they are empty-but-valid — the first fact gets proposed via `/lex-harness:fact`.

- [ ] **Step 1: Write `templates/PROVEN_FACTS_REGISTER.md`**

```bash
cat > templates/PROVEN_FACTS_REGISTER.md <<'EOF'
# Proven Facts Register

> Authoritative fact register for this case. T1 — the most protected file in the repo.

**⚠ IMPORTANT:** This file is protected by the git pre-commit hook. AI-generated commits (those with `Co-Authored-By: Claude` in the trailer) are REJECTED at the hook. The AI proposes new facts via `PENDING_FACTS.md`. A human reviews each proposal and promotes it to this file in a SEPARATE commit WITHOUT the AI trailer.

## Schema

Every entry has this structure:

```yaml
---
- id: PF-<category><number>
  category: <letter>
  text: |
    <verbatim fact text, ≤300 chars preferred>
  source: <file path, URL, or human-readable reference>
  grade: <Admiralty Code grade, e.g. A1, B2>
  corroboration:
    - <additional source 1>
    - <additional source 2>
  effective_date: <when the fact became true, YYYY-MM-DD>
  registered_date: <when added to this register, YYYY-MM-DD>
  registered_by: <human reviewer name>
  superseded_by: null
---
```

## Categories

| Category | Meaning | Typical source |
|---|---|---|
| **A** | **Admitted / uncontroverted facts** — facts the opposing party has admitted or has not contested | Email admissions, signed documents, public records |
| **B** | **Behaviour / conduct** — things the opposing party did (or failed to do) | Correspondence, witness accounts, timeline reconstruction |
| **C** | **Correspondence** — specific statements made in communication | Email, WhatsApp, phone-call notes, letters |
| **D** | **Documents** — facts proven by the existence or content of a specific document | Contracts, invoices, receipts, statutes as applied |
| **E** | **Evidence** — physical or documentary items in `04_evidence/` | Photos, files, screenshots with chain of custody |
| **F** | **Forensic** — facts derived from accounting analysis, document metadata, or technical inspection | Invoice anomalies, EXIF, PDF XMP, DKIM |
| **G** | **GDPR / data protection admissions** — admissions in data-subject access responses or privacy notices | SAR responses, privacy policies |
| **H** | **Hearsay-ish** — secondhand accounts useful only with corroboration | Third-party statements, reputation evidence |
| **P** | **Proven (primary evidence)** — strongest grade; tamper-evident items with chain of custody | Photos with EXIF + SHA-256 + RFC3161 timestamp |
| **T** | **Testimony** — first-party witness statements captured in `04_evidence/testimony/` | Signed declarations, transcripts |
| **N** | **Negative facts** — absence is evidence (e.g., "no inventory list was ever signed") | Verified absence confirmed by multiple sources |

## Grading (Admiralty Code)

Every PF entry has a `grade` field combining reliability (A–F) and credibility (1–6):

- **A1–A2, B1–B2** — PROVEN status (can be cited in formal documents)
- **B3, C1–C3** — AVAILABLE status (use with corroboration)
- **Below C3** — do not cite

See `skills/osint-investigation/references/chain-of-custody.md` §5 for the full matrix.

## Promotion workflow

1. AI proposes a fact via `/lex-harness:fact` → appends to `PENDING_FACTS.md`
2. Human reviewer reads the proposal + verifies the source
3. Human reviewer decides: ACCEPT / REJECT / NEEDS-WORK
4. If ACCEPT:
   - Move the entry from `PENDING_FACTS.md` to this file
   - Add the `registered_date` and `registered_by` fields
   - Commit the move in a SEPARATE commit WITHOUT a `Co-Authored-By: Claude` trailer
5. If REJECT: delete the entry from `PENDING_FACTS.md`
6. If NEEDS-WORK: update the entry in `PENDING_FACTS.md` with feedback; re-run review

## Supersession

Facts are never deleted once in the register. If a fact is found to be wrong, add a new entry that supersedes it:

```yaml
- id: PF-A01
  ...
  superseded_by: PF-A47
---
- id: PF-A47
  text: |
    <corrected fact>
  ...
  supersedes: PF-A01
```

The old entry stays in the register for audit.

## Entries

<!-- empty on init — first entry goes below this line after a human promotion -->
EOF
```

- [ ] **Step 2: Write `templates/PENDING_FACTS.md`**

```bash
cat > templates/PENDING_FACTS.md <<'EOF'
# Pending Facts Queue

> AI propose queue. The `/lex-harness:fact` command and the skills append proposals here. A human reviews each proposal and promotes it to `PROVEN_FACTS_REGISTER.md` in a separate commit WITHOUT the `Co-Authored-By: Claude` trailer.

## Why a separate file

The git pre-commit hook blocks AI commits to `PROVEN_FACTS_REGISTER.md` (T1 write-path isolation). This file is the AI's safe write target. The hook DOES NOT block AI commits here — proposals are allowed. Promotion is human-only.

## Schema (same as PROVEN_FACTS_REGISTER)

```yaml
---
- id: PF-<category><number>
  category: <letter>
  text: |
    <verbatim fact text>
  source: <file path, URL, or human-readable reference>
  status: pending | accepted | rejected | needs-work
  proposed_by: AI (via /lex-harness:fact) | <skill-name>
  proposed_date: YYYY-MM-DD
  reviewer: null
  reviewed_date: null
  review_notes: null
  promoted_to_register: false
---
```

## Categories

See `PROVEN_FACTS_REGISTER.md` for the full category table (A–H, P, T, N).

## Review workflow

### For the human reviewer

1. Open this file
2. Read each `status: pending` entry
3. For each entry:
   a. Read the `source` field and verify the fact against the source
   b. Decide: ACCEPT / REJECT / NEEDS-WORK
   c. If ACCEPT:
      - Copy the entry to `PROVEN_FACTS_REGISTER.md`
      - Add `registered_date` and `registered_by` fields
      - Update this entry's `status` to `accepted` and `promoted_to_register: true`
      - **Commit WITHOUT the `Co-Authored-By: Claude` trailer** — the hook will reject the commit otherwise
   d. If REJECT:
      - Update the entry's `status` to `rejected`
      - Add `review_notes` explaining why
      - Commit (may or may not have AI trailer — rejection is harmless)
   e. If NEEDS-WORK:
      - Update the entry's `status` to `needs-work`
      - Add `review_notes` describing what needs to change
      - The AI re-proposes in a new entry later

### For the AI

- NEVER edit an existing entry in this file
- ALWAYS append new proposals at the end
- NEVER add entries with `status` other than `pending`
- NEVER add entries with `promoted_to_register: true`
- NEVER set `reviewer` or `reviewed_date`

## Entries

<!-- empty on init — first proposal goes below this line -->
EOF
```

- [ ] **Step 3: Verify both files**

```bash
ls templates/PROVEN_FACTS_REGISTER.md templates/PENDING_FACTS.md
wc -l templates/PROVEN_FACTS_REGISTER.md templates/PENDING_FACTS.md
```

Expected: 2 files exist.

- [ ] **Step 4: Verify no jurisdiction-specific content**

```bash
python3 - <<'PY'
import sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'Yestay', 'VIAMAR', 'PF-A29', 'PF-G07']
for p in ['templates/PROVEN_FACTS_REGISTER.md', 'templates/PENDING_FACTS.md']:
    with open(p) as f:
        content = f.read()
    hits = [w for w in banned if w in content]
    if hits:
        sys.exit(f"{p}: PR-01 violation: {hits}")
print("OK")
PY
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add templates/PROVEN_FACTS_REGISTER.md templates/PENDING_FACTS.md
git commit -s -m "$(cat <<'EOF'
feat(templates): PROVEN_FACTS_REGISTER.md + PENDING_FACTS.md (T23)

Schema headers for the two-file fact workflow. Both empty on init —
first entry goes after a human promotion or AI proposal.

- PROVEN_FACTS_REGISTER.md: T1 authoritative register protected by
  git hook; documents the full schema, all 11 categories (A-H, P,
  T, N), Admiralty Code grading, promotion workflow, and supersession
- PENDING_FACTS.md: AI propose queue; same schema + separate workflow
  for humans to ACCEPT/REJECT/NEEDS-WORK each proposal
- Both files are JURISDICTION-AGNOSTIC; no sample entries reference
  any specific case

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 24: `templates/DEADLINE_REGISTER.md` + `templates/CURRENT_STATUS.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/templates/DEADLINE_REGISTER.md`
- Create: `~/Developer/projects/lex-harness/templates/CURRENT_STATUS.md`

Both files are populated by `/lex-harness:init` Steps 8-9. The templates are empty-but-valid — they document the schema and include a single placeholder entry that the init command replaces.

- [ ] **Step 1: Write `templates/DEADLINE_REGISTER.md`**

```bash
cat > templates/DEADLINE_REGISTER.md <<'EOF'
# Deadline Register

> Every date-bound obligation in this case. Updated every session by the `legal-strategy` skill. DL-01 is the statutory limitation period — populated by `/lex-harness:init` from the active law pack's `limitation_periods.yaml`.

## Schema

Every deadline has this structure:

```yaml
---
- id: DL-<N>
  title: <short title>
  source_article: <article-id from the active law pack>
  period_days: <integer>
  accrual_event: <description of when the clock started>
  accrual_event_date: YYYY-MM-DD
  deadline: YYYY-MM-DD
  days_remaining: <integer, re-computed every session>
  interruption_methods:
    - <method 1>
    - <method 2>
  status: open | interrupted | satisfied | expired
  notes: <optional>
---
```

## Priority tiers

The `legal-strategy` skill reads this file at every session start and warns if:

- Any deadline has `days_remaining ≤ 60` (warn loudly)
- Any deadline has `days_remaining ≤ 14` (URGENT — block other work)
- Any deadline has `days_remaining ≤ 0` (MISSED — escalate immediately)

## Interruption

Some jurisdictions allow deadline interruption by specific actions (formal demand, court filing, settlement discussion). The active law pack's `limitation_periods.yaml` lists the interruption methods for each period. When an interruption occurs:

1. Do NOT delete the original entry
2. Add a new entry: `DL-<N>-i1` with the post-interruption clock
3. Update the original entry's `status` to `interrupted`
4. Link the two with `notes: interrupted by DL-<N>-i1`

## Entries

## DL-01 — <<LIMITATION_TITLE>>

- **Source article:** `<<LIMITATION_ARTICLE_ID>>`
- **Period:** `<<LIMITATION_PERIOD_DAYS>>` days from `<<LIMITATION_ACCRUAL_EVENT>>`
- **Accrual event date:** `<<ACCRUAL_EVENT_DATE>>`
- **Deadline:** `<<LIMITATION_DEADLINE>>`
- **Days remaining:** `<<DAYS_REMAINING>>` (re-compute every session)
- **Interruption methods:** `<<INTERRUPTION_METHODS>>`
- **Status:** open

<!-- additional deadlines (DL-02, DL-03, ...) get appended below as they arise -->
EOF
```

- [ ] **Step 2: Write `templates/CURRENT_STATUS.md`**

```bash
cat > templates/CURRENT_STATUS.md <<'EOF'
# Current Status

> Session-start orientation file. ≤30 lines. Updated by the `legal-strategy` skill at every session end. First thing the skill reads when a new session begins.

## Phase

`<<PHASE>>`

## Last action

- **Date:** `<<LAST_ACTION_DATE>>`
- **Action:** `<<LAST_ACTION>>`
- **By:** `<<LAST_ACTION_BY>>`

## Next action (ONE only)

`<<NEXT_ACTION>>`

## Critical deadlines

- `<<DL_01_SUMMARY>>`

## Open questions (top 3)

1. `<<OPEN_Q1>>`
2. `<<OPEN_Q2>>`
3. `<<OPEN_Q3>>`

## Recent decisions (top 3)

1. `<<RECENT_DL1>>`
2. `<<RECENT_DL2>>`
3. `<<RECENT_DL3>>`

## Session history (append-only)

<!-- newest entries at top; one line per session -->
- `<<DATE>>` — <<SESSION_SUMMARY>>
EOF
```

- [ ] **Step 3: Verify both files**

```bash
ls templates/DEADLINE_REGISTER.md templates/CURRENT_STATUS.md
wc -l templates/DEADLINE_REGISTER.md templates/CURRENT_STATUS.md
```

Expected: 2 files exist.

- [ ] **Step 4: Verify no jurisdiction-specific content**

```bash
python3 - <<'PY'
import sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'Yestay', 'VIAMAR',
          'Art. 602', 'Pilitsoglou']
for p in ['templates/DEADLINE_REGISTER.md', 'templates/CURRENT_STATUS.md']:
    with open(p) as f:
        content = f.read()
    hits = [w for w in banned if w in content]
    if hits:
        sys.exit(f"{p}: PR-01 violation: {hits}")
print("OK")
PY
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add templates/DEADLINE_REGISTER.md templates/CURRENT_STATUS.md
git commit -s -m "$(cat <<'EOF'
feat(templates): DEADLINE_REGISTER + CURRENT_STATUS templates (T24)

Both files are empty-but-valid schema headers populated by
/lex-harness:init from the active law pack's limitation_periods.yaml
and the user's case metadata.

- DEADLINE_REGISTER.md: schema + priority tiers (60d / 14d / 0d
  warnings) + interruption workflow + DL-01 placeholder with
  <<LIMITATION_*>> slots filled by init
- CURRENT_STATUS.md: session-start orientation file (≤30 lines) with
  phase, last action, next action, critical deadlines, open
  questions, recent decisions, and append-only session history

Both JURISDICTION-AGNOSTIC per PR-01 / PR-03.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 25: `templates/CLAUDE.md` (case-agnostic project instructions)

**Files:**
- Create: `~/Developer/projects/lex-harness/templates/CLAUDE.md`

This file is copied into a new case repo by `/lex-harness:init`. It is the Claude Code project instructions file — the first thing Claude Code reads when a session starts in that repo. It references the plugin's skills and the active law pack by relative path.

It MUST be JURISDICTION-AGNOSTIC — no mention of Greek law, no yestay-specific content. The init command fills in a few `<<placeholders>>` (jurisdiction name, pack version) when copying.

- [ ] **Step 1: Write `templates/CLAUDE.md`**

```bash
cat > templates/CLAUDE.md <<'EOF'
# CLAUDE.md

This file provides guidance to Claude Code when working with this legal case repository.

## Project type

**Legal case management repository.** NOT a code project. Files are markdown + YAML. No build system, no test runner, no dependency manager (other than the `lex-harness` plugin).

## Case metadata

| Field | Value |
|---|---|
| Claimant | `<<CLAIMANT>>` |
| Opposing party | `<<OPPOSING_PARTY>>` |
| Dispute subject | `<<DISPUTE_SUBJECT>>` |
| Amount at stake | `<<AMOUNT>>` |
| Jurisdiction | `<<JURISDICTION>>` |
| Law pack version | `<<PACK_VERSION>>` |
| Initialised | `<<INIT_DATE>>` via `/lex-harness:init` |

See `01_case_summary/CASE_OVERVIEW.md` for the full overview.

## Plugin

This repo consumes the `lex-harness` plugin. The plugin provides:

- 4 skills: `legal-strategy`, `osint-investigation`, `document-production`, `devil-advocate`
- 3 slash commands: `/lex-harness:init`, `/lex-harness:fact`, `/lex-harness:devil`
- The active law pack at `05_legal_research/law_pack/` (copied from `${CLAUDE_PLUGIN_ROOT}/law-packs/<<JURISDICTION>>/`)

Update the law pack with: `/lex-harness:init <<JURISDICTION>> --update-pack`

## Repository structure

```
01_case_summary/           # CASE_OVERVIEW.md (single source of truth), CHARGES_OVERVIEW.md, TIMELINE.md
02_contracts/              # All signed contracts, extensions, amendments
03_correspondence/         # Emails, WhatsApp, phone calls, meetings
04_evidence/               # Photos, invoices, OSINT, testimony; EVIDENCE_INDEX.md + CHAIN_OF_CUSTODY.log
05_legal_research/         # law_pack/ (from plugin) + case_notes/
06_claims_and_defenses/    # CH/CC files + PROVEN_FACTS_REGISTER + PENDING_FACTS + BURDEN_OF_PROOF_MATRIX
07_strategy/               # SA files + core/ (CASE_THEORY, LEGAL_PLAYBOOK, DECISION_LOG, SETTLEMENT_ECONOMICS) + da_reviews/
08_drafts/                 # Formal documents ready or being prepared (OWNED by document-production)
09_ai_research/            # AI research library, research_queue.md
CURRENT_STATUS.md          # Session-start orientation (≤30 lines)
DEADLINE_REGISTER.md       # DL-01 (limitation) + other date-bound obligations
CLAUDE.md                  # This file
```

## Key documents

| Document | Purpose |
|---|---|
| `01_case_summary/CASE_OVERVIEW.md` | Single source of truth — parties, amounts, dates, jurisdiction |
| `CURRENT_STATUS.md` | Session-start orientation — phase, last action, next action, deadlines |
| `DEADLINE_REGISTER.md` | All date-bound obligations; DL-01 = statutory limitation period |
| `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` | Authoritative fact register (T1 — protected by git hook) |
| `06_claims_and_defenses/PENDING_FACTS.md` | AI propose queue (AI writes here; human promotes) |
| `07_strategy/core/CASE_THEORY.md` | Theme, legal theory, factual theory, risk assessment |
| `07_strategy/core/DECISION_LOG.md` | Dropped/downgraded/corrected arguments; check before proposing anything |
| `05_legal_research/law_pack/` | Active jurisdiction's law pack — do not hand-edit; update via plugin |

## T1 write-path isolation (critical rule)

`PROVEN_FACTS_REGISTER.md` is the most protected file in this repo. The git pre-commit hook in `.githooks/pre-commit` REJECTS any commit that touches this file AND contains a `Co-Authored-By: Claude` trailer.

Why: an AI that can fabricate facts and commit them to the authoritative register is a P0 risk. The hook is the architectural enforcement of the "AI proposes, human promotes" workflow.

**How to add a fact:**

1. AI runs `/lex-harness:fact` → appends proposal to `PENDING_FACTS.md`
2. Human reviews the proposal + verifies the source
3. Human copies the entry from `PENDING_FACTS.md` to `PROVEN_FACTS_REGISTER.md` in a **separate commit WITHOUT** the `Co-Authored-By: Claude` trailer
4. The hook allows the human commit because it lacks the AI trailer

**What happens if the AI tries to commit to PROVEN_FACTS_REGISTER:**

```
[T1-WRITE-VIOLATION]
AI-trailered commit detected touching PROVEN_FACTS_REGISTER.md.
Rejecting. AI must propose new facts via PENDING_FACTS.md for human review.
```

## Skills reference

| Skill | When to invoke |
|---|---|
| `legal-strategy` | Any strategic decision, drafting plan, play selection, settlement reasoning, forum choice |
| `osint-investigation` | Evidence preservation, public-records research, witness statement capture, chain of custody |
| `document-production` | Any formal document leaving the workspace — demand letters, complaints, filings, settlement proposals |
| `devil-advocate` | Adversarial review of a strategic argument (dispatched via `/lex-harness:devil <id>`) |

All four skills are jurisdiction-agnostic. They load the active law pack at runtime from `05_legal_research/law_pack/`.

## Language

Documents in this repo may be in the user's native language OR the jurisdiction's legal language (typically the same, but not always). Preserve legal terminology exactly — never paraphrase statute text, never translate legal terms without flagging the translation.

## Archive safety rule

If this repo has an `archive/` directory, NEVER read files under `archive/` as source of truth. Archived files contain superseded or known-wrong values. Always use the current files in the numbered directories.

## Commit conventions

- The AI commits with `Co-Authored-By: Claude` in the trailer
- Human commits that promote facts to PROVEN_FACTS_REGISTER MUST NOT have the AI trailer
- Every commit MUST have a Developer Certificate of Origin sign-off (`git commit -s`) per the `lex-harness` CONTRIBUTING.md

## Useful commands

```bash
# Add a fact (AI proposes)
/lex-harness:fact

# Update the law pack
/lex-harness:init <<JURISDICTION>> --update-pack

# Run devil's advocate on an argument
/lex-harness:devil <argument-id>

# Check git hook is installed
git config --get core.hooksPath     # should print: .githooks

# Verify PROVEN_FACTS_REGISTER hook works
echo "test" >> 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
git add 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
git commit -s -m "test commit

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
# Expected: hook rejects with [T1-WRITE-VIOLATION]

# Reset the test
git reset --hard HEAD
```
EOF
```

- [ ] **Step 2: Verify the file**

```bash
ls templates/CLAUDE.md
wc -l templates/CLAUDE.md
```

Expected: file exists; ~130 lines.

- [ ] **Step 3: Verify no jurisdiction-specific content**

```bash
python3 - <<'PY'
import sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'Yestay', 'VIAMAR',
          'Art. 612A', 'Pilitsoglou', 'Elliniko', 'Ypsilantou']
with open('templates/CLAUDE.md') as f:
    content = f.read()
hits = [w for w in banned if w in content]
if hits:
    sys.exit(f"PR-01 violation: {hits}")
print("OK")
PY
```

Expected: `OK`.

- [ ] **Step 4: Commit**

```bash
git add templates/CLAUDE.md
git commit -s -m "$(cat <<'EOF'
feat(templates): CLAUDE.md — case-agnostic project instructions (T25)

The file /lex-harness:init copies into a new case repo. Claude Code
reads this first when a session starts.

- Case metadata table with <<placeholder>> slots filled by init
- Repository structure overview (10 numbered directories)
- Key documents table
- T1 write-path isolation rule explained + how to add a fact
- Skills reference table (legal-strategy, osint-investigation,
  document-production, devil-advocate)
- Archive safety rule
- Commit conventions (AI trailer + DCO)
- Useful commands including the hook verification test

NO mention of Greek law, yestay, or any specific case. References
the active law pack via <<JURISDICTION>> placeholder.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 26: `templates/pre-commit` git hook + `scripts/install-githooks.sh`

**Files:**
- Create: `~/Developer/projects/lex-harness/templates/pre-commit`
- Create: `~/Developer/projects/lex-harness/scripts/install-githooks.sh`

The pre-commit hook implements T1 write-path isolation. It rejects any commit that:

1. Touches `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md`, AND
2. Contains `Co-Authored-By: Claude` in the commit message

This is the architectural enforcement of "AI proposes, human promotes." The AI proposes facts via `PENDING_FACTS.md` (which is NOT protected). Human commits (without the AI trailer) promote them.

The install script sets `core.hooksPath` to `.githooks/` and makes the hook executable. It's also invoked by `/lex-harness:init` Step 5.

Per the yestay MVP plan T10, the hook must have three documented test cases:

- **RED test:** AI-trailered commit touching PROVEN_FACTS_REGISTER → REJECTED
- **GREEN test 1:** Human commit (no AI trailer) touching PROVEN_FACTS_REGISTER → ALLOWED
- **GREEN test 2:** AI-trailered commit touching other files (not PROVEN_FACTS_REGISTER) → ALLOWED

- [ ] **Step 1: Create the scripts directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p scripts templates
```

- [ ] **Step 2: Write `templates/pre-commit`**

```bash
cat > templates/pre-commit <<'EOF'
#!/usr/bin/env bash
#
# lex-harness T1 write-path isolation hook
# -----------------------------------------
# Rejects commits that touch PROVEN_FACTS_REGISTER.md if the commit
# message contains `Co-Authored-By: Claude` in the trailer.
#
# The AI proposes new facts via PENDING_FACTS.md (which is NOT
# protected). A human reviews each proposal and promotes it to
# PROVEN_FACTS_REGISTER.md in a separate commit WITHOUT the AI trailer.
#
# Installed by: /lex-harness:init OR scripts/install-githooks.sh
# Hook path:    <case-repo>/.githooks/pre-commit
# Enabled via:  git config core.hooksPath .githooks

set -euo pipefail

PROTECTED_FILES=(
    "06_claims_and_defenses/PROVEN_FACTS_REGISTER.md"
)

# Check if any staged file is in the protected list
STAGED=$(git diff --cached --name-only --diff-filter=ACMR)

TOUCHED_PROTECTED=""
for file in "${PROTECTED_FILES[@]}"; do
    if echo "$STAGED" | grep -Fxq "$file"; then
        TOUCHED_PROTECTED="$file"
        break
    fi
done

if [ -z "$TOUCHED_PROTECTED" ]; then
    # No protected file touched — allow the commit
    exit 0
fi

# A protected file is touched. Check the commit message for the AI trailer.
# The commit message is in $1 (passed by git) OR in the
# .git/COMMIT_EDITMSG file (if $1 is not set, fall back).
COMMIT_MSG_FILE="${1:-.git/COMMIT_EDITMSG}"

if [ ! -f "$COMMIT_MSG_FILE" ]; then
    # No commit message file — allow (interactive use)
    exit 0
fi

# Look for the Co-Authored-By: Claude trailer
if grep -qi "^Co-Authored-By: Claude" "$COMMIT_MSG_FILE"; then
    cat <<ERR >&2

[T1-WRITE-VIOLATION]
AI-trailered commit detected touching protected file:
  $TOUCHED_PROTECTED

The AI cannot write to the authoritative fact register.
Propose new facts via PENDING_FACTS.md using /lex-harness:fact
A human reviewer promotes them in a separate commit WITHOUT the
Co-Authored-By: Claude trailer.

Rejecting commit.

ERR
    exit 1
fi

# Human commit (no AI trailer) touching PROVEN_FACTS_REGISTER — allow
exit 0
EOF
chmod +x templates/pre-commit
```

- [ ] **Step 3: Write `scripts/install-githooks.sh`**

```bash
cat > scripts/install-githooks.sh <<'EOF'
#!/usr/bin/env bash
#
# install-githooks.sh — install the lex-harness T1 pre-commit hook
# into a case repo.
#
# Usage:
#   scripts/install-githooks.sh                    # installs into CWD
#   scripts/install-githooks.sh <case-repo-path>   # installs into a specific repo
#
# Called by: /lex-harness:init Step 5
#            or manually after cloning a case repo

set -euo pipefail

TARGET="${1:-$(pwd)}"

if [ ! -d "$TARGET" ]; then
    echo "Error: target directory does not exist: $TARGET" >&2
    exit 1
fi

cd "$TARGET"

# Confirm this is a git repo or init one
if [ ! -d ".git" ]; then
    echo "Initialising git repo in $TARGET..."
    git init -b main
fi

# Locate the hook template (relative to this script OR the plugin root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK_SRC=""

if [ -f "$SCRIPT_DIR/../templates/pre-commit" ]; then
    HOOK_SRC="$SCRIPT_DIR/../templates/pre-commit"
elif [ -n "${CLAUDE_PLUGIN_ROOT:-}" ] && [ -f "$CLAUDE_PLUGIN_ROOT/templates/pre-commit" ]; then
    HOOK_SRC="$CLAUDE_PLUGIN_ROOT/templates/pre-commit"
else
    echo "Error: cannot locate templates/pre-commit" >&2
    echo "Tried:" >&2
    echo "  $SCRIPT_DIR/../templates/pre-commit" >&2
    echo "  \$CLAUDE_PLUGIN_ROOT/templates/pre-commit" >&2
    exit 1
fi

mkdir -p .githooks
cp "$HOOK_SRC" .githooks/pre-commit
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks

echo "Installed lex-harness T1 pre-commit hook."
echo "  Source:       $HOOK_SRC"
echo "  Destination:  $TARGET/.githooks/pre-commit"
echo "  Enabled via:  git config core.hooksPath .githooks"
echo
echo "Verify:"
echo "  git config --get core.hooksPath"
echo "  ls -la .githooks/pre-commit"
EOF
chmod +x scripts/install-githooks.sh
```

- [ ] **Step 4: Verify both files exist and are executable**

```bash
ls -la templates/pre-commit scripts/install-githooks.sh
```

Expected: both files exist; both have executable (`-rwxr-xr-x`) permissions.

- [ ] **Step 5: Document the hook test cases (RED + GREEN + GREEN)**

Create a verification test document to satisfy the "RED + GREEN + GREEN" requirement from the yestay MVP plan T10:

```bash
cat > templates/pre-commit.test.md <<'EOF'
# T1 pre-commit hook test cases

> Manual test cases for the `templates/pre-commit` git hook. Run these in a scratch directory AFTER installing the hook.

## Setup

```bash
mkdir -p /tmp/lex-harness-hook-test
cd /tmp/lex-harness-hook-test
git init -b main
git config user.name "Test User"
git config user.email "test@example.com"
mkdir -p 06_claims_and_defenses .githooks
touch 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
touch 06_claims_and_defenses/PENDING_FACTS.md
cp <plugin-root>/templates/pre-commit .githooks/pre-commit
chmod +x .githooks/pre-commit
git config core.hooksPath .githooks
git add 06_claims_and_defenses/
git commit -s -m "initial commit (no AI trailer)"
```

Expected: commit succeeds (no AI trailer → hook allows).

## RED test — AI commit to PROVEN_FACTS_REGISTER should be REJECTED

```bash
echo "- id: PF-A01" >> 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
git add 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
git commit -s -m "test: add PF-A01

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

**Expected:** commit is REJECTED with:

```
[T1-WRITE-VIOLATION]
AI-trailered commit detected touching protected file:
  06_claims_and_defenses/PROVEN_FACTS_REGISTER.md

...
Rejecting commit.
```

And:

```bash
echo $?
```

Expected exit code: non-zero (1).

Reset for next test:

```bash
git reset HEAD
git checkout -- 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
```

## GREEN test 1 — Human commit to PROVEN_FACTS_REGISTER should be ALLOWED

```bash
echo "- id: PF-A01" >> 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
git add 06_claims_and_defenses/PROVEN_FACTS_REGISTER.md
git commit -s -m "promote PF-A01 after human review"
```

**Expected:** commit SUCCEEDS (no AI trailer → hook allows).

```bash
echo $?
```

Expected exit code: 0.

## GREEN test 2 — AI commit to OTHER files should be ALLOWED

```bash
echo "- id: PF-A02" >> 06_claims_and_defenses/PENDING_FACTS.md
git add 06_claims_and_defenses/PENDING_FACTS.md
git commit -s -m "propose PF-A02 via /lex-harness:fact

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>"
```

**Expected:** commit SUCCEEDS (PENDING_FACTS is not protected → hook allows even with AI trailer).

```bash
echo $?
```

Expected exit code: 0.

## Cleanup

```bash
cd /
rm -rf /tmp/lex-harness-hook-test
```

## Summary

| Test | File touched | AI trailer? | Expected | Reason |
|---|---|---|---|---|
| RED | PROVEN_FACTS_REGISTER | YES | REJECTED | T1 write-path isolation |
| GREEN 1 | PROVEN_FACTS_REGISTER | NO | ALLOWED | Human promotion is legitimate |
| GREEN 2 | PENDING_FACTS | YES | ALLOWED | PENDING_FACTS is the AI propose queue |

All three tests MUST pass for the hook to be considered working. Run these tests manually after any change to `templates/pre-commit`.
EOF
```

- [ ] **Step 6: Verify the test document**

```bash
ls templates/pre-commit.test.md
wc -l templates/pre-commit.test.md
```

Expected: file exists; ~100 lines.

- [ ] **Step 7: Commit**

```bash
git add templates/pre-commit templates/pre-commit.test.md scripts/install-githooks.sh
git commit -s -m "$(cat <<'EOF'
feat(hooks): T1 pre-commit hook + install script + test cases (T26)

The T1 write-path isolation hook implements the architectural
enforcement of "AI proposes, human promotes":

- templates/pre-commit: bash script that checks if any staged file is
  in PROTECTED_FILES (currently: PROVEN_FACTS_REGISTER.md). If yes,
  checks the commit message for a `Co-Authored-By: Claude` trailer.
  If both conditions are true, rejects the commit with
  [T1-WRITE-VIOLATION]. Otherwise allows.
- scripts/install-githooks.sh: installs the hook into a case repo.
  Sets core.hooksPath to .githooks. Can be called standalone or by
  /lex-harness:init Step 5. Handles both the local plugin path and
  the $CLAUDE_PLUGIN_ROOT path.
- templates/pre-commit.test.md: three documented test cases —
  RED (AI commit to PROVEN_FACTS_REGISTER → REJECTED),
  GREEN 1 (human commit to PROVEN_FACTS_REGISTER → ALLOWED),
  GREEN 2 (AI commit to PENDING_FACTS → ALLOWED).
  All three MUST pass for the hook to be considered working.

This is the port of yestay MVP plan T10 into the plugin templates.
The hook is JURISDICTION-AGNOSTIC — no country-specific file paths.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 27: `templates/phase3_civil_demand_skeleton.md` + `law-packs/greece/templates/phase3_civil_demand.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/templates/phase3_civil_demand_skeleton.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/templates/phase3_civil_demand.md`

Two files for this task:

1. **Skeleton** (plugin layer 1, jurisdiction-agnostic) — a universal template with `<<slot>>` placeholders that any law pack can fill. Lives in `templates/` at the plugin root.

2. **Greek instantiation** (plugin layer 2, jurisdiction-specific) — the Greek-language template that fills the skeleton's slots with actual Greek legal structure. Lives in `law-packs/greece/templates/`.

When `document-production` produces a Phase 3 demand letter for a Greek case, it:

- Reads `<case-repo>/05_legal_research/law_pack/templates/phase3_civil_demand.md` (which was copied from `law-packs/greece/templates/phase3_civil_demand.md` by `/init`)
- If the localised template is missing, falls back to `${CLAUDE_PLUGIN_ROOT}/templates/phase3_civil_demand_skeleton.md` and warns the user

Both files contain the same STRUCTURE — only the Greek one has Greek text.

- [ ] **Step 1: Write `templates/phase3_civil_demand_skeleton.md` (jurisdiction-agnostic)**

```bash
cat > templates/phase3_civil_demand_skeleton.md <<'EOF'
<!--
  Jurisdiction-agnostic Phase 3 civil demand skeleton.

  This file is the FALLBACK for document-production when the active
  law pack does not ship a localised phase3_civil_demand.md template.

  Law packs SHOULD ship a localised version with actual legal-language
  text filled in. See law-packs/greece/templates/phase3_civil_demand.md
  for a reference implementation.

  Slot format: <<slot_name>> — populated by document-production.
-->

---
doc_type: phase3_civil_demand
jurisdiction_agnostic: true
generated_by: document-production
verify_gate:
  passed: false
  date: TBD
  failures: []
---

# <<DOCUMENT_TITLE>>

**To:** <<OPPOSING_PARTY_NAME>>
**Address:** <<OPPOSING_PARTY_ADDRESS>>
**From:** <<CLAIMANT_NAME>>
**Date:** <<DRAFT_DATE>>
**Re:** <<DISPUTE_SUBJECT>>

---

## 1. Identification of the parties

<<PARTY_IDENTIFICATION_BLOCK>>

## 2. Factual background

The following facts are established by the evidence listed in Section 5 below:

<<FACTUAL_BACKGROUND_BLOCK>>

Each numbered paragraph in this section corresponds to one or more PF codes in the footer block. Facts are stated as claims, not argued — the legal significance is developed in Section 3.

## 3. Legal basis

The legal basis for this demand rests on the following statutory provisions, quoted verbatim from the applicable law:

<<LEGAL_BASIS_BLOCK>>

<!--
  For each cited article, the populated version should include:
  - The article ID (e.g., "Art. 592 ΑΚ" or "§ 535 BGB")
  - The verbatim text in the active language
  - A one-sentence application to the facts

  Example:

  ### <<ARTICLE_ID>>

  > <<verbatim statute text>>

  **Application:** <<one sentence applying the article to the facts above>>
-->

## 4. Demand

Based on the facts in Section 2 and the law in Section 3, <<CLAIMANT_NAME>> demands that <<OPPOSING_PARTY_NAME>>:

<<DEMAND_BLOCK>>

Within <<RESPONSE_DEADLINE_DAYS>> days of receipt of this letter.

## 5. Supporting evidence

The following evidence items support the facts in Section 2:

<<EVIDENCE_LIST>>

Each item is registered in `04_evidence/EVIDENCE_INDEX.md` with a SHA-256 hash and RFC3161 timestamp. Copies are available on request.

## 6. Consequences of non-compliance

If <<OPPOSING_PARTY_NAME>> fails to comply within the response deadline, <<CLAIMANT_NAME>> reserves the right to:

<<ESCALATION_OPTIONS_BLOCK>>

<!--
  Escalation options are jurisdiction-specific. The law pack's localised
  template should enumerate the actual available forums (civil court,
  consumer ombudsman, data protection authority, criminal referral, etc.).
-->

## 7. Settlement offer (optional)

<<SETTLEMENT_OFFER_BLOCK>>

<!--
  Only included if 07_strategy/core/SETTLEMENT_ECONOMICS.md has a
  ZOPA computed. Otherwise this section is omitted.
-->

---

## Signature

<<CLAIMANT_NAME>>
<<CLAIMANT_ADDRESS>>
<<CLAIMANT_CONTACT>>
<<SIGNATURE_DATE>>

---

## Footer block (mandatory per document-production skill)

```yaml
---
footer_block:
  pf_ids:
    - <<PF_ID_1>>
    - <<PF_ID_2>>
  law_articles:
    - <<ARTICLE_ID_1>>
    - <<ARTICLE_ID_2>>
  evidence_items:
    - <<EVIDENCE_ID_1>>
    - <<EVIDENCE_ID_2>>
  da_review_refs:
    - <<DA_REVIEW_FILENAME>>
verify_gate:
  passed: <<true_or_false>>
  date: <<YYYY-MM-DD>>
  failures: []
manual_verification_required:
  - <<any_manual_verification_item>>
---
```
EOF
```

- [ ] **Step 2: Verify the skeleton is jurisdiction-agnostic**

```bash
python3 - <<'PY'
import sys
banned = ['Greek', 'Greece', 'ΑΚ', 'ΚΠολΔ', 'Yestay', 'VIAMAR',
          'kodiko.gr', 'lawspot.gr', 'Άρειος Πάγος', 'Eirinodikio',
          'Εθνάρχου Μακαρίου', 'εξώδικο']
with open('templates/phase3_civil_demand_skeleton.md') as f:
    content = f.read()
hits = [w for w in banned if w in content]
if hits:
    sys.exit(f"PR-01 violation: {hits}")
print("OK — skeleton is jurisdiction-agnostic")
PY
```

Expected: `OK`. (Note: the comment in the file mentions "Greek" once as a pointer to the reference implementation — that's fine in a comment but NOT in the body. If the grep catches it, move it to a different phrasing like "reference implementation in the Greek law pack".)

Actually re-check: the comment says "See law-packs/greece/templates/phase3_civil_demand.md for a reference implementation." The word "greece" is lowercase as a directory name — let the check allow it. Update the check:

```bash
python3 - <<'PY'
import re, sys
banned = ['ΑΚ', 'ΚΠολΔ', 'Yestay', 'VIAMAR',
          'kodiko.gr', 'lawspot.gr', 'Άρειος Πάγος',
          'εξώδικο', 'Εθνάρχου']
# Remove comments first, then check
with open('templates/phase3_civil_demand_skeleton.md') as f:
    content = f.read()
# Strip HTML comments
body = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
hits = [w for w in banned if w in body]
if hits:
    sys.exit(f"PR-01 violation (outside comments): {hits}")
print("OK — skeleton body is jurisdiction-agnostic (comments may mention Greek as a pointer)")
PY
```

Expected: `OK`.

- [ ] **Step 3: Create the Greek law pack templates directory**

```bash
mkdir -p law-packs/greece/templates
```

- [ ] **Step 4: Write `law-packs/greece/templates/phase3_civil_demand.md` (Greek instantiation)**

```bash
cat > law-packs/greece/templates/phase3_civil_demand.md <<'EOF'
<!--
  Greek-language Phase 3 civil demand template (εξώδικη διαμαρτυρία και
  δήλωση). Fills the jurisdiction-agnostic skeleton with Greek legal
  structure + placeholder Greek text + actual ΑΚ / ΚΠολΔ article
  references.

  Used by document-production when the active jurisdiction is 'greece'.
  Populated at runtime from the case repo's 06_claims_and_defenses/
  and 07_strategy/ content.
-->

---
doc_type: phase3_civil_demand
jurisdiction: greece
language: el
pack_version: <<PACK_VERSION>>
generated_by: document-production
verify_gate:
  passed: false
  date: TBD
  failures: []
---

# ΕΞΩΔΙΚΗ ΔΙΑΜΑΡΤΥΡΙΑ – ΠΡΟΣΚΛΗΣΗ – ΔΗΛΩΣΗ

**ΠΡΟΣ:**
`<<OPPOSING_PARTY_NAME>>`
`<<OPPOSING_PARTY_LEGAL_FORM>>` (π.χ. Ανώνυμη Εταιρεία / ΙΚΕ / ΕΠΕ)
ΑΦΜ: `<<OPPOSING_PARTY_AFM>>`
ΔΟΥ: `<<OPPOSING_PARTY_DOY>>`
Δ/νση: `<<OPPOSING_PARTY_ADDRESS>>`

**ΑΠΟ:**
`<<CLAIMANT_NAME>>`
ΑΦΜ: `<<CLAIMANT_AFM>>`
Δ/νση: `<<CLAIMANT_ADDRESS>>`

**Αθήνα, `<<DRAFT_DATE>>`**

**ΘΕΜΑ: `<<DISPUTE_SUBJECT>>`**

---

## Ι. Ιστορικό

Όπως γνωρίζετε:

<<FACTUAL_BACKGROUND_BLOCK>>

<!--
  Each numbered paragraph here references one or more PF codes from
  06_claims_and_defenses/PROVEN_FACTS_REGISTER.md. The populated version
  inlines the fact text in Greek with the PF code as a parenthetical.

  Example:
  1. Την <<date>>, <<fact text in Greek>> (PF-A29).
  2. Την <<date>>, <<fact text>> (PF-A30).
-->

## ΙΙ. Νομικό πλαίσιο

Η απαίτησή μου θεμελιώνεται στις ακόλουθες διατάξεις, που παρατίθενται αυτολεξεί:

<<LEGAL_BASIS_BLOCK>>

<!--
  Example populated block (showing the format document-production will
  use — inlining verbatim article text from law-packs/greece/core/
  or law-packs/greece/modules/tenancy/):

  ### Άρθρο 592 ΑΚ — Φθορά από τη συμφωνημένη χρήση

  > <<verbatim Greek text of Art. 592 ΑΚ from the law pack's core file>>

  **Εφαρμογή:** Η φθορά που παρουσιάζεται στο μίσθιο αντιστοιχεί σε
  συνήθη χρήση κατοικίας για <<N>> μήνες και εμπίπτει στην εξαίρεση
  του άρθρου 592 ΑΚ.

  ### Άρθρο 602 ΑΚ — Αποσβεστική προθεσμία 6 μηνών

  > <<verbatim Greek text of Art. 602 ΑΚ>>

  **Εφαρμογή:** Οποιαδήποτε αξίωση αποζημίωσης από φθορά του μισθίου
  πρέπει να ασκηθεί εντός 6 μηνών από την παράδοση. Η προθεσμία αυτή
  λήγει την <<limitation_deadline>>.

  (Verbatim text is loaded from 05_legal_research/law_pack/core/AK_592.md
  etc. at population time. The sha256 in the article frontmatter is
  verified against the inlined text — if they don't match, Stage 3b of
  the verify-gate fails with [STATUTE-DRIFT].)
-->

## ΙΙΙ. Η απαίτησή μου

Για τους παραπάνω λόγους, ΔΙΑΜΑΡΤΥΡΟΜΑΙ για τη συμπεριφορά σας και ΣΑΣ ΚΑΛΩ:

<<DEMAND_BLOCK>>

<!--
  Example:
  1. Να μου επιστρέψετε το ποσό των <<amount>> € εντός <<N>> ημερών από
     την επίδοση της παρούσας.
  2. Να μου παραδώσετε αντίγραφα των εγγράφων που προβλέπονται στο
     άρθρο <<article>> εντός της ίδιας προθεσμίας.
-->

Εντός αποκλειστικής προθεσμίας `<<RESPONSE_DEADLINE_DAYS>>` ημερών από την επίδοση της παρούσας.

## IV. Αποδεικτικά στοιχεία

Τα παραπάνω γεγονότα αποδεικνύονται από:

<<EVIDENCE_LIST>>

<!--
  Example:
  - E-101: Σύμβαση μίσθωσης της <<date>>
  - E-102: Τιμολόγιο αρ. <<number>>
  - E-103: Email της <<date>> από <<sender>>

  All referenced items are registered in 04_evidence/EVIDENCE_INDEX.md
  with SHA-256 hashes and RFC3161 timestamps.
-->

## V. Συνέπειες μη συμμόρφωσης

Σε περίπτωση μη συμμόρφωσής σας εντός της παραπάνω προθεσμίας, επιφυλάσσομαι ρητά να:

<<ESCALATION_OPTIONS_BLOCK>>

<!--
  Greek escalation options (from law-packs/greece/forums.yaml):

  1. Ασκήσω αγωγή ενώπιον του αρμόδιου Ειρηνοδικείου Αθηνών εντός της
     προθεσμίας του άρθρου 602 ΑΚ.
  2. Υποβάλω καταγγελία στον Συνήγορο του Καταναλωτή (ν. 3297/2004).
  3. Υποβάλω καταγγελία στην Αρχή Προστασίας Δεδομένων Προσωπικού
     Χαρακτήρα (ν. 4624/2019 και Κανονισμός (ΕΕ) 2016/679).
  4. Αναφερθώ στις αρμόδιες φορολογικές αρχές (ΑΑΔΕ) για τις
     διαπιστωθείσες φορολογικές παραβάσεις.
  5. Υποβάλω μήνυση για τα προκύπτοντα ποινικά αδικήματα.

  Only include the options that apply given the case's specific CH/CC
  content and the forum precondition rules in forums.yaml.
-->

## VI. Πρόταση συμβιβασμού (προαιρετικό)

<<SETTLEMENT_OFFER_BLOCK>>

<!--
  Only included if 07_strategy/core/SETTLEMENT_ECONOMICS.md has a ZOPA
  computed. Otherwise this section is omitted. Example:

  Προς αποφυγή δικαστικής διαμάχης, είμαι διατεθειμένος να δεχθώ
  συμβιβαστικά το ποσό των <<zopa_low>> €, υπό την προϋπόθεση ότι θα
  καταβληθεί εντός <<N>> ημερών και θα συνοδεύεται από γραπτή
  παραίτηση από οποιαδήποτε περαιτέρω απαίτηση εκατέρωθεν.
-->

---

**Με την επιφύλαξη κάθε νόμιμου δικαιώματός μου,**

`<<CLAIMANT_NAME>>`
`<<CLAIMANT_ADDRESS>>`
`<<CLAIMANT_CONTACT>>`
`<<SIGNATURE_DATE>>`

---

## Footer block (mandatory per document-production skill)

```yaml
---
footer_block:
  pf_ids:
    - <<PF_ID_1>>
    - <<PF_ID_2>>
  law_articles:
    - AK_592
    - AK_602
    - <<OTHER_ARTICLE_IDS>>
  evidence_items:
    - <<EVIDENCE_ID_1>>
    - <<EVIDENCE_ID_2>>
  da_review_refs:
    - <<DA_REVIEW_FILENAME>>
verify_gate:
  passed: <<true_or_false>>
  date: <<YYYY-MM-DD>>
  failures: []
manual_verification_required:
  - <<any_manual_verification_item>>
---
```
EOF
```

- [ ] **Step 5: Verify the Greek template is well-formed**

```bash
ls law-packs/greece/templates/phase3_civil_demand.md
wc -l law-packs/greece/templates/phase3_civil_demand.md
head -20 law-packs/greece/templates/phase3_civil_demand.md
```

Expected: file exists; ~200 lines.

- [ ] **Step 6: Verify the two files use the same slot names**

The skeleton's slots and the Greek template's slots must match, so `document-production` can populate either with the same logic.

```bash
python3 - <<'PY'
import re, sys

def extract_slots(path):
    with open(path) as f:
        content = f.read()
    # Slots are <<NAME>>
    slots = set(re.findall(r'<<([A-Z_][A-Z0-9_]*)>>', content))
    return slots

skel = extract_slots('templates/phase3_civil_demand_skeleton.md')
grk = extract_slots('law-packs/greece/templates/phase3_civil_demand.md')

only_skel = skel - grk
only_grk = grk - skel

print(f"Skeleton slots: {len(skel)}")
print(f"Greek slots: {len(grk)}")
print(f"Common slots: {len(skel & grk)}")
print(f"Only in skeleton: {sorted(only_skel)}")
print(f"Only in Greek: {sorted(only_grk)}")

# The Greek template may have extra slots (AFM, DOY, etc.) but every
# skeleton slot SHOULD appear in the Greek template (barring 1-2
# intentional exceptions).
missing_in_greek = only_skel - {'DOCUMENT_TITLE', 'PARTY_IDENTIFICATION_BLOCK'}
if missing_in_greek:
    print(f"WARNING: skeleton slots missing from Greek template: {missing_in_greek}")
else:
    print("OK — Greek template covers all skeleton slots (modulo intentional exclusions)")
PY
```

Expected: the Greek template covers all skeleton slots (or the warning lists only acceptable exclusions).

- [ ] **Step 7: Commit**

```bash
git add templates/phase3_civil_demand_skeleton.md law-packs/greece/templates/phase3_civil_demand.md
git commit -s -m "$(cat <<'EOF'
feat(templates): phase3 civil demand skeleton + Greek instantiation (T27)

Two-file split per the 3-layer architecture (PR-01):

- templates/phase3_civil_demand_skeleton.md (layer 1, jurisdiction-
  agnostic): universal skeleton with <<slot>> placeholders. Used as
  a fallback by document-production when the active law pack lacks
  a localised template. JURISDICTION-AGNOSTIC body (comments may
  mention "Greek" as a pointer to the reference implementation).

- law-packs/greece/templates/phase3_civil_demand.md (layer 2, Greek):
  Greek-language εξώδικη διαμαρτυρία template with actual ΑΚ article
  references (592, 602) and Greek legal structure. The verbatim
  statute text is inlined from law-packs/greece/core/AK_*.md files
  at population time — the template itself contains placeholder
  comments showing the format.

Both files use the SAME slot names so document-production can
populate either with the same logic. A verification script confirms
slot parity with acceptable exceptions (DOCUMENT_TITLE and
PARTY_IDENTIFICATION_BLOCK are abstract in the skeleton but
fragmented into specific Greek fields in the localised template).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## End of Part 3

Tasks T16 through T27 are complete. The remaining tasks (T28 onwards) cover:

- T28–T29: Remaining Greek law pack modules (tax_invoices, corporate)
- T30: Codex bootstrap script
- T31: Pack validation script
- T32: Tests directory
- T33: ARCHITECTURE.md
- T34: PLUGIN_REQUIREMENTS.md + ROADMAP.md
- T35: TOOL_OPTIONALITY.md + SECURITY.md
- T36: CI workflow + GitHub issue templates
- T37: v0.1.0 tag + GitHub release

Those tasks continue in Part 4: `2026-04-07-lex-harness-v0.1-part4.md`.
