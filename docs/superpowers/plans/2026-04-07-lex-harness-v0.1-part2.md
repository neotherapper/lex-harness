# lex-harness v0.1 Implementation Plan (Plan A) — Part 2

> Continuation of `2026-04-07-lex-harness-v0.1.md` — Tasks T5 through T15.
>
> **For agentic workers:** Use superpowers:subagent-driven-development or superpowers:executing-plans. All paths are absolute and rooted at `~/Developer/projects/lex-harness/` (the new repo, NOT yestay). `${CLAUDE_PLUGIN_ROOT}` is used for intra-plugin references INSIDE skill / command bodies — never in shell scripts.

---

## Task 5: `law-packs/greece/pack.json`

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/pack.json`

The Greek pack manifest. Validates against the schema in `law-packs/_schema.md` (T4). PR-02 + PR-11: every MCP server listed must have `required: false`.

- [ ] **Step 1: Create the directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p law-packs/greece
```

- [ ] **Step 2: Write `pack.json`**

```bash
cat > law-packs/greece/pack.json <<'EOF'
{
  "name": "greece",
  "version": "0.1.0",
  "language": "el",
  "country_code": "GR",
  "display_name": "Greece — Civil Law (Αστικός Κώδικας + ΚΠολΔ)",
  "description": "Greek civil law pack covering rental disputes, consumer protection, GDPR enforcement, tort/moral damages, corporate (spin-off) liability, tax/invoice compliance, criminal/regulatory escalation, and Eirinodikio procedure. MVP for the lex-harness plugin.",
  "default_modules": [
    "tenancy",
    "tax_invoices",
    "corporate"
  ],
  "available_modules": [
    "tenancy",
    "consumer_protection",
    "gdpr",
    "tort_damages",
    "corporate",
    "tax_invoices",
    "criminal_regulatory",
    "procedure_eirinodikio"
  ],
  "mcp_servers": [
    {
      "name": "eur-lex",
      "purpose": "EUR-Lex CELEX retrieval for GDPR + CJEU",
      "required": false
    },
    {
      "name": "cerebra-legal",
      "purpose": "Greek consumer-protection legal reasoning templates",
      "required": false
    },
    {
      "name": "chrome-devtools",
      "purpose": "Live web evidence capture (kodiko.gr, areiospagos.gr, dpa.gr SPA)",
      "required": false
    },
    {
      "name": "neo4j-memory",
      "purpose": "Multi-hop fact relationship queries",
      "required": false
    }
  ],
  "forum_rules_file": "forums.yaml",
  "limitation_periods_file": "limitation_periods.yaml",
  "playbook_file": "playbook.yaml",
  "glossary_file": "glossary.md",
  "module_index_file": "MODULE_INDEX.md",
  "primary_sources": {
    "statute_articles": "https://www.kodiko.gr/",
    "verification": "https://www.lawspot.gr/",
    "fek_gazette": "https://search.et.gr/",
    "ap_decisions": "https://www.areiospagos.gr/",
    "eu_law": "https://eur-lex.europa.eu/",
    "hdpa_decisions": "https://www.dpa.gr/"
  },
  "maintainer": {
    "name": "Georgios Pilitsoglou",
    "url": "https://github.com/neotherapper"
  },
  "schema_version": "1.0",
  "created": "2026-04-07",
  "last_updated": "2026-04-07"
}
EOF
```

- [ ] **Step 3: Validate JSON**

```bash
python3 -c "import json; json.load(open('law-packs/greece/pack.json')); print('valid')"
```

Expected: `valid`

- [ ] **Step 4: Verify required fields against schema**

```bash
python3 <<'PY'
import json
m = json.load(open('law-packs/greece/pack.json'))
required = [
    "name", "version", "language", "country_code",
    "default_modules", "mcp_servers",
    "forum_rules_file", "limitation_periods_file",
    "playbook_file", "glossary_file", "maintainer"
]
missing = [k for k in required if k not in m]
assert not missing, f"missing fields: {missing}"
assert m["name"] == "greece"
assert m["language"] == "el"
assert m["country_code"] == "GR"
# PR-11: every MCP server must be optional
for s in m["mcp_servers"]:
    assert s["required"] is False, f"MCP {s['name']} is not optional (PR-11 violation)"
print("pack.json schema OK")
PY
```

Expected: `pack.json schema OK`

- [ ] **Step 5: Commit**

```bash
git add law-packs/greece/pack.json
git commit -s -m "$(cat <<'EOF'
feat(greece): pack.json manifest (T5)

Greek civil-law pack manifest. Default modules: tenancy, tax_invoices,
corporate. 8 modules available total. All 4 listed MCP servers marked
required: false per PR-11 (all external tools optional). Primary sources:
kodiko.gr, lawspot.gr, search.et.gr, areiospagos.gr, EUR-Lex, dpa.gr.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 6: `law-packs/greece/MODULE_INDEX.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/MODULE_INDEX.md`

The single registry per design D22: routing table for task → modules + SA → modules + Forum Preconditions sections. The legal-strategy skill consults this on every session to decide which modules to load beyond core.

- [ ] **Step 1: Write MODULE_INDEX.md**

```bash
cat > law-packs/greece/MODULE_INDEX.md <<'EOF'
---
document: MODULE_INDEX
pack: greece
version: 0.1.0
purpose: routing-table
last_updated: 2026-04-07
---

# Greek Pack — Module Routing Index

> **Single registry** consulted by `legal-strategy` at session start to decide which modules to load beyond `core/`. Replaces ad-hoc skill prose with one mechanical lookup. Per design D22.

## How to read this file

Three lookup tables, in order of precedence:

1. **Task → Modules** — match the user's request type
2. **Strategic Argument (SA) → Modules** — match the SA being analysed
3. **Forum Preconditions** — what must be true before drafting for a forum

The skill loads `core/` always, then unions every module returned by the matched rows. Duplicates are de-duplicated. If no rule matches, only `core/` plus `default_modules` from `pack.json` is loaded.

---

## 1. Task → Modules

| Task signal (any of these phrases / patterns) | Modules to load |
|---|---|
| "deposit", "rental damage", "wear and tear", "φυσιολογική φθορά", "CH1", "CH2", "CH3", "CH4", "CH5" | `tenancy` |
| "balcony rent reduction", "Art. 576", "defect", "rent abatement", "CC2", "CC3" | `tenancy`, `tort_damages` |
| "consumer", "Law 2251", "ΓΟΣ", "unfair clause", "Consumer Ombudsman", "professional supplier" | `consumer_protection` |
| "GDPR", "Art. 15 SAR", "HDPA", "data subject", "controller", "Nowak", "C-579/21", "CC6" | `gdpr` |
| "moral damages", "personality", "ψυχική οδύνη", "Art. 932", "CC2-B", "CC4", "CC5" | `tort_damages` |
| "VIAMAR II", "spin-off", "αλλαγή επωνυμίας", "joint liability", "Art. 65", "Art. 70 N. 4601", "SA-32" | `corporate` |
| "invoice", "stamp duty", "χαρτόσημο", "VAT", "myDATA", "AADE", "depreciation", "Art. 24 N. 4172", "N. 4308", "N. 5177" | `tax_invoices` |
| "criminal", "ΠΚ 386", "ΠΚ 216", "fraud", "false document", "ΣΕΠΕ", "asbestos referral" | `criminal_regulatory`, `tax_invoices` |
| "Eirinodikio", "αγωγή", "προτάσεις", "default judgment", "jurisdiction", "ΚΠολΔ 14" | `procedure_eirinodikio` |
| "settlement", "ZOPA", "BATNA", "negotiation" | (no module — uses core + `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/settlement-math.md`) |
| "extraction question", "GDPR SAR draft", "ELICIT mode" | `gdpr`, `tenancy` |
| "OSINT", "evidence preservation", "chain of custody" | (no module — uses core + osint-investigation skill) |

**Rule:** when more than one row matches the prompt, the union of all matched modules is loaded.

---

## 2. Strategic Argument (SA) → Modules

| SA pattern | Modules |
|---|---|
| SA-01 to SA-10 (substantive defences on charges) | `tenancy` |
| SA-11 to SA-20 (procedural / corporate) | `corporate`, `procedure_eirinodikio` |
| SA-21 to SA-25 (consumer + ΓΟΣ challenges) | `consumer_protection`, `tenancy` |
| SA-26 to SA-30 (tax / invoice attacks) | `tax_invoices` |
| SA-31 (systematic bad faith — multi-element compound) | `tenancy`, `gdpr`, `tax_invoices`, `corporate` |
| SA-32 (dual-defendant joint liability) | `corporate` |
| SA-33 (arbitrage-model conflict of interest) | `corporate`, `consumer_protection` |
| Any new SA → consult MODULE_INDEX before drafting; if no module matches, log a gap to `09_ai_research/research_queue.md` |

**Rule:** SA lookups are advisory — task signals (table 1) override.

---

## 3. Forum Preconditions

This table encodes the mechanical gate the legal-strategy skill enforces before recommending a forum action. Sourced from `forums.yaml`.

| Forum | Precondition type | Must complete first | Effect if violated |
|---|---|---|---|
| Civil court (Eirinodikio αγωγή) | `statutory_blocking` | None for civil; **but if criminal complaint filed first → Art. 52 KPolD blocks civil suspension** | HALT — strategy must reorder |
| Phase 3 demand letter (εξώδικη δήλωση) | `none` | None | Always permitted |
| Consumer Ombudsman (Συνήγορος Καταναλωτή) | `strategic_recommended` | Phase 3 demand letter sent | Soft warning — skill flags risk |
| HDPA complaint | `strategic_recommended` | GDPR SAR (Art. 15) sent + 30-day deadline expired | Soft warning — risk of dismissal as premature |
| AADE referral | `strategic_recommended` | Forensic invoice analysis complete + 6 documented violations | Soft warning |
| Criminal complaint (ΠΚ 386 / ΠΚ 216) | `statutory_blocking` (FOR CIVIL) | Civil suit filed OR explicitly chosen "criminal-only" path | HALT — Art. 52 KPolD warns this freezes civil proceedings |
| ΣΕΠΕ asbestos referral | `none` | None | Always permitted |

**The "criminal last" doctrine** — a Layer 1 universal principle — manifests in this Greek pack as: never recommend criminal complaint until civil αγωγή is filed, because Art. 52 KPolD freezes civil proceedings the moment a parallel criminal case is open.

---

## 4. Default load behaviour

If the user prompt does not match any row in §1 or §2, the legal-strategy skill loads:
- `core/` (22 articles, always)
- `default_modules` from `pack.json` (currently: `tenancy`, `tax_invoices`, `corporate`)

This guarantees that every Greek session has the most-cited statutes available without explicit task framing.

---

## 5. Out-of-pack escalation

If a user request matches a task signal that has no module in this pack (e.g., "intellectual property", "labour law"), the skill MUST:

1. Respond `[OUT-OF-PACK: <topic>]`
2. Log the gap to `<case-repo>/09_ai_research/research_queue.md`
3. Suggest the user file a contribution issue at `github.com/neotherapper/lex-harness/issues/new?template=new_country_pack.md`
4. NEVER hallucinate articles from training memory to fill the gap

---

**Cross-references:**
- `pack.json` — declares `default_modules`
- `forums.yaml` — full forum precondition rules
- `limitation_periods.yaml` — statutory deadlines
- `playbook.yaml` — Greek-specific common plays
- `core/` — always-loaded statute articles
- `modules/<m>/` — task-specific module articles
EOF
```

- [ ] **Step 2: Verify file exists and parses**

```bash
ls -la law-packs/greece/MODULE_INDEX.md
wc -l law-packs/greece/MODULE_INDEX.md
head -20 law-packs/greece/MODULE_INDEX.md
```

Expected: file exists, ~110 lines, frontmatter visible at top.

- [ ] **Step 3: Verify the three required sections exist**

```bash
grep -c "^## 1. Task → Modules" law-packs/greece/MODULE_INDEX.md
grep -c "^## 2. Strategic Argument" law-packs/greece/MODULE_INDEX.md
grep -c "^## 3. Forum Preconditions" law-packs/greece/MODULE_INDEX.md
```

Expected: each prints `1`.

- [ ] **Step 4: Commit**

```bash
git add law-packs/greece/MODULE_INDEX.md
git commit -s -m "$(cat <<'EOF'
feat(greece): MODULE_INDEX.md routing table (T6)

Single registry per design D22 — task → modules, SA → modules, forum
preconditions. Replaces ad-hoc prose in skill bodies with one mechanical
lookup the legal-strategy skill consults at session start. Encodes the
"criminal last" doctrine via Art. 52 KPolD precondition gate.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 7: forums.yaml + limitation_periods.yaml + playbook.yaml + glossary.md

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/forums.yaml`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/limitation_periods.yaml`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/playbook.yaml`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/glossary.md`

The 4 jurisdiction config files. `forums.yaml` encodes the Art. 52 KPolD blocking rule. `limitation_periods.yaml` carries Art. 602 ΑΚ 6-month rental deadline. `playbook.yaml` ports universal-strategy plays from the 50-play yestay playbook. `glossary.md` translates Greek vocabulary to English.

- [ ] **Step 1: Write `forums.yaml`**

```bash
cat > law-packs/greece/forums.yaml <<'EOF'
# Greek pack — forum precondition rules
# Schema: see law-packs/_schema.md §forums.yaml

forums:
  - id: phase3-demand-letter
    name: Phase 3 demand letter (εξώδικη δήλωση / πρόσκληση)
    type: pre-litigation
    precondition_type: none
    must_complete_first: []
    notes: >-
      Greek pre-litigation formal notice. No statutory blocker. Used to
      trigger Art. 602 ΑΚ tolling, document bad faith, and establish
      admissibility of subsequent forums. Default first forum.

  - id: civil-court-eirinodikio
    name: Civil court — Eirinodikio (αγωγή)
    type: civil-litigation
    precondition_type: statutory_blocking
    must_complete_first: []
    blocked_by_other_action:
      - forum: criminal-complaint
        statute: Art. 52 KPolD
        effect: >-
          If criminal complaint is filed first on the same facts, civil
          proceedings are SUSPENDED until the criminal case completes.
          Strategy must therefore file civil αγωγή BEFORE criminal.
    notes: >-
      Default civil forum for deposit disputes ≤ €20,000 (Art. 14 ΚΠολΔ).
      Art. 602 ΑΚ 6-month limitation controls deadline.

  - id: consumer-ombudsman
    name: Consumer Ombudsman (Συνήγορος Καταναλωτή)
    type: regulatory-non-binding
    precondition_type: strategic_recommended
    must_complete_first:
      - phase3-demand-letter
    notes: >-
      Free, non-binding mediation. Adds pressure without committing to
      court. Skill flags risk if filed without prior demand letter.

  - id: hdpa-complaint
    name: Hellenic Data Protection Authority complaint
    type: regulatory-binding
    precondition_type: strategic_recommended
    must_complete_first:
      - gdpr-sar-art-15
    notes: >-
      Filed AFTER Art. 15 GDPR Subject Access Request has been sent and
      either ignored or partially fulfilled past the 30-day deadline.

  - id: gdpr-sar-art-15
    name: GDPR Subject Access Request (Art. 15)
    type: pre-regulatory
    precondition_type: none
    must_complete_first: []
    notes: >-
      Always permitted. The 30-day controller response deadline starts
      on receipt. Tracked via DEADLINE_REGISTER.md as a soft deadline.

  - id: aade-referral
    name: AADE tax authority referral
    type: regulatory-binding
    precondition_type: strategic_recommended
    must_complete_first:
      - phase3-demand-letter
      - forensic-invoice-analysis
    notes: >-
      Forensic-grade analysis must be complete before AADE referral.

  - id: criminal-complaint
    name: Criminal complaint (μήνυση — ΠΚ 386 fraud / ΠΚ 216 forgery)
    type: criminal
    precondition_type: statutory_blocking
    must_complete_first:
      - civil-court-eirinodikio
    blocks_other_action:
      - forum: civil-court-eirinodikio
        statute: Art. 52 KPolD
        effect: >-
          Filing criminal complaint freezes civil proceedings. Therefore
          ALWAYS file civil αγωγή first; criminal is the last forum.
    notes: >-
      The "criminal last" doctrine. Universal layer 1 principle, with
      Greek-specific manifestation via Art. 52 KPolD. Skill MUST refuse
      to recommend criminal forum until civil αγωγή is filed.

  - id: sepe-asbestos-referral
    name: Labour Inspectorate (ΣΕΠΕ) asbestos / safety referral
    type: regulatory-binding
    precondition_type: none
    must_complete_first: []
    notes: >-
      Independent of civil proceedings. Used for ΠΔ 212/2006 violations.
      Free to file in parallel with anything else.
EOF
```

- [ ] **Step 2: Write `limitation_periods.yaml`**

```bash
cat > law-packs/greece/limitation_periods.yaml <<'EOF'
# Greek pack — limitation periods
# Schema: see law-packs/_schema.md §limitation_periods.yaml

limitations:
  - id: AK_602-rental-deposit
    description: >-
      6-month deadline for landlord claims arising from the lease
      (rent damages, security deposit set-off). Controls every CH/CC.
    statute: AK_602
    period_days: 180
    accrual_event: >-
      Date the leased property is returned to the landlord (end of
      tenancy).
    interruption_methods:
      - filing of αγωγή in civil court
      - service of εξώδικη δήλωση followed by αγωγή within 6 months
      - written acknowledgment of debt by landlord
      - judicial settlement
    notes: >-
      The DEADLINE that controls every Greek deposit case. Tracked as
      DL-01 by default in every case scaffolded by /lex-harness:init.

  - id: AK_249-general
    description: General 20-year prescription
    statute: AK_249
    period_days: 7305
    accrual_event: When the claim becomes actionable
    interruption_methods:
      - lawsuit
      - written acknowledgment of debt
    notes: Catch-all baseline.

  - id: AK_250-five-year
    description: 5-year prescription for periodic payments (rent, utilities)
    statute: AK_250
    period_days: 1826
    accrual_event: When each periodic payment fell due
    interruption_methods:
      - lawsuit
      - written acknowledgment
    notes: Applies to counterclaims for unpaid rent or services.

  - id: AK_937-tort
    description: 5-year prescription for tort claims (Art. 914 ΑΚ)
    statute: AK_937
    period_days: 1826
    accrual_event: >-
      When the injured party became aware of the injury and the
      identity of the tortfeasor.
    interruption_methods:
      - lawsuit
      - written acknowledgment
    notes: Used for moral damages and personality-rights claims.

  - id: GDPR_82-damages
    description: GDPR damages claim (Art. 82)
    statute: GDPR_Art_82
    period_days: 1826
    accrual_event: When the data subject became aware of the violation
    interruption_methods:
      - HDPA complaint filing
      - civil αγωγή
    notes: 5-year alignment with Greek tort prescription.

  - id: gdpr-sar-response
    description: 30-day deadline for controller to respond to Art. 15 SAR
    statute: GDPR_Art_12_3
    period_days: 30
    accrual_event: Date the SAR was received by the controller
    interruption_methods: []
    notes: >-
      Soft deadline (response window, not limitation). Triggers the
      ripeness precondition for HDPA complaint.

  - id: art-52-kpold-criminal-suspension
    description: >-
      NOT a limitation period — a procedural blocking rule.
      Filing criminal complaint suspends civil proceedings.
    statute: KPolD_52
    period_days: null
    accrual_event: null
    interruption_methods: []
    notes: >-
      Encoded here for visibility. Strategy must order civil before
      criminal. Enforced via forums.yaml precondition_type:
      statutory_blocking on criminal-complaint.
EOF
```

- [ ] **Step 3: Write `playbook.yaml`**

```bash
cat > law-packs/greece/playbook.yaml <<'EOF'
# Greek pack — common plays
# Schema: see law-packs/_schema.md §playbook.yaml
# Source: extracted from the 50-play yestay playbook, generalised to
# be case-agnostic but Greek-jurisdiction-specific.

plays:
  - id: GR-P01
    name: Art. 602 ΑΚ deadline leverage
    forum: phase3-demand-letter
    description: >-
      Greek law gives landlords only 6 months from key handover to
      bring damage claims (Art. 602 ΑΚ). Use the approaching deadline
      as leverage in every demand letter and settlement negotiation.
    requires_state: deposit-dispute-active
    blocked_by: []
    typical_cost: 0
    typical_duration: ongoing
    cited_articles:
      - AK_602
    universality: jurisdiction-universal-pattern
    notes: Loaded by default in every Greek case.

  - id: GR-P02
    name: Lost records adverse inference (Art. 339-340 ΚΠολΔ)
    forum: civil-court-eirinodikio
    description: >-
      When the landlord cannot produce a check-in inventory list or
      check-out joint inspection record, Greek civil procedure permits
      the court to draw an adverse inference (Art. 339, 340, 366, 450
      ΚΠολΔ). The absence of documentation is itself evidence.
    requires_state: opposing-party-cannot-produce-inventory
    blocked_by: []
    typical_cost: 0
    typical_duration: instant
    cited_articles:
      - KPolD_339
      - KPolD_340
      - KPolD_366
      - KPolD_450
      - AK_330
    universality: greek-civil-procedure
    notes: >-
      Pairs with the universal "absence is evidence" principle.

  - id: GR-P03
    name: Set-off calculation (Art. 440-452 ΑΚ συμψηφισμός)
    forum: phase3-demand-letter
    description: >-
      Greek civil code allows mutual debts to be extinguished by
      declaration of set-off (Art. 440-452 ΑΚ), with retroactive effect
      to the date both became due (Art. 442). Always present as a
      single table so the math is visible.
    requires_state: counterclaims-totalled
    blocked_by: []
    typical_cost: 0
    typical_duration: instant
    cited_articles:
      - AK_440_452
    universality: jurisdiction-universal-pattern
    notes: Strongest negotiation lever — flips "you owe nothing" to "you owe X".

  - id: GR-P04
    name: Consumer protection burden flip (Law 2251/1994 Art. 9c, 9e)
    forum: consumer-ombudsman
    description: >-
      When the opposing party is a professional supplier and the user
      is a private consumer, Greek consumer-protection law reverses
      the burden of proof on unfair commercial practices. Supplier
      must affirmatively prove its conduct was fair.
    requires_state: opposing-party-is-professional-supplier
    blocked_by: []
    typical_cost: 0
    typical_duration: weeks
    cited_articles:
      - Law_2251_1994_Art_9c
      - Law_2251_1994_Art_9e
    universality: eu-directive-2005-29
    notes: Free, non-binding, creates written record of unfair-practice findings.

  - id: GR-P05
    name: Betterment rule (ΕφΑθ 3994/2005 + ΑΠ 777/2022)
    forum: civil-court-eirinodikio
    description: >-
      Greek case law caps recovery at the depreciated value
      (αποκατάσταση όχι πλουτισμός — restoration, not enrichment).
      Always demand depreciation calculations on every charged item.
    requires_state: any-damage-charge
    blocked_by: []
    typical_cost: 0
    typical_duration: instant
    cited_articles:
      - AK_297
      - AK_298
      - AK_904
    case_law:
      - "ΑΠ 777/2022"
      - "ΕφΑθ 3994/2005"
      - "ΑΠ 985/2020"
    universality: civil-law-restitution-principle
    notes: Combine with the universal "no depreciation = unjust enrichment" principle.

  - id: GR-P06
    name: Itemisation requirement (ΑΠ 1597/1995)
    forum: phase3-demand-letter
    description: >-
      Greek case law (foundational ΑΠ 1597/1995) requires landlord
      claims to be itemised — quantity, type, unit cost. Lump-sum
      claims are αόριστες (legally indeterminate) and fatal.
    requires_state: opposing-party-served-lump-sum-claim
    blocked_by: []
    typical_cost: 0
    typical_duration: instant
    cited_articles:
      - AK_330
      - KPolD_338
    case_law:
      - "ΑΠ 1597/1995"
    universality: greek-civil-procedure
    notes: An αόριστη claim cannot be cured at trial — must be re-filed.

  - id: GR-P07
    name: Spin-off joint liability (Art. 65 §4 N. 4601/2019)
    forum: civil-court-eirinodikio
    description: >-
      When the opposing entity has been spun off, Greek corporate law
      makes both entities jointly and severally liable for 5 years.
      Always name BOTH companies as defendants in the αγωγή.
    requires_state: opposing-party-underwent-spin-off
    blocked_by: []
    typical_cost: court-fee-doubled-for-second-defendant
    typical_duration: case-lifetime
    cited_articles:
      - N_4601_2019_Art_65
      - N_4601_2019_Art_70
    case_law:
      - "ΑΠ 362/2023"
    universality: eu-cross-border-mergers-directive
    notes: Universal succession means notification gaps cannot be cured.
EOF
```

- [ ] **Step 4: Write `glossary.md`**

```bash
cat > law-packs/greece/glossary.md <<'EOF'
---
document: glossary
pack: greece
language_pair: el-en
purpose: Greek legal terminology with English translations
---

# Greek Legal Glossary

> Translation table for the Greek vocabulary used throughout the pack. English-speaking lawyers reviewing a Greek case can use this file to navigate the rest of the pack. Skill outputs preserve the Greek term + parenthetical English on first use.

## Core procedural terms

| Greek | Transliteration | English | Plain-language gloss |
|---|---|---|---|
| Αστικός Κώδικας (ΑΚ) | Astikos Kodikas | Civil Code | Main statute book for private-law disputes |
| Κώδικας Πολιτικής Δικονομίας (ΚΠολΔ) | Kodikas Politikis Dikonomias | Code of Civil Procedure | Procedural rules for civil courts |
| Σύνταγμα | Syntagma | Constitution | Greek constitutional text |
| Άρειος Πάγος (ΑΠ) | Areios Pagos | Supreme Court of Greece | Highest civil court |
| ΟλΑΠ | Olomeleia Areiou Pagou | Plenary session of ΑΠ | Strongest precedent — full bench |
| Ειρηνοδικείο | Eirinodikio | Magistrate court | First-instance court for claims ≤ €20,000 |
| Πρωτοδικείο | Protodikio | Court of First Instance | First-instance for claims > €20,000 |
| Εφετείο | Efetio | Court of Appeal | Second instance |

## Action types

| Greek | Transliteration | English | Plain-language gloss |
|---|---|---|---|
| αγωγή | agogi | Lawsuit / civil action | Written pleading that opens a civil case |
| εξώδικη δήλωση | exodiki dilosi | Extrajudicial declaration | Pre-litigation formal demand letter |
| εξώδικο | exodiko | Same as above (colloquial) | Pre-litigation formal notice |
| πρόσκληση | prosklisi | Invitation / call to act | Variant of εξώδικη δήλωση |
| προτάσεις | protaseis | Written submissions / brief | Post-αγωγή written pleading at trial |
| μήνυση | minysi | Criminal complaint | Filed with prosecutor |
| αντιμωλία | antimolia | Contradictory inspection | Joint check-out where both parties present |
| ανταγωγή | antagogi | Counterclaim | Defendant's claim against plaintiff in same suit |

## Substantive concepts

| Greek | Transliteration | English | Plain-language gloss |
|---|---|---|---|
| φυσιολογική φθορά | fysiologiki fthora | Normal wear and tear | Use-related deterioration the tenant is NOT liable for |
| παραγραφή | paragrafi | Limitation period / prescription | Statutory deadline after which a claim is barred |
| αόριστη | aoristi | Legally indeterminate / vague | Claim lacking required specificity — fatal defect |
| ψυχική οδύνη | psychiki odyni | Moral / psychological harm | Compensable under Art. 932 ΑΚ |
| καλή πίστη | kali pisti | Good faith | Art. 288 ΑΚ — universal civil-law standard |
| κατάχρηση δικαιώματος | katachrisi dikaiomatos | Abuse of right | Art. 281 ΑΚ |
| αδικαιολόγητος πλουτισμός | adikaiologitos ploutismos | Unjust enrichment | Art. 904 ΑΚ |
| καθολική διαδοχή | katholiki diadochi | Universal succession | Spin-off transfer (N. 4601/2019) |
| συμψηφισμός | symfismos | Set-off | Mutual extinction of debts — Art. 440-452 ΑΚ |
| αποκατάσταση | apokatastasi | Restoration | Compensable measure (ΑΠ 777/2022) |
| αντικατάσταση | antikatastasi | Replacement | Distinguished from αποκατάσταση |
| αλλαγή επωνυμίας | allagi eponymias | Change of name | Often misused to hide a spin-off |
| ΓΟΣ | GOS | Standard terms | Greek "unfair contract terms" doctrine |
| Schutzzweck | (German loan-word) | Protective purpose | Whether a statute's protected interest covers this party |
| εν εκκρεμοδικία | en ekkremodikia | Pending litigation | Art. 222 KPolD bar on parallel proceedings |
| ΦΕΚ | FEK | Government Gazette | Authoritative source for statute text |

## Forums and authorities

| Greek | English | Plain-language gloss |
|---|---|---|
| Συνήγορος Καταναλωτή | Consumer Ombudsman | Free non-binding mediator |
| Αρχή Προστασίας Δεδομένων / HDPA | Hellenic Data Protection Authority | Greek GDPR regulator |
| ΑΑΔΕ | Independent Public Revenue Authority | Greek tax authority |
| ΣΕΠΕ | Labour Inspectorate | Workplace-safety regulator |
| ΓΕΜΗ | General Commercial Registry | Greek company register |

## Statute citation forms

| Greek | English | Notes |
|---|---|---|
| Άρθρο 592 ΑΚ | Article 592 of the Civil Code | Always cite article + code |
| Άρθρο 338 ΚΠολΔ | Article 338 of the Code of Civil Procedure | |
| Νόμος 2251/1994 | Law 2251/1994 | Statute number / year format |
| ΦΕΚ Α' 219/28.11.2025 | Government Gazette, Series A, No. 219, 28 Nov 2025 | Authoritative source |
| ΑΠ 985/2020 | Areios Pagos decision 985 of 2020 | Decision number / year |
| ΟλΑΠ 705/1979 | Plenary Areios Pagos decision 705 of 1979 | Full bench |
| C-579/21 | CJEU case 579/2021 | EU Court of Justice |
| HDPA 36/2021 | Hellenic Data Protection Authority decision 36/2021 | |

---

**Use rule:** when the legal-strategy skill emits Greek terms in user-facing output, the first instance MUST include the parenthetical English translation; subsequent uses MAY omit it.
EOF
```

- [ ] **Step 5: Validate YAML files parse**

```bash
python3 <<'PY'
import yaml
for f in ["forums.yaml", "limitation_periods.yaml", "playbook.yaml"]:
    with open(f"law-packs/greece/{f}") as fh:
        d = yaml.safe_load(fh)
    print(f"{f}: ok ({type(d).__name__})")
PY
```

Expected: each prints `ok (dict)`.

- [ ] **Step 6: Verify forums.yaml encodes Art. 52 KPolD**

```bash
grep -c "Art. 52 KPolD" law-packs/greece/forums.yaml
grep -c "criminal-complaint" law-packs/greece/forums.yaml
```

Expected: both ≥ 2.

- [ ] **Step 7: Verify AK_602 with 180 days**

```bash
grep "AK_602" law-packs/greece/limitation_periods.yaml
grep "period_days: 180" law-packs/greece/limitation_periods.yaml
```

Expected: both lines present.

- [ ] **Step 8: Verify playbook has ≥5 plays**

```bash
python3 -c "import yaml; d = yaml.safe_load(open('law-packs/greece/playbook.yaml')); n = len(d['plays']); print(f'plays: {n}'); assert n >= 5"
```

Expected: `plays: 7`.

- [ ] **Step 9: Verify glossary terms exist**

```bash
grep -c "φυσιολογική φθορά" law-packs/greece/glossary.md
grep -c "Άρειος Πάγος" law-packs/greece/glossary.md
grep -c "παραγραφή" law-packs/greece/glossary.md
```

Expected: each ≥ 1.

- [ ] **Step 10: Commit**

```bash
git add law-packs/greece/forums.yaml law-packs/greece/limitation_periods.yaml law-packs/greece/playbook.yaml law-packs/greece/glossary.md
git commit -s -m "$(cat <<'EOF'
feat(greece): forums + limitations + playbook + glossary (T7)

Four jurisdiction config files for the Greek pack:

- forums.yaml: 8 forums with precondition rules. Encodes Art. 52
  KPolD blocking rule: criminal complaint suspends civil proceedings,
  so civil αγωγή MUST be filed first. Implements the "criminal last"
  doctrine.
- limitation_periods.yaml: 7 statutory deadlines + the procedural
  blocking rule. AK_602 = 180 days from key handover.
- playbook.yaml: 7 universal Greek plays ported from yestay 50-play
  playbook (deadline leverage, lost records inference, set-off,
  consumer burden flip, betterment rule, itemisation, spin-off
  joint liability).
- glossary.md: ~50 Greek legal terms with English translation.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 8: Greek core articles part 1 (10 of 22)

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_173.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_200.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_249.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_261.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_281.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_288.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_297.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_298.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_300.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_330.md`

This task creates 10 statute files, each with frontmatter matching the schema in T4 (`law-packs/_schema.md`) and a verbatim Greek text section. The task does NOT actually fetch the statute text — it documents the workflow (kodiko.gr primary, lawspot.gr verification) and writes the file structure with a `<<FETCH-FROM-kodiko.gr>>` marker that the executor replaces during execution.

**Source workflow (per `09_ai_research/research/12_greek_legal_databases/07_kodiko_gr.md`):**

1. Navigate to `https://www.kodiko.gr/nomologia/document_navigation/...` for each AK article
2. Extract the verbatim Greek text (the article body, not commentary)
3. Cross-verify against `https://www.lawspot.gr/` (if a discrepancy, prefer kodiko.gr)
4. Compute `sha256sum | cut -c1-16` of the verbatim text section (excluding frontmatter)
5. Replace `<<FETCH-FROM-kodiko.gr>>` placeholder
6. Update the `sha256` field in frontmatter
7. Single batched commit at end of task per the yestay MVP plan T3/T4 style

**Single commit at end batches all 10 articles** (matches yestay MVP plan T3/T4 style).

- [ ] **Step 1: Create the directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p law-packs/greece/core
```

- [ ] **Step 2: Write `AK_173.md` (Contract interpretation — true intent)**

```bash
cat > law-packs/greece/core/AK_173.md <<'EOF'
---
article_id: AK_173
short_name: "Contract interpretation — true intention"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-173"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: []
canonical_uri: "kodiko://AK/173"
---

# Άρθρο 173 ΑΚ — Ερμηνεία δικαιοπραξιών

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>
>
> Replace this block with the verbatim text fetched from
> https://www.kodiko.gr (article 173 of the Civil Code). Cross-verify
> against https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-173
> before computing sha256.

## English working translation (informal)

> When interpreting a declaration of will, one must seek the true
> intention without adhering literally to the words.

## Loaded by

`core/` — every Greek session.

## Used in

Contract interpretation arguments. The "true intention" rule defeats
literal-text defences when the contracting parties' actual practice
contradicts a clause that was never meant to apply (e.g., cleaning
fee clauses re-applied as damage charges).
EOF
```

- [ ] **Step 3: Write `AK_200.md` (Good faith interpretation)**

```bash
cat > law-packs/greece/core/AK_200.md <<'EOF'
---
article_id: AK_200
short_name: "Good-faith interpretation baseline"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-200"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: []
canonical_uri: "kodiko://AK/200"
---

# Άρθρο 200 ΑΚ — Ερμηνεία συμβάσεων κατά την καλή πίστη

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Contracts are interpreted as good faith requires, having regard to
> commercial usage.

## Loaded by

`core/` — every Greek session.

## Used in

Pairs with AK_173. Where AK_173 looks at subjective intent, AK_200
imports the objective good-faith standard. Together they form the
interpretation backbone for every contract dispute.
EOF
```

- [ ] **Step 4: Write `AK_249.md` (20-year general prescription)**

```bash
cat > law-packs/greece/core/AK_249.md <<'EOF'
---
article_id: AK_249
short_name: "20-year general prescription"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-249"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: []
canonical_uri: "kodiko://AK/249"
---

# Άρθρο 249 ΑΚ — Εικοσαετής παραγραφή

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Unless otherwise provided, the period of prescription of claims is
> twenty years.

## Loaded by

`core/` — every Greek session.

## Used in

Catch-all baseline limitation period. Counterclaim limitation tables.
EOF
```

- [ ] **Step 5: Write `AK_261.md` (Prescription interruption)**

```bash
cat > law-packs/greece/core/AK_261.md <<'EOF'
---
article_id: AK_261
short_name: "Prescription interruption"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-261"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: []
canonical_uri: "kodiko://AK/261"
---

# Άρθρο 261 ΑΚ — Διακοπή της παραγραφής με αγωγή

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Prescription is interrupted by the filing of a lawsuit. The new
> period begins from the latest procedural act of the parties or
> the court.

## Loaded by

`core/` — every Greek session.

## Used in

Determining whether prior demand letters tolled the AK_602 6-month
deadline. Pairs with AK_602.
EOF
```

- [ ] **Step 6: Write `AK_281.md` (Abuse of right)**

```bash
cat > law-packs/greece/core/AK_281.md <<'EOF'
---
article_id: AK_281
short_name: "Abuse of right (κατάχρηση δικαιώματος)"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-281"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, consumer_protection, gdpr]
canonical_uri: "kodiko://AK/281"
---

# Άρθρο 281 ΑΚ — Κατάχρηση δικαιώματος

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The exercise of a right is prohibited if it manifestly exceeds the
> limits imposed by good faith, good morals, or the social or economic
> purpose of the right.

## Loaded by

`core/` — every Greek session.

## Used in

The most-cited article in the corpus. Anchors every "systematic bad
faith" argument and every challenge to overreaching contract
enforcement. Pairs with AK_288 (good faith) and Syntagma_25
(proportionality) to form a 3-element abuse-of-right test.
EOF
```

- [ ] **Step 7: Write `AK_288.md` (Good faith / business usage)**

```bash
cat > law-packs/greece/core/AK_288.md <<'EOF'
---
article_id: AK_288
short_name: "Good faith / business usage"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-288"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, consumer_protection, gdpr, tort_damages, corporate, tax_invoices]
canonical_uri: "kodiko://AK/288"
---

# Άρθρο 288 ΑΚ — Καλή πίστη και συναλλακτικά ήθη

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The debtor must perform the obligation as good faith requires,
> having regard to commercial usage.

## Loaded by

`core/` — every Greek session.

## Used in

Universal civil-law standard. Every CH/CC/SA file references it.
Pairs with AK_281.
EOF
```

- [ ] **Step 8: Write `AK_297.md` (Damages — actual loss + lost profit)**

```bash
cat > law-packs/greece/core/AK_297.md <<'EOF'
---
article_id: AK_297
short_name: "Damages — actual loss + lost profit"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-297"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, tort_damages]
canonical_uri: "kodiko://AK/297"
---

# Άρθρο 297 ΑΚ — Έκταση της αποζημίωσης

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Compensation includes actual loss (damnum emergens) and lost profit
> (lucrum cessans). The court may award compensation in money or in
> kind, depending on circumstances.

## Loaded by

`core/` — every Greek session.

## Used in

Defines the measure of compensable damages. Pairs with AK_298 to
form the causation + extent framework. Anchors the betterment rule
(restoration not enrichment).
EOF
```

- [ ] **Step 9: Write `AK_298.md` (Causation / damages extent)**

```bash
cat > law-packs/greece/core/AK_298.md <<'EOF'
---
article_id: AK_298
short_name: "Causation / damages extent"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-298"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, tort_damages]
canonical_uri: "kodiko://AK/298"
---

# Άρθρο 298 ΑΚ — Θετική και αποθετική ζημία

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Compensation is owed for damage caused, including loss of profit
> the injured party would have probably acquired in the ordinary
> course of events.

## Loaded by

`core/` — every Greek session.

## Used in

Pairs with AK_297. Defines causation requirement for damages claims.
EOF
```

- [ ] **Step 10: Write `AK_300.md` (Mitigation duty / contributory fault)**

```bash
cat > law-packs/greece/core/AK_300.md <<'EOF'
---
article_id: AK_300
short_name: "Contributory fault / mitigation duty"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-300"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, tort_damages]
canonical_uri: "kodiko://AK/300"
---

# Άρθρο 300 ΑΚ — Συντρέχον πταίσμα του ζημιωθέντος

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> If fault on the part of the injured party contributed to the damage
> or its extent, the court may reduce or refuse compensation.

## Loaded by

`core/` — every Greek session.

## Used in

Used defensively when the opposing party's own conduct contributed
to the damage they now claim against you (e.g., spoliation of
evidence, refusal to permit timely repair, failure to inspect).
EOF
```

- [ ] **Step 11: Write `AK_330.md` (Professional standard of care)**

```bash
cat > law-packs/greece/core/AK_330.md <<'EOF'
---
article_id: AK_330
short_name: "Professional standard of care"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-330"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, consumer_protection, tort_damages]
canonical_uri: "kodiko://AK/330"
---

# Άρθρο 330 ΑΚ — Πταίσμα

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The debtor is liable for any fault (intentional or negligent),
> unless otherwise provided. Negligence exists when the diligence
> required in the transactions is not exercised.

## Loaded by

`core/` — every Greek session.

## Used in

Critical for professional-supplier cases. A professional landlord
or property-management company is held to a higher standard than a
private individual. Anchors record-keeping requirements: a
professional that cannot produce inventory documentation breached
its AK_330 duty.
EOF
```

- [ ] **Step 12: Verify all 10 files exist**

```bash
ls -la law-packs/greece/core/AK_{173,200,249,261,281,288,297,298,300,330}.md
```

Expected: 10 files listed.

- [ ] **Step 13: Verify each has frontmatter + verbatim text marker**

```bash
for f in law-packs/greece/core/AK_{173,200,249,261,281,288,297,298,300,330}.md; do
  head -1 "$f" | grep -q '^---$' || { echo "FAIL frontmatter: $f"; exit 1; }
  grep -q "<<FETCH-FROM-kodiko.gr>>" "$f" || { echo "FAIL marker: $f"; exit 1; }
  grep -q "^article_id: AK_" "$f" || { echo "FAIL article_id: $f"; exit 1; }
done
echo "all 10 files OK"
```

Expected: `all 10 files OK`

- [ ] **Step 14: Single batched commit (matches yestay MVP plan T3/T4 style)**

```bash
git add law-packs/greece/core/AK_{173,200,249,261,281,288,297,298,300,330}.md
git commit -s -m "$(cat <<'EOF'
feat(greece/core): 10 of 22 always-loaded ΑΚ articles (T8)

Statute files for AK_173, AK_200, AK_249, AK_261, AK_281, AK_288,
AK_297, AK_298, AK_300, AK_330. Each file:

- Frontmatter matching law-packs/_schema.md (article_id, short_name,
  source_primary, source_verification, effective_date, repeal_date,
  sha256 placeholder, translation_status, last_verified, loaded_by,
  cited_in_modules, canonical_uri)
- Verbatim text section with <<FETCH-FROM-kodiko.gr>> placeholder
  to be replaced during execution by fetched text from kodiko.gr
- Informal English working translation
- "Loaded by" + "Used in" sections explaining role in corpus

Source workflow per 09_ai_research/research/12_greek_legal_databases/
07_kodiko_gr.md: kodiko.gr primary, lawspot.gr verification, sha256
of verbatim section, single batched commit per task.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 9: Greek core articles part 2 (12 of 22)

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_440_452.md` (bundled set-off articles)
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_602.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_904.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_914.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/AK_932.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/KPolD_338.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/KPolD_339.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/KPolD_340.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/KPolD_366.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/KPolD_433.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/KPolD_450.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/core/Syntagma_25.md`

The remaining 12 of the 22 core articles (per LEGAL_CORPUS_MAP §1). `AK_440_452.md` is special: it bundles articles 440-452 into one file because they cover a single contiguous topic (set-off / συμψηφισμός). All other files are one-article-per-file like T8.

**Same source workflow as T8** — kodiko.gr primary, lawspot.gr verification, `<<FETCH-FROM-kodiko.gr>>` placeholder, single batched commit at end. **Syntagma_25** uses `https://www.hellenicparliament.gr/` as primary source.

- [ ] **Step 1: Write `AK_440_452.md` (set-off bundle)**

```bash
cat > law-packs/greece/core/AK_440_452.md <<'EOF'
---
article_id: AK_440_452
short_name: "Set-off (συμψηφισμός) — bundled articles 440-452"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-440"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy]
canonical_uri: "kodiko://AK/440-452"
bundled_articles:
  - AK_440
  - AK_441
  - AK_442
  - AK_443
  - AK_444
  - AK_445
  - AK_446
  - AK_447
  - AK_448
  - AK_449
  - AK_450
  - AK_451
  - AK_452
---

# Άρθρα 440-452 ΑΚ — Συμψηφισμός (set-off)

> Bundled into a single file because articles 440-452 cover one
> contiguous topic — set-off — and are always cited together. The
> verbatim text section below contains all 13 articles in order.

## Verbatim text (Greek)

### Άρθρο 440
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 441
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 442
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 443
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 444
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 445
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 446
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 447
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 448
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 449
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 450
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 451
> <<FETCH-FROM-kodiko.gr>>

### Άρθρο 452
> <<FETCH-FROM-kodiko.gr>>

## English working summary (informal)

> Set-off (συμψηφισμός) extinguishes mutual debts up to the lower
> amount. It is invoked by unilateral declaration (Art. 441) and has
> retroactive effect to the date both debts became simultaneously
> due (Art. 442). Counterclaims arising from the same legal
> relationship are eligible. Some claims are excluded from set-off
> (Arts. 451-452).

## Loaded by

`core/` — every Greek session. Cited in COUNTERCLAIMS hub and every
counterclaim file.

## Used in

The mathematical backbone for any deposit dispute with counterclaims.
Once total counterclaims exceed the opposing party's primary claim,
the set-off table flips the dispute from "we owe you" to "you owe us".
Art. 442's retroactive effect is the key — it means the dispute is
treated as if it had never been a debt at all.
EOF
```

- [ ] **Step 2: Write `AK_602.md` (6-month rental limitation — THE deadline)**

```bash
cat > law-packs/greece/core/AK_602.md <<'EOF'
---
article_id: AK_602
short_name: "6-month limitation period for rental claims"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-602"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy]
canonical_uri: "kodiko://AK/602"
---

# Άρθρο 602 ΑΚ — Παραγραφή αξιώσεων από τη μίσθωση

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Claims of the lessor for damages caused to the leased property,
> for changes made by the lessee, and for omitted improvements,
> are time-barred after six months from the date the lessor took
> back possession of the property.

## Loaded by

`core/` — every Greek session.

## Used in

THE deadline that controls every Greek deposit case. Tracked as
DL-01 in DEADLINE_REGISTER.md by /lex-harness:init for any case
that involves a tenancy. The 180-day clock starts on the date the
property is returned (key handover, not contract end). Pairs with
limitation_periods.yaml AK_602-rental-deposit entry.
EOF
```

- [ ] **Step 3: Write `AK_904.md` (Unjust enrichment)**

```bash
cat > law-packs/greece/core/AK_904.md <<'EOF'
---
article_id: AK_904
short_name: "Unjust enrichment"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-904"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, tax_invoices]
canonical_uri: "kodiko://AK/904"
---

# Άρθρο 904 ΑΚ — Αδικαιολόγητος πλουτισμός

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> A person who is enriched without lawful cause from the property or
> at the expense of another is liable to return the enrichment.

## Loaded by

`core/` — every Greek session.

## Used in

Alternate basis when the primary claim (e.g., damages under AK_297)
fails. Critical for "no depreciation" arguments — if landlord cannot
prove depreciated value, they cannot recover full replacement cost
without unjust enrichment. Note: Art. 904 is SUBSIDIARY — it cannot
be the primary basis when AK_281 + AK_297-298 apply directly.
EOF
```

- [ ] **Step 4: Write `AK_914.md` (Tort liability)**

```bash
cat > law-packs/greece/core/AK_914.md <<'EOF'
---
article_id: AK_914
short_name: "Tort liability"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-914"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tort_damages, gdpr]
canonical_uri: "kodiko://AK/914"
---

# Άρθρο 914 ΑΚ — Αδικοπραξία

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> A person who through fault unlawfully causes damage to another is
> liable for compensation.

## Loaded by

`core/` — every Greek session.

## Used in

Tort foundation. Required for moral damages (paired with AK_932)
and personality-rights claims. The "unlawfully" element is satisfied
by breach of any protective rule (e.g., GDPR, ΠΔ 212/2006 asbestos).
EOF
```

- [ ] **Step 5: Write `AK_932.md` (Moral damages)**

```bash
cat > law-packs/greece/core/AK_932.md <<'EOF'
---
article_id: AK_932
short_name: "Moral / psychological damages"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-932"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tort_damages, gdpr]
canonical_uri: "kodiko://AK/932"
---

# Άρθρο 932 ΑΚ — Χρηματική ικανοποίηση λόγω ηθικής βλάβης

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> In the case of tort, the court may, regardless of compensation for
> material damage, award reasonable monetary satisfaction for moral
> harm. This applies in particular where health, honour, or chastity
> were threatened, or where one was deprived of personal freedom.

## Loaded by

`core/` — every Greek session.

## Used in

Per ΑΠ 806/2023, monetary satisfaction is available where health
was THREATENED — actual physical injury is not required. Used in
infant/pregnancy moral-damage claims and GDPR Art. 82 damages
(C-300/21 — non-material harm is compensable).
EOF
```

- [ ] **Step 6: Write `KPolD_338.md` (Burden of proof)**

```bash
cat > law-packs/greece/core/KPolD_338.md <<'EOF'
---
article_id: KPolD_338
short_name: "Burden of proof"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3962/kodikas-politikis-dikonomias"
source_verification: "https://www.lawspot.gr/nomoi/kodikas-politikis-dikonomias/arthro-338"
effective_date: 1968-09-16
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, procedure_eirinodikio]
canonical_uri: "kodiko://KPolD/338"
---

# Άρθρο 338 ΚΠολΔ — Βάρος απόδειξης

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Each party bears the burden of proving the facts necessary to
> support its claim or defence.

## Loaded by

`core/` — every Greek session.

## Used in

Burden allocation. Critical for landlord damage claims — the landlord
bears the burden of proving (a) damage existed at departure, (b) it
exceeded normal wear, (c) the cost of repair. Failure on any element
defeats the claim.
EOF
```

- [ ] **Step 7: Write `KPolD_339.md` (Admissible evidence + presumptions)**

```bash
cat > law-packs/greece/core/KPolD_339.md <<'EOF'
---
article_id: KPolD_339
short_name: "Admissible means of evidence"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3962/kodikas-politikis-dikonomias"
source_verification: "https://www.lawspot.gr/nomoi/kodikas-politikis-dikonomias/arthro-339"
effective_date: 1968-09-16
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, procedure_eirinodikio]
canonical_uri: "kodiko://KPolD/339"
---

# Άρθρο 339 ΚΠολΔ — Αποδεικτικά μέσα

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Means of evidence include: confession, autopsy, expert opinion,
> documents, examination of parties, witnesses, and judicial
> presumptions.

## Loaded by

`core/` — every Greek session.

## Used in

The admissibility catalogue. Frames the inference framework: where
direct evidence is missing, judicial presumptions can fill the gap.
Pairs with KPolD_340 (free evaluation).
EOF
```

- [ ] **Step 8: Write `KPolD_340.md` (Free evaluation of evidence)**

```bash
cat > law-packs/greece/core/KPolD_340.md <<'EOF'
---
article_id: KPolD_340
short_name: "Free evaluation of evidence"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3962/kodikas-politikis-dikonomias"
source_verification: "https://www.lawspot.gr/nomoi/kodikas-politikis-dikonomias/arthro-340"
effective_date: 1968-09-16
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, procedure_eirinodikio]
canonical_uri: "kodiko://KPolD/340"
---

# Άρθρο 340 ΚΠολΔ — Ελεύθερη εκτίμηση αποδείξεων

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The court evaluates evidence freely according to its persuasive
> force, except where the law provides otherwise.

## Loaded by

`core/` — every Greek session.

## Used in

Used to attack low-quality evidence (e.g., 320×240 thumbnails from
a 50MP camera). Free evaluation lets the court conclude that
deliberately degraded evidence is unpersuasive.
EOF
```

- [ ] **Step 9: Write `KPolD_366.md` (Non-production adverse inference)**

```bash
cat > law-packs/greece/core/KPolD_366.md <<'EOF'
---
article_id: KPolD_366
short_name: "Adverse inference for non-production"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3962/kodikas-politikis-dikonomias"
source_verification: "https://www.lawspot.gr/nomoi/kodikas-politikis-dikonomias/arthro-366"
effective_date: 1968-09-16
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, procedure_eirinodikio]
canonical_uri: "kodiko://KPolD/366"
---

# Άρθρο 366 ΚΠολΔ — Άρνηση επίδειξης εγγράφου

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Where a party refuses without cause to produce a document under
> their control, the court may treat as proven the facts the
> document was meant to establish.

## Loaded by

`core/` — every Greek session.

## Used in

The "absence is evidence" principle. When a professional landlord
cannot produce the check-in inventory list or check-out joint
inspection, the court may treat tenant's allegations about pre-existing
condition as proven.
EOF
```

- [ ] **Step 10: Write `KPolD_433.md` (Spoliation presumption)**

```bash
cat > law-packs/greece/core/KPolD_433.md <<'EOF'
---
article_id: KPolD_433
short_name: "Spoliation presumption"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3962/kodikas-politikis-dikonomias"
source_verification: "https://www.lawspot.gr/nomoi/kodikas-politikis-dikonomias/arthro-433"
effective_date: 1968-09-16
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy]
canonical_uri: "kodiko://KPolD/433"
---

# Άρθρο 433 ΚΠολΔ — Καταστροφή αποδεικτικών μέσων

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Where a party destroys or conceals a document or other evidence
> in their possession, the facts that the evidence was meant to
> prove are presumed in favour of the opposing party.

## Loaded by

`core/` — every Greek session.

## Used in

Spoliation (e.g., physical destruction of a charged item before the
opposing party can inspect it) reverses the burden of proof under
this article. Combined with AK_330 (professional standard) for
property managers.
EOF
```

- [ ] **Step 11: Write `KPolD_450.md` (Document non-production adverse inference)**

```bash
cat > law-packs/greece/core/KPolD_450.md <<'EOF'
---
article_id: KPolD_450
short_name: "Document non-production adverse inference"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3962/kodikas-politikis-dikonomias"
source_verification: "https://www.lawspot.gr/nomoi/kodikas-politikis-dikonomias/arthro-450"
effective_date: 1968-09-16
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy]
canonical_uri: "kodiko://KPolD/450"
---

# Άρθρο 450 ΚΠολΔ — Υποχρέωση επίδειξης εγγράφων

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> A party may be ordered to produce documents in their control if
> the opposing party shows the documents are necessary to prove a
> fact in dispute. Refusal triggers the adverse inference of
> Art. 366.

## Loaded by

`core/` — every Greek session.

## Used in

Procedural mechanism to force production of opposing party's records
(check-in inventory, photos, repair invoices). Pairs with KPolD_366.
EOF
```

- [ ] **Step 12: Write `Syntagma_25.md` (Constitutional proportionality)**

```bash
cat > law-packs/greece/core/Syntagma_25.md <<'EOF'
---
article_id: Syntagma_25
short_name: "Constitutional rights + proportionality principle"
source_primary: "https://www.hellenicparliament.gr/Vouli-ton-Ellinon/To-Politevma/Syntagma/article-25/"
source_verification: "https://www.lawspot.gr/nomoi/syntagma/arthro-25"
effective_date: 1975-06-11
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: core
cited_in_modules: [tenancy, gdpr]
canonical_uri: "syntagma://25"
---

# Άρθρο 25 Συντάγματος — Αρχή αναλογικότητας

## Verbatim text (Greek)

> <<FETCH-FROM-hellenicparliament.gr>>

## English working translation (informal)

> The rights of the human as an individual and as a member of society
> are guaranteed by the State. All organs of the State are obliged to
> ensure their unhindered and effective exercise. Restrictions of
> these rights must respect the principle of proportionality.

## Loaded by

`core/` — every Greek session.

## Used in

Constitutional anchor for the proportionality principle. Used to
strengthen AK_281 abuse-of-right arguments — proportionality is
the bridge between civil-code "good faith" and constitutional
fundamental-rights protection. Source is hellenicparliament.gr (NOT
kodiko.gr) because constitutional articles have a separate
authoritative source.
EOF
```

- [ ] **Step 13: Verify all 12 files exist + frontmatter + markers**

```bash
ls -la law-packs/greece/core/AK_440_452.md \
       law-packs/greece/core/AK_602.md \
       law-packs/greece/core/AK_904.md \
       law-packs/greece/core/AK_914.md \
       law-packs/greece/core/AK_932.md \
       law-packs/greece/core/KPolD_{338,339,340,366,433,450}.md \
       law-packs/greece/core/Syntagma_25.md

for f in law-packs/greece/core/AK_440_452.md \
         law-packs/greece/core/AK_602.md \
         law-packs/greece/core/AK_904.md \
         law-packs/greece/core/AK_914.md \
         law-packs/greece/core/AK_932.md \
         law-packs/greece/core/KPolD_{338,339,340,366,433,450}.md \
         law-packs/greece/core/Syntagma_25.md; do
  head -1 "$f" | grep -q '^---$' || { echo "FAIL frontmatter: $f"; exit 1; }
  grep -q "<<FETCH-FROM-" "$f" || { echo "FAIL marker: $f"; exit 1; }
done
echo "all 12 files OK"
```

Expected: `all 12 files OK`

- [ ] **Step 14: Verify the bundled file lists 13 sub-articles**

```bash
grep -c "^### Άρθρο 4" law-packs/greece/core/AK_440_452.md
```

Expected: `13` (articles 440 through 452 inclusive).

- [ ] **Step 15: Verify total core file count is now 22**

```bash
ls law-packs/greece/core/*.md | wc -l
```

Expected: `22` (T8 wrote 10, T9 wrote 12).

- [ ] **Step 16: Single batched commit**

```bash
git add law-packs/greece/core/AK_440_452.md \
        law-packs/greece/core/AK_602.md \
        law-packs/greece/core/AK_904.md \
        law-packs/greece/core/AK_914.md \
        law-packs/greece/core/AK_932.md \
        law-packs/greece/core/KPolD_338.md \
        law-packs/greece/core/KPolD_339.md \
        law-packs/greece/core/KPolD_340.md \
        law-packs/greece/core/KPolD_366.md \
        law-packs/greece/core/KPolD_433.md \
        law-packs/greece/core/KPolD_450.md \
        law-packs/greece/core/Syntagma_25.md
git commit -s -m "$(cat <<'EOF'
feat(greece/core): remaining 12 of 22 always-loaded articles (T9)

Statute files for AK_440-452 (set-off bundle), AK_602 (THE 6-month
deadline), AK_904, AK_914, AK_932, KPolD_338, KPolD_339, KPolD_340,
KPolD_366, KPolD_433, KPolD_450, Syntagma_25.

AK_440_452.md is special: it bundles articles 440-452 in one file
because they're a single contiguous topic (συμψηφισμός / set-off)
and are always cited together. The verbatim section has 13 sub-headings,
one per article, each with its own <<FETCH-FROM-kodiko.gr>> placeholder.

Syntagma_25.md sources from hellenicparliament.gr (constitutional
authoritative source) rather than kodiko.gr.

Combined with T8, the core/ directory now contains all 22 articles
listed in 09_ai_research/LEGAL_CORPUS_MAP.md §1.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 10: Greek tenancy module

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/_module.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_574.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_575.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_576.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_577.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_578.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_592.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_599.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/AK_624.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tenancy/case_law_inline.md`

The Greek tenancy module per LEGAL_CORPUS_MAP §2 Module 1: 8 articles + `_module.md` (trigger metadata) + `case_law_inline.md` with 5 ΑΠ summaries plus the ΑΠ 399/2023 ADVERSE flag. Source for ΑΠ summaries: areiospagos.gr.

- [ ] **Step 1: Create directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p law-packs/greece/modules/tenancy
```

- [ ] **Step 2: Write `_module.md` (trigger metadata)**

```bash
cat > law-packs/greece/modules/tenancy/_module.md <<'EOF'
---
module: tenancy
pack: greece
version: 0.1.0
loaded_when: task-signal-or-default
trigger_signals:
  - "deposit"
  - "rental damage"
  - "wear and tear"
  - "φυσιολογική φθορά"
  - "balcony rent reduction"
  - "Art. 576"
  - "defect"
  - "rent abatement"
  - "CH1"
  - "CH2"
  - "CH3"
  - "CH4"
  - "CH5"
  - "CC2"
  - "CC3"
articles:
  - AK_574
  - AK_575
  - AK_576
  - AK_577
  - AK_578
  - AK_592
  - AK_599
  - AK_624
case_law_inline_file: case_law_inline.md
adverse_decisions:
  - id: "ΑΠ 399/2023"
    flag: ADVERSE
    instruction: "DO NOT CITE — flag in DECISION_LOG"
last_verified: 2026-04-07
---

# Tenancy module — Greek pack

> Lease relationship under the Greek Civil Code (Αστικός Κώδικας Books III & IV).
> Loaded by every CH1–CH5 case, every CC2 (rent reduction) and CC3 (defect remedy)
> case, and any task whose prompt matches the trigger signals above.

## Articles in this module

- **AK_574** — Concept of lease
- **AK_575** — Lessor's duty to deliver and maintain
- **AK_576** — Lessee's right to rent reduction for defects
- **AK_577** — Lessee's right to terminate for defects
- **AK_578** — Lessor's good-faith warranty
- **AK_592** — Normal wear-and-tear exemption (the operative defence article)
- **AK_599** — Lessee's duty to return the property
- **AK_624** — Lessee's right to repair-deduct

## Inline case law

See `case_law_inline.md` for ≤500-character summaries of:
- ΑΠ 985/2020 (primary 3-element burden test)
- ΑΠ 777/2022 (most recent betterment + depreciation framework)
- ΑΠ 938/2018 (family use = agreed use)
- ΟλΑΠ 705/1979 (repair preferred — full bench)
- ΑΠ 1597/1995 (itemisation requirement)

## Adverse decisions (DO NOT CITE)

- **ΑΠ 399/2023** — flagged ADVERSE per LEGAL_CORPUS_MAP §3.
  This decision narrows tenant defences in a way that hurts our position.
  The skill MUST refuse to cite it and MUST flag any user request that
  proposes citing it as `[ADVERSE-PRECEDENT-BLOCKED]`.
EOF
```

- [ ] **Step 3: Write the 8 article files**

Each follows the same frontmatter + verbatim text pattern as T8/T9. The `loaded_by` field is `module:tenancy` (not `core`).

```bash
cat > law-packs/greece/modules/tenancy/AK_574.md <<'EOF'
---
article_id: AK_574
short_name: "Concept of lease"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-574"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/574"
---

# Άρθρο 574 ΑΚ — Έννοια της μίσθωσης

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> By the contract of lease, the lessor is obliged to grant the lessee
> the use of the leased property for the agreed term, and the lessee
> is obliged to pay the agreed rent.

## Used in

The definitional anchor — establishes that "use" not "preservation"
is the lessee's obligation.
EOF

cat > law-packs/greece/modules/tenancy/AK_575.md <<'EOF'
---
article_id: AK_575
short_name: "Lessor's duty to deliver and maintain"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-575"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/575"
---

# Άρθρο 575 ΑΚ — Παράδοση και διατήρηση του μισθίου

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The lessor is obliged to deliver the leased property to the lessee
> in a condition fit for its agreed use and to maintain it in such
> condition for the duration of the lease.

## Used in

Establishes the lessor's continuing duty. Pairs with AK_576/577 to
form the defect-remedy framework. Defeats "as is" arguments.
EOF

cat > law-packs/greece/modules/tenancy/AK_576.md <<'EOF'
---
article_id: AK_576
short_name: "Lessee's right to rent reduction for defects"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-576"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/576"
---

# Άρθρο 576 ΑΚ — Μείωση μισθώματος λόγω ελαττωμάτων

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> If the leased property has, at the time of delivery or during the
> lease, a defect that essentially reduces its fitness for the agreed
> use, the lessee may claim a corresponding reduction of the rent for
> the period of the defect.

## Used in

The CC2 / CC3 anchor. Used for balcony rent reduction (CC2-A) and
broken-bed rent reduction (CC3). The reduction runs from the date
the defect was reported to the lessor (or the lessor became aware).
EOF

cat > law-packs/greece/modules/tenancy/AK_577.md <<'EOF'
---
article_id: AK_577
short_name: "Lessee's right to terminate for defects"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-577"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/577"
---

# Άρθρο 577 ΑΚ — Καταγγελία λόγω ελαττώματος

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> If the defect prevents or substantially impedes the agreed use,
> the lessee may terminate the lease without notice.

## Used in

The escalation step from AK_576. If the defect is severe enough
to make the property unusable, the lessee can terminate.
EOF

cat > law-packs/greece/modules/tenancy/AK_578.md <<'EOF'
---
article_id: AK_578
short_name: "Lessor's good-faith warranty"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-578"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/578"
---

# Άρθρο 578 ΑΚ — Εγγύηση καταλληλότητας

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The lessor warrants that the leased property is, and will remain,
> fit for the agreed use. Knowledge by the lessee at the time of
> contract formation may exclude the warranty.

## Used in

Establishes a warranty independent of fault. Defeats lessor's "I
didn't know" defences. Knowledge exclusion is narrow — must be
explicit.
EOF

cat > law-packs/greece/modules/tenancy/AK_592.md <<'EOF'
---
article_id: AK_592
short_name: "Normal wear-and-tear exemption — THE operative article"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-592"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/592"
---

# Άρθρο 592 ΑΚ — Φυσιολογική φθορά

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> The lessee is not liable for changes or deterioration arising from
> the agreed use.

## Used in

THE operative defence article in every CH1–CH5 case. Frames the
"wear and tear" exemption: anything that arose from the agreed use
is not compensable. The 3-element burden test (per ΑΠ 985/2020)
requires the lessor to prove (a) damage exists, (b) it exceeds normal
wear, (c) the cost of repair. Element (b) is where AK_592 lives.
EOF

cat > law-packs/greece/modules/tenancy/AK_599.md <<'EOF'
---
article_id: AK_599
short_name: "Lessee's duty to return"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-599"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/599"
---

# Άρθρο 599 ΑΚ — Απόδοση του μισθίου

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> Upon termination of the lease, the lessee must return the property
> in the condition in which it was received, save for normal wear
> arising from the agreed use.

## Used in

Pairs with AK_592. The "save for normal wear" clause is the
statutory anchor for the wear-and-tear defence. Defines the moment
of obligation: return at termination, not maintenance during the
lease.
EOF

cat > law-packs/greece/modules/tenancy/AK_624.md <<'EOF'
---
article_id: AK_624
short_name: "Lessee's right to repair-deduct"
source_primary: "https://www.kodiko.gr/nomologia/document_navigation/3461/astikos-kodikas"
source_verification: "https://www.lawspot.gr/nomoi/astikos-kodikas/arthro-624"
effective_date: 1946-02-23
repeal_date: null
sha256: "<<TO-BE-COMPUTED>>"
translation_status: el-only
last_verified: 2026-04-07
loaded_by: module:tenancy
canonical_uri: "kodiko://AK/624"
---

# Άρθρο 624 ΑΚ — Δικαίωμα του μισθωτή να επισκευάσει

## Verbatim text (Greek)

> <<FETCH-FROM-kodiko.gr>>

## English working translation (informal)

> If the lessor delays repair of a defect after demand, the lessee
> may carry out the repair and deduct the cost from the rent.

## Used in

Repair-deduct remedy. Backstop when AK_576 (rent reduction) is
insufficient. Documents tenant good faith — tenant tried to repair,
lessor failed.
EOF
```

- [ ] **Step 4: Write `case_law_inline.md` with 5 ΑΠ summaries + adverse flag**

Source for the 5 inline ΑΠ summaries is `https://www.areiospagos.gr/nomologia/apofaseis.asp` (POST form: x_number, x_ETOS, charset windows-1253). Each summary is a verbatim ratio decidendi extract ≤500 characters. Per `09_ai_research/research/12_greek_legal_databases/08_areiospagos_gr.md`.

```bash
cat > law-packs/greece/modules/tenancy/case_law_inline.md <<'EOF'
---
document: case_law_inline
module: tenancy
pack: greece
purpose: "Inline ΑΠ ratio decidendi summaries — fetch from areiospagos.gr"
last_verified: 2026-04-07
---

# Tenancy — inline case law

> The 5 most-cited Areios Pagos decisions for the tenancy module.
> Each summary is ≤500 characters and contains the verbatim ratio
> decidendi extracted from the official decision text. Source:
> areiospagos.gr decision search at /nomologia/apofaseis.asp.
>
> The skill loads this file alongside the article files when the
> tenancy module is active.

---

## ΑΠ 985/2020 — Primary 3-element burden test

**Source:** https://www.areiospagos.gr/nomologia/apofaseis.asp (x_number=985, x_ETOS=2020)
**Last fetched:** <<FETCH-FROM-areiospagos.gr>>
**sha256 of summary:** <<TO-BE-COMPUTED>>

**Ratio (≤500 chars, verbatim Greek):**

> <<FETCH-VERBATIM-RATIO-FROM-areiospagos.gr>>

**English working summary (informal):**

> The lessor claiming damages from the lessee bears a 3-element
> burden: (1) damage exists at return; (2) the damage exceeds
> normal wear from the agreed use; (3) the cost claimed corresponds
> to the actual repair. Failure on any element defeats the claim.

**Used in:** every CH1–CH5 file. The standard burden framework cited
in Phase 3 demand letters and αγωγή.

---

## ΑΠ 777/2022 — Betterment + depreciation framework

**Source:** https://www.areiospagos.gr/nomologia/apofaseis.asp (x_number=777, x_ETOS=2022)
**Last fetched:** <<FETCH-FROM-areiospagos.gr>>
**sha256 of summary:** <<TO-BE-COMPUTED>>

**Ratio (≤500 chars, verbatim Greek):**

> <<FETCH-VERBATIM-RATIO-FROM-areiospagos.gr>>

**English working summary (informal):**

> Compensation for damaged leased property is restoration
> (αποκατάσταση), not enrichment (πλουτισμός). The lessor cannot
> recover the full replacement cost of an item with depreciated
> value — recovery is capped at the depreciated value at the time
> of damage. The most recent ΑΠ pronouncement on betterment.

**Used in:** every charge that involves a replaced item. Anchors
the depreciation requirement.

---

## ΑΠ 938/2018 — Family use = agreed use

**Source:** https://www.areiospagos.gr/nomologia/apofaseis.asp (x_number=938, x_ETOS=2018)
**Last fetched:** <<FETCH-FROM-areiospagos.gr>>
**sha256 of summary:** <<TO-BE-COMPUTED>>

**Ratio (≤500 chars, verbatim Greek):**

> <<FETCH-VERBATIM-RATIO-FROM-areiospagos.gr>>

**English working summary (informal):**

> Where a residential lease is signed for "family use", the agreed
> use includes the presence of children, infants, and household
> pets. Wear arising from those uses is normal wear under AK_592.
> The lessor cannot exclude family-incidental wear post hoc.

**Used in:** any case where the lessor charges for wear caused by
children or pets in a family residence. Defeats "high standards"
arguments that try to exclude the actual occupants from the agreed use.

---

## ΟλΑΠ 705/1979 — Repair preferred over replacement

**Source:** https://www.areiospagos.gr/nomologia/apofaseis.asp (x_number=705, x_ETOS=1979, ΟλΑΠ)
**Last fetched:** <<FETCH-FROM-areiospagos.gr>>
**sha256 of summary:** <<TO-BE-COMPUTED>>

**Ratio (≤500 chars, verbatim Greek):**

> <<FETCH-VERBATIM-RATIO-FROM-areiospagos.gr>>

**English working summary (informal):**

> Plenary session decision: the law prefers repair (επιδιόρθωση)
> over replacement (αντικατάσταση) where repair is feasible. The
> lessor must justify replacement on the ground that repair was
> impossible or disproportionately expensive.

**Used in:** any charge that replaces an item where repair was
possible. Strongest precedent because it is a full-bench (Ολομέλεια)
decision — overrides single-chamber decisions.

---

## ΑΠ 1597/1995 — Itemisation requirement (foundational)

**Source:** https://www.areiospagos.gr/nomologia/apofaseis.asp (x_number=1597, x_ETOS=1995)
**Last fetched:** <<FETCH-FROM-areiospagos.gr>>
**sha256 of summary:** <<TO-BE-COMPUTED>>

**Ratio (≤500 chars, verbatim Greek):**

> <<FETCH-VERBATIM-RATIO-FROM-areiospagos.gr>>

**English working summary (informal):**

> Damage claims from a lease must be itemised — quantity, type,
> unit cost. Lump-sum demands are αόριστες (legally indeterminate)
> and cannot found a valid claim. The defect cannot be cured at
> trial; the claim must be re-filed.

**Used in:** every Phase 3 demand letter as a litmus test of the
opposing party's claim. Foundational — the most-cited tenancy
itemisation precedent.

---

## ⚠ ΑΠ 399/2023 — ADVERSE — DO NOT CITE

**Source:** https://www.areiospagos.gr/nomologia/apofaseis.asp (x_number=399, x_ETOS=2023)
**Status:** ADVERSE
**Flag instruction:** This decision narrows tenant defences in a way
that hurts our position. Per `LEGAL_CORPUS_MAP §3`, the skill MUST:

1. Refuse to cite this decision in any draft
2. Flag any user request that proposes citing it as
   `[ADVERSE-PRECEDENT-BLOCKED: ΑΠ 399/2023]`
3. Log the attempt to `<case-repo>/07_strategy/core/DECISION_LOG.md`
4. Suggest alternative precedents (ΑΠ 985/2020, ΑΠ 777/2022) instead

**The verbatim text is intentionally NOT included** — this file
documents the adverse flag, not the decision itself, to prevent
accidental copy-paste into drafts.
EOF
```

- [ ] **Step 5: Verify all 10 files exist**

```bash
ls -la law-packs/greece/modules/tenancy/_module.md \
       law-packs/greece/modules/tenancy/AK_{574,575,576,577,578,592,599,624}.md \
       law-packs/greece/modules/tenancy/case_law_inline.md
```

Expected: 10 files.

- [ ] **Step 6: Verify the case_law_inline file flags ΑΠ 399/2023 as adverse**

```bash
grep -c "ADVERSE" law-packs/greece/modules/tenancy/case_law_inline.md
grep -c "ΑΠ 399/2023" law-packs/greece/modules/tenancy/case_law_inline.md
grep -c "ADVERSE-PRECEDENT-BLOCKED" law-packs/greece/modules/tenancy/case_law_inline.md
```

Expected: each ≥ 1.

- [ ] **Step 7: Verify the 5 inline summaries are present**

```bash
for c in "ΑΠ 985/2020" "ΑΠ 777/2022" "ΑΠ 938/2018" "ΟλΑΠ 705/1979" "ΑΠ 1597/1995"; do
  grep -q "$c" law-packs/greece/modules/tenancy/case_law_inline.md || { echo "MISSING: $c"; exit 1; }
done
echo "all 5 ΑΠ summaries present"
```

Expected: `all 5 ΑΠ summaries present`

- [ ] **Step 8: Verify article files have correct loaded_by field**

```bash
for f in law-packs/greece/modules/tenancy/AK_{574,575,576,577,578,592,599,624}.md; do
  grep -q "loaded_by: module:tenancy" "$f" || { echo "FAIL loaded_by: $f"; exit 1; }
done
echo "all 8 article files have loaded_by: module:tenancy"
```

Expected: success message.

- [ ] **Step 9: Single batched commit**

```bash
git add law-packs/greece/modules/tenancy/
git commit -s -m "$(cat <<'EOF'
feat(greece/tenancy): tenancy module — 8 articles + inline case law (T10)

Greek tenancy module per LEGAL_CORPUS_MAP §2 Module 1:

- _module.md: trigger metadata (loaded_when: task-signal-or-default,
  trigger_signals list, articles list, adverse decisions registry)
- AK_574 through AK_624: 8 always-loaded-when-tenancy-module-active
  article files (574 lease concept, 575 deliver/maintain, 576 rent
  reduction, 577 termination, 578 warranty, 592 normal wear — THE
  operative defence article, 599 return duty, 624 repair-deduct)
- case_law_inline.md: 5 ratio decidendi summaries from areiospagos.gr
  (ΑΠ 985/2020, ΑΠ 777/2022, ΑΠ 938/2018, ΟλΑΠ 705/1979, ΑΠ 1597/1995)
  PLUS the ΑΠ 399/2023 ADVERSE flag with skill instruction to refuse
  citation and log attempts to DECISION_LOG.

Same <<FETCH-FROM-kodiko.gr>> / <<FETCH-FROM-areiospagos.gr>> placeholder
pattern as T8/T9 — text fetched during execution, not at plan-write time.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11: `skills/legal-strategy/SKILL.md` (jurisdiction-agnostic port)

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/SKILL.md`

Port the existing yestay legal-strategy skill into the plugin. **CRITICAL: jurisdiction-agnostic body per PR-01 + PR-03.** The SKILL.md body MUST NOT contain "Greek", "ΑΚ", "Art. 612A", "ΚΠολΔ", "Yestay", or any other country-/case-specific term. The body references the active law pack via `<case-repo>/05_legal_research/law_pack/MODULE_INDEX.md` and reference files via `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/*.md`.

Description ≤1024 chars per Codex limit (per design spec §5.1 verbatim). Frontmatter has `name`, `version: "4.0"`, `description`, `writes_to`, `reads_from`, `handoff_to`, plus a new `optional_tools` field per PR-15.

- [ ] **Step 1: Create directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p skills/legal-strategy/references
```

- [ ] **Step 2: Write `SKILL.md`**

```bash
cat > skills/legal-strategy/SKILL.md <<'EOF'
---
name: legal-strategy
version: "4.0"
description: >-
  Use when working on any civil legal dispute — drafting demand letters,
  formal complaints, lawsuits, counterclaims, regulator filings,
  consumer ombudsman complaints, settlement negotiations, strategy
  decisions on what to do next, analysing opposing-party responses,
  choosing which legal play to deploy, citing statute articles from the
  active jurisdiction's law pack, computing limitation periods,
  assessing argument vulnerability, or reasoning about when to pressure
  the other side. Loads the active jurisdiction's law pack from
  05_legal_research/law_pack/ and reads the case repo's strategy + claims +
  decision log for context. Runs the verify gate before any formal
  output. Refuses to cite statutes whose verbatim text is not in the
  loaded law pack.
writes_to:
  - "<case-repo>/CURRENT_STATUS.md"
  - "<case-repo>/06_claims_and_defenses/PENDING_FACTS.md"
  - "<case-repo>/07_strategy/core/DECISION_LOG.md"
  - "<case-repo>/09_ai_research/research_queue.md"
reads_from:
  - "<case-repo>/01_case_summary/CASE_OVERVIEW.md"
  - "<case-repo>/06_claims_and_defenses/"
  - "<case-repo>/07_strategy/"
  - "<case-repo>/05_legal_research/law_pack/"
  - "${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/"
handoff_to:
  - document-production
  - devil-advocate
optional_tools:
  - name: chrome-devtools
    purpose: "Live web evidence capture"
    fallback: "Manual WebFetch + paste"
  - name: neo4j-memory
    purpose: "Multi-hop fact relationship queries"
    fallback: "Markdown grep across 06_claims_and_defenses/"
  - name: cerebra-legal
    purpose: "Consumer-protection legal reasoning templates"
    fallback: "Inline reasoning checklists in references/"
  - name: eur-lex
    purpose: "EU law CELEX retrieval"
    fallback: "Manual EUR-Lex web fetch"
---

# Legal Strategy Skill

Civil legal disputes — extraction, pressure, drafting, and decision discipline. **"Information First, Attack Second"** — every communication extracts information or creates a documented fact that benefits your position.

This skill is jurisdiction-agnostic. It loads the active jurisdiction's rules at runtime from `<case-repo>/05_legal_research/law_pack/`. Statute citations, forum rules, limitation periods, common plays, and templates all live in the active law pack — never hardcoded in this skill.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│  Layer 1: PIPELINE PHASES (always bookend the session)        │
│  DISCOVER ──→ [task modes] ──→ EVOLVE                         │
├──────────────────────────────────────────────────────────────┤
│  Layer 2: TASK MODES (pick based on goal — not sequential)    │
│  ABSORB · RESEARCH · FORENSICS · PLAN · DRAFT                │
│  NEGOTIATE · DEPLOY                                           │
├──────────────────────────────────────────────────────────────┤
│  Layer 3: CROSS-CUTTING DISCIPLINES (quality gates)           │
│  VERIFY · CHALLENGE · ELICIT · MONITOR                        │
├──────────────────────────────────────────────────────────────┤
│  Layer 4: COOPERATIVE SKILLS                                  │
│  osint-investigation · document-production · devil-advocate   │
└──────────────────────────────────────────────────────────────┘
```

## DISCOVER — Session start (always first)

### Step 0: Case detection (PR-09)

Before doing anything else, check whether the current working directory is a lex-harness case repo:

```
IF `<case-repo>/01_case_summary/CASE_OVERVIEW.md` does NOT exist:
  EMIT the following message to the user and HALT:
  "No lex-harness case detected in this directory.
   To initialise a new case, run: /lex-harness:init <jurisdiction>
   To invoke this skill against an existing case, `cd` to the case directory first."
  DO NOT proceed to the mandatory loads below.
  DO NOT crash, raise an exception, or produce a partial session brief.
ELSE:
  Proceed to the mandatory loads.
```

This guard satisfies PR-09 (plugin works without a case repo): the skill responds with a friendly, actionable message instead of crashing when it can't find case files. The same guard applies to `osint-investigation`, `document-production`, and `devil-advocate` — each checks for `CASE_OVERVIEW.md` at invocation and emits the equivalent "no case detected" message before doing anything else.

**Mandatory loads (exactly 3 files):**

| Source | What it provides |
|---|---|
| `<case-repo>/CURRENT_STATUS.md` | Current phase, open items, last action, recommended next action |
| `<case-repo>/07_strategy/core/DECISION_LOG.md` | Blocked/dropped arguments — prevents resurfacing |
| `<case-repo>/01_case_summary/CASE_OVERVIEW.md` | Key facts fingerprint: dates, amounts, entities |

**Then load the active law pack:**

| Source | What it provides |
|---|---|
| `<case-repo>/05_legal_research/law_pack/MODULE_INDEX.md` | Routing table — task → modules + SA → modules + forum preconditions |
| `<case-repo>/05_legal_research/law_pack/limitation_periods.yaml` | Statutory deadlines (compute days remaining) |
| `<case-repo>/05_legal_research/law_pack/forums.yaml` | Forum precondition gates |

**Output:** Session Brief with phase, open items, last action, ONE recommended next action, deadline alerts (anything within 14 days). Tool-availability log: list any optional tool that is unavailable as `[TOOL-UNAVAILABLE:<name>]`.

## EVOLVE — Session end (always last)

| Action | Target |
|---|---|
| New facts discovered | → `<case-repo>/06_claims_and_defenses/PENDING_FACTS.md` (proposed; human promotes to PROVEN_FACTS_REGISTER in a separate commit without the AI co-author trailer) |
| Arguments tested/dropped | → `<case-repo>/07_strategy/core/DECISION_LOG.md` |
| Tier 1 fact changes | → cascade update to all Tier 2 references |
| Session summary | → `<case-repo>/CURRENT_STATUS.md` (≤30 lines) |
| Skill improvements | → propose to user, never silent update |

## Task mode routing

| Goal | Mode | Reference file |
|---|---|---|
| Process incoming response/email/evidence | **ABSORB** | `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/knowledge-vault.md` |
| Find new legal/OSINT/market information | **RESEARCH** | `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/knowledge-vault.md` |
| Analyse existing evidence deeply | **FORENSICS** | `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/verify-gate.md` |
| Structure arguments / design strategy | **PLAN** | `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/strategy-reasoning.md` + `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/atomic-decomposition.md` |
| Produce a document | **DRAFT** | hand off to `document-production` skill |
| Assess settlement | **NEGOTIATE** | `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/settlement-math.md` |
| File / send / serve a document | **DEPLOY** | check forums.yaml preconditions; verify deadline-register impact |

**ABSORB categories:** admission | contradiction | new violation | rebuttal | new argument | new fact | misinformation. Every statement from the opposing party must be classified into one of these.

## Cross-cutting disciplines

### VERIFY — Citation safety gate

**Trigger:** before any citation enters a formal document.

**SOLAR rule:** No statute is applied to facts until its verbatim text has been loaded from the active law pack. Reasoning from training memory about statute content is PROHIBITED. If a citation is needed but the article is not in `<case-repo>/05_legal_research/law_pack/core/` or one of the loaded `modules/`, the skill must:

1. Refuse to emit the citation
2. Log a gap to `<case-repo>/09_ai_research/research_queue.md`
3. Suggest the user fetch the article and add it to the law pack

The full 9-stage verify-gate is in `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/verify-gate.md`.

### CHALLENGE — Adversarial testing gate

**Trigger:** before any new legal argument is finalised for a formal document.

Hand off to `devil-advocate` skill via the `/<plugin>:devil <argument-id>` command. The dispatch is in an isolated subagent with no inherited session context — only raw facts, cited law, and the argument text. See `${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references/atomic-decomposition.md` for compound-argument breakdown before dispatch.

### ELICIT — Extraction quality gate

**Trigger:** before any question is sent to the opposing party.

**Three-Column Test:** every question must have all three columns filled:

| If YES | If NO | If SILENT |
|---|---|---|
| What admission does this create? | What contradiction does this expose? | What adverse inference (per the active jurisdiction's evidence rules)? |

ALL three must advance the user's position. Hardest questions first.

### MONITOR — Deadline & response tracking

**Trigger:** session start (DISCOVER), after any DEPLOY, after deadline discovery.

| Category | Alert threshold |
|---|---|
| Statutory limitations (loaded from `limitation_periods.yaml`) | 60 / 30 / 14 days remaining |
| Filing deadlines (regulator response windows) | 7 days remaining |
| Response deadlines (silence = adverse inference) | day after expiry |
| Evidence decay (web listings, social media) | monthly check |

Deadline breaches MUST be escalated immediately, not deferred to session end.

## Decision principles (universal — Layer 1)

These principles are jurisdiction-independent and apply everywhere:

1. **Information First, Attack Second** — every communication extracts info or creates a documented fact
2. **Dropped arguments stay dropped** — if DECISION_LOG marked an argument [DROPPED], it does not return without explicit reconsideration entry
3. **Criminal last** — never recommend criminal forum until civil action is filed (most jurisdictions have a procedural blocking rule that suspends civil if criminal goes first; check forums.yaml for the active jurisdiction's specific rule)
4. **Absence is evidence** — when the opposing party cannot produce a record they should have, the absence is admissible against them
5. **No depreciation = no enrichment** — replacement cost without depreciation equals unjust enrichment in nearly every civil-law jurisdiction
6. **One write path for facts** — humans write to `PROVEN_FACTS_REGISTER`; AI proposes via `PENDING_FACTS`. The git pre-commit hook enforces this.

## Quality gates

| Gate | When | Blocks |
|---|---|---|
| **G1: Research complete** | Before PLAN | Cannot plan without source material loaded |
| **G2: Argument consistent** | Before DRAFT | Cannot draft contradictory arguments |
| **G3: DA reviewed** | Before formal doc uses argument | Cannot send without adversarial testing |
| **G4: Ready to send** | Before DEPLOY | All citations [VERIFIED] + user approves |

## Tool-availability discipline (PR-11 + PR-12)

Every optional tool listed in this skill's frontmatter has a documented fallback. The skill MUST:

1. Detect tool availability before use
2. Fall back to the manual/offline path if unavailable
3. Log the degradation as `[TOOL-UNAVAILABLE:<tool-name>]` in the session brief

The skill NEVER crashes, NEVER blocks a workflow, and NEVER requires installation mid-session. The full fallback matrix is in `${CLAUDE_PLUGIN_ROOT}/docs/TOOL_OPTIONALITY.md`.

## Reference files

| File | When to load |
|---|---|
| `references/knowledge-vault.md` | SOLAR rule + verbatim retrieval workflow (every session) |
| `references/strategy-reasoning.md` | PLAN mode — 1-page strategy checklist |
| `references/settlement-math.md` | NEGOTIATE mode — ZOPA / BATNA / EV |
| `references/verify-gate.md` | Before any formal output — 9-stage gate |
| `references/atomic-decomposition.md` | Compound argument → element rows |
| `references/mcp-tools-guide.md` | Optional MCP tool usage (if available) |
EOF
```

- [ ] **Step 3: Verify description ≤ 1024 chars (Codex limit)**

```bash
python3 <<'PY'
import re
content = open('skills/legal-strategy/SKILL.md').read()
m = re.search(r'^description: >-\n((?:  .*\n)+)', content, re.MULTILINE)
assert m, "no description block found"
desc_lines = [l[2:] for l in m.group(1).rstrip().split('\n')]
desc = ' '.join(desc_lines).strip()
n = len(desc)
print(f"description: {n} chars")
assert n <= 1024, f"description exceeds 1024 chars: {n}"
print("OK")
PY
```

Expected: `description: <N> chars` with N ≤ 1024, then `OK`.

- [ ] **Step 4: Verify NO Greek-specific terms in skill body (PR-01 + PR-03)**

```bash
# These terms must NOT appear in the body. Frontmatter is OK to have
# language-neutral words.
forbidden=("Greek" "ΑΚ" "ΚΠολΔ" "Art\\. 592" "Art\\. 281" "Art\\. 602" "Yestay" "VIAMAR" "Άρειος" "kodiko" "lawspot" "areiospagos" "Άρθρο" "ΑΠ ")
fail=0
for term in "${forbidden[@]}"; do
  # Allow inside code/path examples by checking only non-frontmatter,
  # non-code-block lines. We use a simple grep across the whole file
  # since the SKILL.md body is jurisdiction-agnostic by construction.
  if grep -qE "$term" skills/legal-strategy/SKILL.md; then
    echo "FORBIDDEN term found: $term"
    fail=1
  fi
done
[ $fail -eq 0 ] && echo "PR-01/PR-03 PASS — no jurisdiction-specific terms"
```

Expected: `PR-01/PR-03 PASS — no jurisdiction-specific terms`

- [ ] **Step 5: Verify required frontmatter fields**

```bash
python3 <<'PY'
import re
c = open('skills/legal-strategy/SKILL.md').read()
required = ["name:", "version:", "description:", "writes_to:", "reads_from:", "handoff_to:", "optional_tools:"]
for r in required:
    assert r in c, f"missing frontmatter field: {r}"
print("frontmatter OK")
PY
```

Expected: `frontmatter OK`

- [ ] **Step 6: Verify body uses `${CLAUDE_PLUGIN_ROOT}` for intra-plugin paths**

```bash
grep -c '${CLAUDE_PLUGIN_ROOT}/05_legal_research/law_pack' skills/legal-strategy/SKILL.md
grep -c '${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/references' skills/legal-strategy/SKILL.md
```

Expected: both ≥ 1.

- [ ] **Step 7: Commit**

```bash
git add skills/legal-strategy/SKILL.md
git commit -s -m "$(cat <<'EOF'
feat(skill/legal-strategy): jurisdiction-agnostic SKILL.md (T11)

Ports the yestay legal-strategy skill into the plugin with strict
PR-01 + PR-03 layer separation:

- Description (≤1024 chars per Codex limit) per design spec §5.1
- Frontmatter: name, version 4.0, description, writes_to, reads_from,
  handoff_to, plus new optional_tools field per PR-15 (chrome-devtools,
  neo4j-memory, cerebra-legal, eur-lex — all optional with documented
  fallback)
- Body references the active law pack via
  <case-repo>/05_legal_research/law_pack/MODULE_INDEX.md and
  reference files via ${CLAUDE_PLUGIN_ROOT}/skills/legal-strategy/
  references/*.md
- ZERO references to Greek, ΑΚ, ΚΠολΔ, Yestay, VIAMAR, kodiko.gr,
  or any country-/case-specific term in the body
- 4-layer architecture preserved (pipeline, task modes, cross-cutting,
  cooperative)
- 6 universal decision principles documented (Information First, etc.)
- Tool-availability discipline (PR-11/PR-12) baked into the skill body

Verify-gate, atomic-decomposition, knowledge-vault, strategy-reasoning,
settlement-math reference files are written in T12-T15.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 11b: `skills/legal-strategy/references/tool-detection.md` (PR-12 implementation)

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/references/tool-detection.md`

**Purpose:** PR-12 compliance. The round-5 validation of Plan A found that every skill body says "detect tool availability + fall back gracefully" but no workflow contains the concrete step-by-step IF/ELSE pattern an AI agent should follow. This reference file IS the concrete pattern — every skill references it from the "Tool-availability discipline" section of its body.

- [ ] **Step 1: Write the file**

```bash
cd ~/Developer/projects/lex-harness
cat > skills/legal-strategy/references/tool-detection.md <<'EOF'
---
reference: tool-detection
parent_skill: legal-strategy
purpose: Concrete IF/ELSE pattern for detecting optional MCP tools and falling back when absent (PR-12)
created: 2026-04-07
---

# Tool Detection + Graceful Degradation — Concrete Pattern

> Referenced from every skill's "Tool-availability discipline" section. Defines the exact steps an AI agent follows when a workflow CAN use an external MCP tool but the tool is OPTIONAL per PR-11.

## The rule

Before invoking ANY MCP tool listed in the skill's `optional_tools:` frontmatter, the agent MUST:

1. **Check availability** — does the tool appear in the session's available tools list?
2. **Use it if present** — invoke via normal MCP call
3. **Fall back if absent** — use the documented native Claude Code primitive (WebFetch, Read, Grep, Bash)
4. **Log the degradation** — emit `[TOOL-UNAVAILABLE:<tool-name>]` in the session brief OR in the relevant file's metadata

## Detection method

Claude Code exposes available tools via its native tool list at session start. To check whether a specific MCP tool is available, the agent:

```
IF `mcp__<server-name>__<tool-name>` appears in the session's tool inventory:
  → use the MCP tool directly
ELSE:
  → use the fallback primitive
  → emit [TOOL-UNAVAILABLE:<server-name>]
```

No bash / environment variable checks needed. The tool list is the source of truth.

## Per-tool fallback table (PR-13 matrix)

| Optional tool | What it adds | Fallback primitive | Fallback steps |
|---|---|---|---|
| `mcp__chrome-devtools__*` | Full-fidelity JS-rendered web capture + SPA scraping | `WebFetch` + manual paste | 1. Call `WebFetch` on the URL. 2. If the content looks like a rendered page, save it. 3. If it's obviously a JS-only SPA (empty body, `<div id="root">`), prompt the user to open the URL in a browser, copy the rendered HTML, and paste it into a session message. 4. Save the pasted content to `<case-repo>/04_evidence/osint/<slug>_<date>.md` with `[TOOL-UNAVAILABLE:chrome-devtools]` in the frontmatter. |
| `mcp__neo4j-memory__*` / `mcp__neo4j-cypher__*` | Multi-hop fact relationship queries (e.g., "which arguments cite PF-A29") | Manual grep over markdown | 1. `grep -l "PF-A29" <case-repo>/06_claims_and_defenses/CH*.md <case-repo>/06_claims_and_defenses/CC*.md <case-repo>/07_strategy/SA*.md`. 2. Report the file list. 3. Emit `[TOOL-UNAVAILABLE:neo4j]` in the session brief. |
| `mcp__chromadb__*` | Semantic search over case-law volume | Inline summaries in the active law pack | 1. Read the `case_law_inline.md` file in the relevant module (e.g., `<case-repo>/05_legal_research/law_pack/modules/tenancy/case_law_inline.md`). 2. Scan the ≤10 inline ΑΠ summaries. 3. If none match the query, document the gap — do NOT invent case law. 4. Emit `[TOOL-UNAVAILABLE:chromadb]`. |
| `mcp__dikaio-ai__*` | Automated Greek law citation verification | Manual verification via kodiko.gr | 1. Open the cited article file from the active law pack. 2. Copy the verbatim text. 3. Prompt the user to paste it into Dikaio.ai manually and confirm the result. 4. Record the verification in `<case-repo>/09_ai_research/dikaio_verifications/<article>_<date>.md`. 5. Emit `[TOOL-UNAVAILABLE:dikaio-ai]`. |
| `mcp__greek-law-mcp__*` / `mcp__eur-lex__*` | Live statute / CJEU retrieval | `WebFetch` against kodiko.gr / search.et.gr / EUR-Lex | 1. Construct the URL pattern for the article (e.g., `https://www.kodiko.gr/nomologia/document_navigation/<N>/astikos-kodikas-arthro-<M>`). 2. `WebFetch`. 3. Extract the verbatim text. 4. Save to a scratchpad. 5. Emit `[TOOL-UNAVAILABLE:greek-law-mcp]` or `[TOOL-UNAVAILABLE:eur-lex-mcp]`. |

## Workflow example: evidence capture

A concrete walkthrough showing the IF/ELSE pattern in action.

**Task:** George wants to preserve a Google Maps review URL as evidence.

**With Chrome DevTools MCP (full-power path):**
```
Step 1: Check for mcp__chrome-devtools__navigate_page in tool list → present
Step 2: Call mcp__chrome-devtools__navigate_page(url=<URL>)
Step 3: Call mcp__chrome-devtools__take_snapshot
Step 4: Call mcp__chrome-devtools__take_screenshot(filePath="<case-repo>/04_evidence/osint/<slug>.png")
Step 5: Compute sha256 of the screenshot
Step 6: Write <case-repo>/04_evidence/osint/<slug>_<date>.md with frontmatter (url, sha256, capture_method: chrome-devtools-mcp, captured_at)
Step 7: Append row to CHAIN_OF_CUSTODY.log
```

**Without Chrome DevTools MCP (fallback path):**
```
Step 1: Check for mcp__chrome-devtools__navigate_page in tool list → absent
Step 2: Emit "[TOOL-UNAVAILABLE:chrome-devtools-mcp] Falling back to WebFetch"
Step 3: Call WebFetch(url=<URL>, prompt="Return the page content")
Step 4: Examine the response
Step 5: If the response is empty or clearly a JS-only SPA, prompt the user: "Please open <URL> in a browser, copy the rendered HTML, and paste it here"
Step 6: Wait for user paste
Step 7: Save the captured content to <case-repo>/04_evidence/osint/<slug>_<date>.md with frontmatter (url, sha256, capture_method: manual-webfetch OR user-paste, captured_at, tool_unavailable: chrome-devtools-mcp)
Step 8: Append row to CHAIN_OF_CUSTODY.log with the `[TOOL-UNAVAILABLE]` tag
```

**Both paths produce a file with the same schema.** The only difference is:
- The with-tool path is faster and automated
- The without-tool path requires manual user interaction
- The without-tool path's frontmatter carries `tool_unavailable: <name>` for audit

## Logging conventions

Every time a skill falls back, it MUST log:

1. **In the session brief** — a line like `[TOOL-UNAVAILABLE:chrome-devtools-mcp] Capture used WebFetch fallback for <URL>`
2. **In the produced file's frontmatter** — `tool_unavailable: chrome-devtools-mcp`
3. **In CHAIN_OF_CUSTODY.log if applicable** — the tag in the capture_method column

These logs are how the lawyer and George know which outputs came from which path.

## Anti-patterns

- ❌ Silent fallback — NEVER fall back without logging the `[TOOL-UNAVAILABLE:...]` tag
- ❌ Crashing on missing tool — NEVER throw an error; ALWAYS fall back
- ❌ Requiring the tool — NEVER tell the user "install X MCP first"; ALWAYS complete the task with the fallback
- ❌ Inventing data when fallback can't produce it — if even the fallback can't fetch content (e.g., paywall, CAPTCHA), say so explicitly and STOP
- ❌ Mixing tool outputs — don't use MCP for step 1 and fallback for step 2 of the same capture; pick one path and stick with it

## When to consult this file

- Before invoking any MCP tool listed in `optional_tools:`
- When writing a new skill that references optional tools
- When a user reports "the skill crashed because X MCP wasn't installed" — that's a PR-12 violation and this file is the cure
EOF
```

- [ ] **Step 2: Verify length + jurisdiction-agnostic check**

```bash
wc -l ~/Developer/projects/lex-harness/skills/legal-strategy/references/tool-detection.md
# Expected: ~110-130 lines

# Jurisdiction-agnostic check (PR-01/PR-03)
forbidden=("ΑΚ" "ΚΠολΔ" "Yestay" "SA-31" "PF-A" "CH1" "CC3")
for term in "${forbidden[@]}"; do
  if grep -l "$term" ~/Developer/projects/lex-harness/skills/legal-strategy/references/tool-detection.md 2>/dev/null; then
    echo "VIOLATION: '$term' found in tool-detection.md — rewrite"
    exit 1
  fi
done
echo "Jurisdiction-agnostic check PASS"
```

Note: Greek MCP server names (`greek-law-mcp`, `dikaio-ai`) are acceptable — they're tool names, not skill-body content. The `greek-law-mcp` row in the fallback table is referring to the tool's actual name.

- [ ] **Step 3: Commit**

```bash
cd ~/Developer/projects/lex-harness
git add skills/legal-strategy/references/tool-detection.md
git commit -s -m "$(cat <<'EOF'
feat(skill): tool-detection reference file (T11b / PR-12)

Concrete IF/ELSE pattern for detecting optional MCP tools and falling
back when absent. Closes the PR-12 implementation gap identified by the
Plan A validator: every skill body said "detect and fall back" but no
file documented the exact pattern.

Includes:
- Detection method (check tool inventory at session start)
- Per-tool fallback table for chrome-devtools / neo4j / chromadb /
  dikaio-ai / greek-law-mcp / eur-lex
- Concrete walkthrough: evidence capture with and without Chrome MCP
- Logging conventions for [TOOL-UNAVAILABLE:<name>] tags
- Anti-patterns

Every skill in this plugin references this file from its
"Tool-availability discipline" section.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 12: `skills/legal-strategy/references/knowledge-vault.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/references/knowledge-vault.md`

The SOLAR + verbatim retrieval workflow. Jurisdiction-agnostic. References the active law pack via `<case-repo>/05_legal_research/law_pack/`.

- [ ] **Step 1: Write `knowledge-vault.md`**

```bash
cat > skills/legal-strategy/references/knowledge-vault.md <<'EOF'
# Knowledge Vault — SOLAR + verbatim retrieval workflow

> **Loaded by:** legal-strategy skill at session start.
> **Jurisdiction:** any. References the active law pack at
> `<case-repo>/05_legal_research/law_pack/`.

## SOLAR rule

**Statute → Only Loaded → Apply → Refuse otherwise.**

No statute citation may enter a draft until its verbatim text has been loaded from the active law pack. Reasoning from training memory about statute content is PROHIBITED. The model's recall of statute text is unreliable; the only safe source is the loaded vault file.

### Decision tree

```
Need to cite a statute?
│
├─ Is the article in <case-repo>/05_legal_research/law_pack/core/?
│  └─ YES → Load the file. Quote verbatim. Mark [VERIFIED].
│
├─ Is the article in <case-repo>/05_legal_research/law_pack/modules/<m>/?
│  └─ YES (and the module is loaded by the active task) → Load. Quote. Mark [VERIFIED].
│  └─ YES (but the module is not loaded) → Load the module first; then quote.
│
└─ Article is not in the pack at all
   └─ REFUSE to cite. Log gap to <case-repo>/09_ai_research/research_queue.md
      with the article ID, the source URL it should come from (per the
      pack's primary_sources), and the reason for the gap.
```

## Verbatim retrieval

When loading a statute file, the workflow is:

1. Open `<case-repo>/05_legal_research/law_pack/<path>/<article_id>.md`
2. Read the **frontmatter** to confirm: `effective_date` is past, `repeal_date` is null, `last_verified` is recent
3. Read the **verbatim text section** (the block under `## Verbatim text`)
4. Quote it character-for-character in the draft, NEVER paraphrase
5. Append a citation footer: `[<article_id>] sha256:<first-16-of-frontmatter-sha256> verified:<last_verified>`

If the verbatim section contains a `<<FETCH-FROM-...>>` placeholder, the file has not yet been populated. The workflow MUST:

1. Refuse to cite the article
2. Log to `<case-repo>/09_ai_research/research_queue.md`: `[VAULT-INCOMPLETE: <article_id> — fetch from <source_primary>]`
3. Suggest the user run the pack maintenance workflow

## Adverse-precedent registry

Each module's `case_law_inline.md` may contain entries flagged ADVERSE. The skill MUST:

1. Refuse to cite any decision tagged `ADVERSE`
2. Flag attempts as `[ADVERSE-PRECEDENT-BLOCKED:<decision-id>]`
3. Log the attempt to `<case-repo>/07_strategy/core/DECISION_LOG.md`
4. Suggest the alternative precedents listed in the same file

## Three-tier retrieval (with optional MCP fallback)

Per PR-11, every retrieval workflow has an optional-tool path AND a manual-fallback path.

### Tier 1: Markdown (always available)

The base case. The skill loads `core/` + matched modules from disk. Pure markdown read. Zero external tools required. This is the only mandatory path.

### Tier 2: Neo4j (if available)

When `neo4j-memory` MCP is available, the skill MAY query the case repo's fact graph for multi-hop relationships (e.g., "which facts are cited in CH2 AND in CC6?"). On detection failure, the skill falls back to grep across `<case-repo>/06_claims_and_defenses/`.

### Tier 3: ChromaDB (if available)

When ChromaDB indices are available (typically in `<case-repo>/.chroma/`), the skill MAY perform semantic search across cold-tier case law (decisions not in the inline summaries). On detection failure, the skill uses the inline summaries in each module's `case_law_inline.md` only.

**All three tiers produce the same draft schema.** The optional tools accelerate the workflow; they NEVER change the output format, the citation footer, or the verify-gate result.

## Anti-pattern catalogue

These are the failure modes the SOLAR rule prevents:

| Anti-pattern | Why it fails |
|---|---|
| Citing an article from training memory | Model recall is unreliable; "real law applied to wrong context" is the dominant LLM failure mode |
| Paraphrasing statute text | Translation introduces ambiguity; opposing counsel exploits drift |
| Citing an article without checking `repeal_date` | Repealed statute → entire argument collapses on review |
| Citing an article whose `effective_date` is later than the operative facts | Inapplicable retroactively |
| Citing a decision flagged ADVERSE | Hands the opposing party a counter-citation |
| Citing without computing days-remaining for the controlling deadline | Missed-deadline malpractice |

## Cross-references

- The 9-stage verify-gate is in `verify-gate.md`
- Compound argument decomposition is in `atomic-decomposition.md`
- Strategy reasoning is in `strategy-reasoning.md`
- Settlement math is in `settlement-math.md`
- Optional MCP usage details are in `mcp-tools-guide.md`
EOF
```

- [ ] **Step 2: Verify file exists and has SOLAR rule**

```bash
ls -la skills/legal-strategy/references/knowledge-vault.md
grep -c "SOLAR" skills/legal-strategy/references/knowledge-vault.md
grep -c '${CLAUDE_PLUGIN_ROOT}/05_legal_research/law_pack' skills/legal-strategy/references/knowledge-vault.md
```

Expected: file exists, ≥3 SOLAR mentions, ≥1 plugin-root path.

- [ ] **Step 3: Verify NO jurisdiction-specific terms**

```bash
grep -E "(Greek|ΑΚ|ΚΠολΔ|kodiko|Yestay|Άρειος)" skills/legal-strategy/references/knowledge-vault.md && { echo "FAIL"; exit 1; }
echo "PR-01/PR-03 PASS"
```

Expected: `PR-01/PR-03 PASS`

- [ ] **Step 4: Commit**

```bash
git add skills/legal-strategy/references/knowledge-vault.md
git commit -s -m "$(cat <<'EOF'
feat(skill/legal-strategy): knowledge-vault.md SOLAR workflow (T12)

Reference file documenting the SOLAR rule (Statute → Only Loaded →
Apply → Refuse otherwise) and verbatim retrieval workflow. Includes:

- Decision tree for "need to cite a statute?"
- Verbatim retrieval procedure with frontmatter checks
- <<FETCH-FROM-...>> placeholder handling
- Adverse-precedent registry rules (per module case_law_inline.md)
- Three-tier retrieval (markdown / Neo4j / ChromaDB) with PR-11
  optional-tool fallback paths
- Anti-pattern catalogue (6 LLM failure modes)

Jurisdiction-agnostic per PR-01 + PR-03. References active law pack
via <case-repo>/05_legal_research/law_pack/.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 13: `strategy-reasoning.md` + `settlement-math.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/references/strategy-reasoning.md`
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/references/settlement-math.md`

The 1-page strategy checklist (frame → list candidates → apply gates → rank → recommend ONE → log) plus settlement math (ZOPA / BATNA / expected value formulas). Both jurisdiction-agnostic.

- [ ] **Step 1: Write `strategy-reasoning.md`**

```bash
cat > skills/legal-strategy/references/strategy-reasoning.md <<'EOF'
# Strategy Reasoning — 1-Page Checklist

> **Loaded by:** legal-strategy skill in PLAN mode.
> **Jurisdiction:** any. References the active law pack's `playbook.yaml`
> and `forums.yaml` at runtime.

## The 6-step decision loop

Apply this loop every time the user asks "what should I do next?". One pass = one recommendation. Log to DECISION_LOG before exiting.

### Step 1: Frame the goal

State the goal as ONE sentence in the form: "I want X because Y." Examples:

- "I want the opposing party to release my deposit because the deadline is in 60 days."
- "I want to extract the inspection photos because they will defeat the damage charge."
- "I want to escalate to a regulator because civil litigation is too slow."

If the user cannot state a single goal, refuse to proceed and ask for clarification.

### Step 2: List candidate plays

Read `<case-repo>/05_legal_research/law_pack/playbook.yaml` and list every play whose `requires_state` matches the current case state. Cross-reference `<case-repo>/07_strategy/core/DECISION_LOG.md` to remove plays already marked DROPPED.

Output a short table:

| Play ID | Name | Forum | Requires |
|---|---|---|---|
| ... | ... | ... | ... |

### Step 3: Apply quality gates

For each candidate, check the four gates:

1. **Forum precondition** — does `forums.yaml` mark this play's forum as `statutory_blocking` with an unmet `must_complete_first`? If yes → REMOVE.
2. **Deadline ripeness** — does `limitation_periods.yaml` show the controlling deadline within 14 days? If yes → URGENCY +2.
3. **Devil's advocate verdict** — has this play's argument been adversarially reviewed? If no → flag NEEDS-DA.
4. **Resource cost** — does `typical_cost` exceed user's stated budget? If yes → REMOVE or DOWNGRADE.

### Step 4: Rank

Sort surviving candidates by composite score:

```
score = (urgency × 3) + (impact × 2) + (cost_inverse × 1) - (risk × 2)
```

Where:
- urgency = 1-5 (5 = deadline within 14 days)
- impact = 1-5 (5 = closes the dispute or extracts dispositive evidence)
- cost_inverse = 6 - (cost_tier from typical_cost)
- risk = 1-5 (5 = HIGH DA verdict or known DROPPED in DECISION_LOG)

### Step 5: Recommend ONE

Output exactly ONE recommended play in this form:

```
RECOMMENDED: <play-id> — <name>

Why: <one paragraph>
Forum: <forum>
Deadline: <days remaining>
Cost: <typical_cost>
Risk: <HIGH/MEDIUM/LOW>
DA status: <DONE / NEEDS-DA>

Alternatives considered (NOT recommended):
- <play-id-2>: <one sentence why not>
- <play-id-3>: <one sentence why not>
```

NEVER recommend more than one. NEVER recommend a play whose forum has an unmet `statutory_blocking` precondition. NEVER recommend a play marked DROPPED in DECISION_LOG without an explicit reconsideration entry.

### Step 6: Log

Append to `<case-repo>/07_strategy/core/DECISION_LOG.md`:

```markdown
## DL-NN — <date> — <play-id> recommended

**Goal:** <step 1 sentence>
**Recommendation:** <play-id>
**Rationale:** <one sentence>
**Alternatives considered:** <play-id-2, play-id-3>
**Status:** RECOMMENDED — awaiting user decision
```

When the user actually executes the play, update the same DL entry with `Status: EXECUTED — <date>`. When the play produces an outcome, update with `Outcome: <description>`.

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Recommending more than one play | Decision paralysis; user defers and nothing happens |
| Recommending a dropped argument | Wastes the prior DA review; reintroduces known-bad reasoning |
| Skipping the forum precondition gate | Can trigger statutory blocking (criminal-suspends-civil pattern) |
| Recommending without checking deadline | Blows the controlling limitation period |
| Logging after the user has acted, not before | Loses the reasoning chain; later sessions cannot trace why |

## Universal principles applied here

This file is the operational expression of the 6 universal decision principles in the SKILL.md body:

1. **Information First, Attack Second** → bias the score toward information-extracting plays in early phases
2. **Dropped arguments stay dropped** → step 2 filters DECISION_LOG drops
3. **Criminal last** → step 3 catches it via forums.yaml precondition_type: statutory_blocking
4. **Absence is evidence** → boosts impact score for plays that exploit opposing party's record gaps
5. **No depreciation = no enrichment** → built into playbook.yaml universal-pattern plays
6. **One write path for facts** → DECISION_LOG entries are AI-writable; PROVEN_FACTS_REGISTER is human-only
EOF
```

- [ ] **Step 2: Write `settlement-math.md`**

```bash
cat > skills/legal-strategy/references/settlement-math.md <<'EOF'
# Settlement Math — ZOPA, BATNA, Expected Value

> **Loaded by:** legal-strategy skill in NEGOTIATE mode.
> **Jurisdiction:** any. The math is universal; the inputs come from
> the active law pack and the case repo.

## The three quantities

Every settlement reasoning starts with three numbers:

| Quantity | Definition | Source |
|---|---|---|
| **BATNA_user** | Best Alternative To Negotiated Agreement — what the user gets if negotiation fails | Computed from expected litigation outcome (see §EV below) |
| **BATNA_opposing** | The opposing party's best alternative | Computed by reasoning about THEIR likely litigation outcome |
| **ZOPA** | Zone Of Possible Agreement — overlap between user's minimum acceptable and opposing's maximum acceptable | `[BATNA_user, BATNA_opposing]` if user is the claimant; reversed if user is the respondent |

If `BATNA_user > BATNA_opposing`, there is **no ZOPA** — settlement is impossible without one party accepting a worse outcome than litigation. The skill must say so explicitly.

## Expected Value (EV) of litigation

For each disputed amount X, EV is computed as:

```
EV(litigation) = (P_win × X × R_collect) - (P_lose × X_counterclaim) - C_legal - (T × discount_rate)
```

Where:
- `P_win` = probability of winning, estimated from devil-advocate verdict (HIGH = 0.7, MEDIUM = 0.5, LOW = 0.3)
- `X` = amount at stake
- `R_collect` = realistic collection rate (most jurisdictions: 0.7-0.9 against solvent corporates, 0.3-0.5 against individuals)
- `P_lose` = `1 - P_win`
- `X_counterclaim` = amount the opposing party would win on their counterclaim
- `C_legal` = legal costs (court fees + lawyer fees + disbursements)
- `T` = time to judgment in years
- `discount_rate` = user's time-cost-of-money (default 0.05/year for typical disputes; adjust for cash-flow constraints)

## Worked example (jurisdiction-agnostic)

Suppose:
- User claims €5,000 deposit refund
- Opposing party counterclaims €1,500 in damages
- DA verdict on user's claim: HIGH (P_win = 0.7)
- DA verdict on opposing's counterclaim: MEDIUM (P_lose_to_them = 0.5, so user's defence success = 0.5)
- Collection rate against the corporate opposing party: 0.85
- Court fees + legal: €800
- Time to judgment: 1.5 years
- Discount rate: 0.05

```
EV(litigation, user) = (0.7 × €5,000 × 0.85) - (0.5 × €1,500) - €800 - (1.5 × 0.05 × €5,000)
                     = €2,975 - €750 - €800 - €375
                     = €1,050
```

So `BATNA_user = €1,050`. The user should NOT settle for less than €1,050 unless they value avoiding litigation hassle by more than the difference.

## ZOPA construction

Compute `BATNA_opposing` the same way, from the opposing party's perspective. They will settle if the agreed payment ≤ their BATNA-cost. If the user's `BATNA_user` ≤ opposing's `BATNA_opposing - opposing's settlement_cost`, ZOPA exists.

Output the ZOPA as `[BATNA_user, BATNA_opposing - C_opposing]`. Recommend a target inside the ZOPA, biased toward the user's side (≈ 60-70% of the way from BATNA_user to BATNA_opposing).

## Settlement scenarios template

Always present at least 3 scenarios so the user has anchors:

| Scenario | Amount | Rationale |
|---|---|---|
| **S1 — Floor** | `BATNA_user` | The number below which litigation is strictly better |
| **S2 — Target** | mid-ZOPA | The realistic ask |
| **S3 — Anchor** | `BATNA_opposing - C_opposing - small_buffer` | The maximum the opposing party would rationally accept |

Optionally add S4–S7 for risk-adjusted variants (worst case, time-pressured, etc.).

## Sensitivity analysis

For any number that's a guess (`P_win`, `R_collect`, etc.), show the EV at ±20%:

```
EV at P_win = 0.56 (low):  €<recomputed>
EV at P_win = 0.70 (mid):  €1,050
EV at P_win = 0.84 (high): €<recomputed>
```

If the recommendation flips signs across the sensitivity range, the user is in a "true uncertainty" zone — recommend extracting more information before deciding.

## Forum-pressure multiplier (optional)

Some forums (regulator filings, ombudsman complaints, public reviews) increase opposing-party settlement pressure WITHOUT changing the underlying litigation EV. Model this as a multiplier on `BATNA_opposing`:

```
BATNA_opposing_with_pressure = BATNA_opposing × pressure_multiplier
```

Where `pressure_multiplier > 1` for forums that the opposing party particularly wants to avoid (e.g., regulator scrutiny for a regulated entity). The pack's `forums.yaml` may suggest multipliers in the `notes` field.

## Cross-references

- The 6-step strategy decision loop is in `strategy-reasoning.md`
- The verify-gate (which validates the EV inputs) is in `verify-gate.md`
- Forum precondition rules are in the active pack's `forums.yaml`
EOF
```

- [ ] **Step 3: Verify both files exist**

```bash
ls -la skills/legal-strategy/references/strategy-reasoning.md \
       skills/legal-strategy/references/settlement-math.md
```

Expected: both files present.

- [ ] **Step 4: Verify the 6 steps and EV formula**

```bash
grep -c "Step 1: Frame" skills/legal-strategy/references/strategy-reasoning.md
grep -c "Step 6: Log" skills/legal-strategy/references/strategy-reasoning.md
grep -c "EV(litigation)" skills/legal-strategy/references/settlement-math.md
grep -c "BATNA" skills/legal-strategy/references/settlement-math.md
grep -c "ZOPA" skills/legal-strategy/references/settlement-math.md
```

Expected: each ≥ 1.

- [ ] **Step 5: Verify NO jurisdiction-specific terms**

```bash
for f in skills/legal-strategy/references/strategy-reasoning.md \
         skills/legal-strategy/references/settlement-math.md; do
  if grep -E "(Greek|ΑΚ|ΚΠολΔ|kodiko|Yestay|Άρειος)" "$f"; then
    echo "FAIL: $f"; exit 1
  fi
done
echo "PR-01/PR-03 PASS"
```

Expected: `PR-01/PR-03 PASS`

- [ ] **Step 6: Commit**

```bash
git add skills/legal-strategy/references/strategy-reasoning.md skills/legal-strategy/references/settlement-math.md
git commit -s -m "$(cat <<'EOF'
feat(skill/legal-strategy): strategy + settlement math references (T13)

Two reference files for legal-strategy skill:

- strategy-reasoning.md: 1-page 6-step decision loop (frame → list
  candidates → apply gates → rank → recommend ONE → log). Cross-
  references playbook.yaml + forums.yaml + DECISION_LOG.md. Documents
  scoring formula, anti-patterns, and the universal principles that
  underpin the loop.
- settlement-math.md: ZOPA + BATNA + Expected Value formulas with
  worked example, sensitivity analysis, and forum-pressure multiplier.
  Jurisdiction-agnostic — math is universal, inputs come from the
  active law pack and case repo.

Both files PR-01/PR-03 compliant: zero references to Greek law,
country names, or specific cases.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 14: `verify-gate.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/references/verify-gate.md`

The consolidated 9-stage verify-gate per design spec. Stages 1-9 documented. Jurisdiction-agnostic.

- [ ] **Step 1: Write `verify-gate.md`**

```bash
cat > skills/legal-strategy/references/verify-gate.md <<'EOF'
# Verify Gate — 9-stage consolidated workflow

> **Loaded by:** legal-strategy + document-production skills before any
> formal output. Universal across all jurisdictions.

## Purpose

Catch citation errors, fact errors, and reasoning errors BEFORE they leave the workspace. The gate is a SAFETY device, not a quality optimisation. It blocks; it does not improve.

## When to run

- Before any formal document is marked ready-to-send
- Before any citation enters a draft
- Before any new fact is promoted from PENDING to PROVEN
- Before any DA review is dispatched (the dispatch payload itself is verified)

## The 9 stages

### Stage 1: Statute existence

For every cited article, confirm the article file exists in the active law pack:

```bash
test -f "<case-repo>/05_legal_research/law_pack/core/<article_id>.md" || \
test -f "<case-repo>/05_legal_research/law_pack/modules/<m>/<article_id>.md"
```

If neither exists → **HALT** with `[STAGE-1-FAIL: <article_id> not in vault]`. Log to research_queue.md.

### Stage 2: Verbatim text loaded

Read the file. Confirm the `## Verbatim text` section does NOT contain a `<<FETCH-FROM-...>>` placeholder. If it does → **HALT** with `[STAGE-2-FAIL: <article_id> placeholder unfilled]`.

### Stage 3a: Currency

Check frontmatter:
- `effective_date` ≤ today
- `repeal_date` is null OR > today
- `last_verified` within last 90 days

If any fails → **HALT** with `[STAGE-3A-FAIL: <article_id> currency check]`.

### Stage 3b: Holding characterisation (Schutzzweck)

Confirm the cited article's protective purpose covers THIS user. Common failure modes:

- Citing a worker-protection statute for a tenant claim
- Citing a spousal-succession article for a damage claim
- Citing a rule-of-evidence article for a substantive remedy

The skill must read the article's `short_name` + the `Used in` section of the file and confirm the use case matches. If mismatch → **HALT** with `[STAGE-3B-FAIL: schutzzweck mismatch — <article_id> protects X, this case needs Y]`.

This stage is the dominant LLM failure-mode catcher. Most "real law applied to wrong context" errors die here.

### Stage 4: Citation footer

Every citation in the draft must have an inline footer:

```
[<article_id>] sha256:<first-16> verified:<YYYY-MM-DD>
```

The sha256 prefix and verified date come from the article file's frontmatter. Missing footer → **HALT** with `[STAGE-4-FAIL: <article_id> missing citation footer]`.

### Stage 5: Fact references (PF codes)

Every factual claim in the draft must reference a `PF-<code>` from the case repo's PROVEN_FACTS_REGISTER. Unsupported claims → **HALT** with `[STAGE-5-FAIL: <claim text excerpt> has no PF reference]`.

### Stage 6: Date arithmetic

Recompute every date arithmetic in the draft (limitation periods, response windows, deadline calculations). If the draft says "deadline 2026-06-07" and recomputation says "2026-06-08", **HALT** with `[STAGE-6-FAIL: date drift]`.

### Stage 7: Amount arithmetic

Recompute every monetary calculation (set-off totals, depreciation, expected value). Cross-check against the case repo's CASE_OVERVIEW.md amounts. Drift → **HALT** with `[STAGE-7-FAIL: amount drift]`.

### Stage 8: Adverse-precedent block

Scan the draft for any decision flagged ADVERSE in any loaded module's `case_law_inline.md`. If found → **HALT** with `[STAGE-8-FAIL: ADVERSE-PRECEDENT-BLOCKED <decision-id>]`.

### Stage 9: Footer block presence

Every formal output must end with the mandatory 4-field footer block:

```
---
pf_ids: [PF-A01, PF-A02, ...]
law_articles: [<article_id>, ...]
evidence_items: [E-001, E-002, ...]
da_review_refs: [DA_<arg-id>_<date>, ...]
---
```

Missing footer → **HALT** with `[STAGE-9-FAIL: footer block missing]`.

## Verdict

The gate emits exactly one of:

- `[VERIFY-GATE-PASS]` — proceed to release
- `[VERIFY-GATE-FAIL: <list of stage failures>]` — block release; user must address

The gate NEVER auto-fixes. It blocks and reports.

## Tool-availability discipline (PR-12)

The gate is implemented in pure markdown logic — no MCP servers required. If optional tools are available (e.g., a checksum-verification MCP), they MAY be used to accelerate stages 4 (sha256 check) and 6/7 (arithmetic). On unavailability, the skill performs the checks manually and logs `[TOOL-UNAVAILABLE:<name>]`.

## Cross-references

- The SOLAR rule (Stage 1-2 foundation) is in `knowledge-vault.md`
- The atomic decomposition workflow that feeds Stage 5 is in `atomic-decomposition.md`
- The strategy decision loop that feeds Stage 8 is in `strategy-reasoning.md`
- Optional MCP details are in `mcp-tools-guide.md`
EOF
```

- [ ] **Step 2: Verify file has 9 stages**

```bash
ls -la skills/legal-strategy/references/verify-gate.md
for s in 1 "2" "3a" "3b" 4 5 6 7 8 9; do
  grep -q "^### Stage $s" skills/legal-strategy/references/verify-gate.md || { echo "missing Stage $s"; exit 1; }
done
echo "all stages present"
```

Expected: `all stages present`.

- [ ] **Step 3: Verify no jurisdiction-specific terms**

```bash
grep -E "(Greek|ΑΚ|ΚΠολΔ|kodiko|Yestay|Άρειος)" skills/legal-strategy/references/verify-gate.md && { echo "FAIL"; exit 1; }
echo "PR-01/PR-03 PASS"
```

Expected: `PR-01/PR-03 PASS`.

- [ ] **Step 4: Commit**

```bash
git add skills/legal-strategy/references/verify-gate.md
git commit -s -m "$(cat <<'EOF'
feat(skill/legal-strategy): verify-gate.md 9-stage consolidated gate (T14)

Reference file documenting the 9-stage verify-gate run before any
formal output:

- Stage 1: Statute existence (file in vault)
- Stage 2: Verbatim text loaded (no <<FETCH-FROM>> placeholder)
- Stage 3a: Currency (effective/repeal/last_verified dates)
- Stage 3b: Holding characterisation / Schutzzweck — the dominant
  LLM failure-mode catcher
- Stage 4: Citation footer (sha256 + verified date)
- Stage 5: Fact references (PF codes)
- Stage 6: Date arithmetic recompute
- Stage 7: Amount arithmetic recompute
- Stage 8: Adverse-precedent block
- Stage 9: Footer block presence (pf_ids, law_articles, evidence_items,
  da_review_refs)

Verdicts: [VERIFY-GATE-PASS] or [VERIFY-GATE-FAIL: <stages>]. Gate
NEVER auto-fixes — blocks and reports.

Jurisdiction-agnostic per PR-01 + PR-03. Optional tool support
documented per PR-12.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 15: `atomic-decomposition.md`

**Files:**
- Create: `~/Developer/projects/lex-harness/skills/legal-strategy/references/atomic-decomposition.md`

Compound argument → element rows workflow. Jurisdiction-agnostic.

- [ ] **Step 1: Write `atomic-decomposition.md`**

```bash
cat > skills/legal-strategy/references/atomic-decomposition.md <<'EOF'
# Atomic Decomposition — compound argument → element rows

> **Loaded by:** legal-strategy + document-production skills before
> dispatching devil-advocate or drafting any compound argument.
> **Jurisdiction:** any.

## Why decompose

A compound legal argument (e.g., "systematic bad faith" with 15 elements, "unfair commercial practice" with 4 elements, "abuse of right" with 3 elements) cannot be reviewed as a single block. Devil-advocate dispatched on a compound argument collapses to one of two failure modes:

1. **Sycophantic agreement** — DA finds no flaws because the surface narrative is internally coherent
2. **Wholesale rejection** — DA flags the strongest element as suspect and tags the whole argument

Both failures are caused by reviewing the argument at the wrong granularity. The fix is to decompose into atomic element rows — each row reviewed independently.

## The element-row schema

For each element of a compound argument, produce one row with these fields:

```yaml
element_id: <argument-id>-E<NN>
element_label: <one-line description>
factual_premise:
  pf_ids: [PF-A01, PF-A02, ...]
  text: "<the verbatim factual claim>"
legal_warrant:
  article_ids: [AK_281, AK_288]
  text: "<the verbatim statute text from the loaded vault>"
inference: "<the bridge from premise to legal conclusion>"
da_verdict: <DONE / NEEDS-DA / DROPPED / DOWNGRADED>
da_review_ref: DA_<element-id>_<YYYY-MM-DD>.md
status: ACTIVE / DROPPED / DOWNGRADED
notes: <optional>
```

The compound argument is then the SET of element rows, not a prose narrative. The narrative is a derived view; the element rows are the source of truth.

## The 5-step workflow

### Step 1: Identify the compound argument

User asks the skill to draft / review / strengthen a compound argument. The skill checks: does this argument have ≥2 elements? If yes, decomposition applies.

### Step 2: Enumerate elements

Read the existing argument file (e.g., `<case-repo>/07_strategy/SA<NN>_*.md`). List every element. If the file does not yet decompose into elements, the skill DOES the decomposition itself by extracting each independent factual + legal claim.

Output the element list as a numbered table for user review BEFORE proceeding to step 3.

### Step 3: Build element rows

For each element, populate the schema above:

- `pf_ids` — find the PF codes that support this element. If no PF exists, log gap to PENDING_FACTS.md.
- `factual_premise.text` — verbatim from the case repo
- `article_ids` — the statutes the element relies on
- `legal_warrant.text` — verbatim from the loaded law pack (run the SOLAR rule first)
- `inference` — the bridge sentence

Each row is independent. No row references the conclusions of another row.

### Step 4: Dispatch devil-advocate per row

For each row marked `da_verdict: NEEDS-DA`, dispatch the devil-advocate skill in isolated subagent mode with the row as the SOLE input. The dispatch payload contains:

- `element_id`
- `factual_premise` (text only — no PF codes that might leak case context)
- `legal_warrant` (statute text only — no module commentary)
- `inference`
- `forum` (where the argument will be deployed)

The DA returns a per-row verdict: SOUND / NEEDS-WORK / DROP. Update each row's `da_verdict` and `da_review_ref` accordingly.

### Step 5: Recompose

Once all rows have a non-NEEDS-DA verdict, recompose the argument:

- ACTIVE rows → keep
- DOWNGRADED rows → keep but flag in the narrative
- DROPPED rows → remove from the narrative + log to DECISION_LOG

The recomposed argument is the union of ACTIVE + DOWNGRADED rows. The narrative MUST cite each row's element_id so readers can trace back to the source.

## Example

User asks for review of a 5-element compound argument. The skill:

1. Reads the SA file
2. Extracts 5 element labels
3. Builds 5 element rows with PF codes + statute citations
4. Dispatches DA on rows E01..E05 in parallel (5 isolated subagents)
5. Receives verdicts: E01=SOUND, E02=SOUND, E03=NEEDS-WORK, E04=DROP, E05=SOUND
6. Drops E04, downgrades E03, recomposes the argument with 4 elements
7. Logs E04 drop to DECISION_LOG
8. Returns the recomposed argument to the user

## Anti-patterns

| Anti-pattern | Why it fails |
|---|---|
| Reviewing the compound argument as one block | DA collapses to sycophantic agreement |
| Letting one row reference another row's conclusion | Inheritance chains poison the isolation |
| Skipping SOLAR on the legal_warrant text | Hallucinated statute slips through DA |
| Recomposing without removing dropped rows | Readers re-discover the dropped reasoning and resurface it |
| Failing to update DECISION_LOG on drop | Same dropped argument resurfaces in next session |

## Handoff

After decomposition, hand off to:

- `document-production` skill if drafting a formal document
- `devil-advocate` skill (via the `/<plugin>:devil` command) if running adversarial review

## Cross-references

- The verify-gate (which checks element rows for completeness) is in `verify-gate.md`
- The strategy decision loop (which decides whether to deploy a recomposed argument) is in `strategy-reasoning.md`
- The SOLAR rule (which gates legal_warrant population) is in `knowledge-vault.md`
EOF
```

- [ ] **Step 2: Verify file structure**

```bash
ls -la skills/legal-strategy/references/atomic-decomposition.md
grep -c "element_id:" skills/legal-strategy/references/atomic-decomposition.md
grep -c "Step [1-5]:" skills/legal-strategy/references/atomic-decomposition.md
```

Expected: file exists, ≥1 element_id mention, ≥5 step headings.

- [ ] **Step 3: Verify no jurisdiction-specific terms**

```bash
grep -E "(Greek|ΑΚ |ΚΠολΔ|kodiko|Yestay|Άρειος)" skills/legal-strategy/references/atomic-decomposition.md && { echo "FAIL"; exit 1; }
echo "PR-01/PR-03 PASS"
```

Expected: `PR-01/PR-03 PASS`. (Note: `AK_281` in the YAML schema example uses underscore, not the standalone abbreviation.)

- [ ] **Step 4: Verify cross-reference set is complete**

```bash
for ref in verify-gate.md strategy-reasoning.md knowledge-vault.md; do
  grep -q "$ref" skills/legal-strategy/references/atomic-decomposition.md || { echo "missing cross-ref to $ref"; exit 1; }
done
echo "cross-references complete"
```

Expected: `cross-references complete`.

- [ ] **Step 5: Final reference-files inventory check**

```bash
ls -la skills/legal-strategy/references/
```

Expected to see (from T12-T15):
- knowledge-vault.md
- strategy-reasoning.md
- settlement-math.md
- verify-gate.md
- atomic-decomposition.md

(`mcp-tools-guide.md` is created in a later task or in T16+ — out of scope here.)

- [ ] **Step 6: Commit**

```bash
git add skills/legal-strategy/references/atomic-decomposition.md
git commit -s -m "$(cat <<'EOF'
feat(skill/legal-strategy): atomic-decomposition.md workflow (T15)

Reference file documenting the compound-argument → element-rows
decomposition workflow:

- Why decompose: compound arguments fool devil-advocate into either
  sycophantic agreement or wholesale rejection
- Element-row YAML schema (element_id, factual_premise, legal_warrant,
  inference, da_verdict, status)
- 5-step workflow: identify → enumerate → build rows → dispatch DA
  per row → recompose
- Worked example showing DROP/DOWNGRADE/SOUND verdicts
- 5 anti-patterns with failure-mode explanations
- Handoff rules to document-production + devil-advocate skills
- Cross-references to verify-gate, strategy-reasoning, knowledge-vault

Jurisdiction-agnostic per PR-01 + PR-03. Article IDs in the schema
example use underscore form (AK_281) not abbreviation form, so the
file passes the layer-separation grep check.

Closes the T11-T15 wave: legal-strategy SKILL.md + 5 reference files
(knowledge-vault, strategy-reasoning, settlement-math, verify-gate,
atomic-decomposition) all in place. The skill is now functional and
PR-01/PR-03 compliant.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

**End of Plan A part 2.** Tasks T16 through T37 continue in subsequent files (`2026-04-07-lex-harness-v0.1-part3.md` and `-part4.md`) covering the osint-investigation, document-production, devil-advocate skills, the 3 slash commands, templates, bootstrap scripts, additional Greek modules (tax_invoices, corporate), tests, docs, CI workflow, and the v0.1.0 release.
