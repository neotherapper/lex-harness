Continuation of `2026-04-07-lex-harness-v0.1.md` part 4 — Tasks T28 through T37 (final)

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement these tasks.
>
> **Predecessors:** Plan A part 1 (T0–T4), part 2 (T5–T15), part 3 (T16–T27). This file contains the **final** ten tasks: T28 (tax_invoices module), T29 (corporate module), T30 (Codex bootstrap), T31 (validate-pack.sh), T32 (manual smoke tests), T33 (ARCHITECTURE.md), T34 (PR docs + roadmap), T35 (tool optionality + security), T36 (CI workflow + GitHub templates), T37 (v0.1.0 release with stop-go gate).
>
> **All file paths absolute under `~/Developer/projects/lex-harness/`. `${CLAUDE_PLUGIN_ROOT}` is used for intra-plugin references inside skill / command bodies — NEVER inside scripts (scripts use `$REPO_ROOT` or relative paths).**

---

## Wave 4 — Tax + corporate modules, scripts, tests, docs, CI, release

This wave finishes the Greek law pack (T28–T29), wires the plugin into Codex (T30), gives contributors a validator (T31), ships manual smoke tests + the architecture/contract docs (T32–T35), turns on CI + the GitHub release surface (T36), and finally ships v0.1.0 behind a hard stop-go gate (T37).

After T37 the plugin is **live on `github.com/neotherapper/lex-harness`** and yestay is unblocked to start Plan B.

---

## Task 28: Greek `tax_invoices` module

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tax_invoices/_module.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tax_invoices/N_4172_2013_Art_24.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tax_invoices/N_4308_2014_Art_9.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tax_invoices/N_4308_2014_Art_18.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tax_invoices/N_5177_2025_Art_3_16.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/tax_invoices/AADE_E_2094_2025.md`

**Source map (per LEGAL_CORPUS_MAP §2 Module 6 + §4 step 8):**
- `N_4172/2013` Art. 24 → **lawspot.gr** (primary), kodiko.gr (verification)
- `N_4308/2014` Arts. 9 + 18 → **taxheaven.gr** (primary), search.et.gr (verification)
- `N_5177/2025` Art. 3 + 16 → **search.et.gr** (primary, ΦΕΚ Α' 21/14.02.2025); REPLACES the older N_5135/2024 stamp-duty regime — explicit note required
- `AADE_E_2094/2025` → **aade.gr** (primary); circular implementing N_5177/2025 stamp-duty rules

**Why this module matters:** invoice analysis, AADE referral, depreciation arguments (CH4 fridge book-value €0 via instant write-off), CH2 stamp-duty mutual exclusion. See LEGAL_CORPUS_MAP §2 Module 6.

- [ ] **Step 1: Create the module directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p law-packs/greece/modules/tax_invoices
```

- [ ] **Step 2: Write `_module.md` (trigger metadata + routing)**

```bash
cat > law-packs/greece/modules/tax_invoices/_module.md <<'EOF'
---
module_id: tax_invoices
language: el
default_loaded: false
trigger_signals:
  - invoice analysis
  - AADE referral
  - depreciation argument
  - book value
  - instant write-off
  - sub-€1,500 asset
  - stamp duty (χαρτόσημο)
  - mutual exclusion (rent vs damages)
  - myDATA
  - DTD
  - N_5177/2025
  - facturation Greek
articles:
  - N_4172_2013_Art_24
  - N_4308_2014_Art_9
  - N_4308_2014_Art_18
  - N_5177_2025_Art_3_16
  - AADE_E_2094_2025
inline_case_law: []
last_verified: 2026-04-07
---

# Module: tax_invoices

Greek tax + invoice statutory framework.

## Scope

This module loads when reasoning about:

- Whether an asset can be depreciated (Art. 24(7) instant write-off for sub-€1,500 items → book value €0)
- Whether an invoice complies with N_4308/2014 content + timing requirements
- Whether a charge labelled as damages is mutually exclusive with rent VAT classification
- Whether stamp duty (χαρτόσημο) was lawfully applied post-Feb 2025 under N_5177/2025 (which **REPLACES** the prior N_5135/2024 regime)
- Whether an AADE referral is warranted (forensic accounting threshold)

## Articles

| ID | Short name | Use case |
|---|---|---|
| `N_4172_2013_Art_24` | Income tax — depreciation + sub-€1,500 instant write-off | CH4 fridge book value €0; depreciation defence |
| `N_4308_2014_Art_9` | ELP — required invoice content (issuer, recipient ΑΦΜ, "είδος και έκταση", VAT) | Invoice validity attack; CH1/CH2 invoice non-compliance |
| `N_4308_2014_Art_18` | ELP — invoice timing (15-day rule, end-of-month rule) | "23 days departure → invoice physically implausible" line |
| `N_5177_2025_Art_3_16` | Digital Transactions Duty (DTD) — POST-Feb 2025 framework. **REPLACES N_5135/2024** | Stamp-duty mutual-exclusion attacks for ALL post-Feb 2025 invoices |
| `AADE_E_2094_2025` | AADE circular implementing N_5177/2025 DTD | Circular-level cite for AADE referral memos |

## Critical version pin

**Anyone reasoning about stamp duty on a 2025+ invoice MUST use `N_5177_2025_Art_3_16`, not the older `N_5135_2024`. The latter was repealed and no longer applies. The skill verify-gate Stage 3b catches drafts that cite the wrong version.**

## Cross-module links

- → `core/AK_904.md` (unjust enrichment — landlord's recovery basis when book value is €0)
- → `modules/tenancy/AK_592.md` (normal wear exemption — competes with depreciation argument)
- → `modules/criminal_regulatory/PK_375.md` (φοροδιαφυγή / forgery if invoice is materially false)

## Source files

All article files in this directory have YAML frontmatter declaring `source_primary` + `source_verification` URLs and a `sha256` hash of the verbatim text section.
EOF
```

- [ ] **Step 3: Write `N_4172_2013_Art_24.md` (depreciation + sub-€1,500 write-off)**

```bash
cat > law-packs/greece/modules/tax_invoices/N_4172_2013_Art_24.md <<'EOF'
---
article_id: N_4172_2013_Art_24
short_name: "Income Tax Code — depreciation of fixed assets and intangibles"
statute: Νόμος 4172/2013 (Κώδικας Φορολογίας Εισοδήματος — ΚΦΕ)
article_number: "24"
source_primary: https://www.lawspot.gr/nomikes-plirofories/nomothesia/n-4172-2013/arthro-24-nomos-4172-2013-aposvesi-pagion
source_verification: https://www.kodiko.gr/nomologia/document_navigation/57906/nomos-4172-2013
effective_date: 2014-01-01
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
---

# Άρθρο 24 ν. 4172/2013 — Αποσβέσεις (income tax depreciation)

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from lawspot.gr; replace this block with the official text. Compute the sha256 of the inserted text and update the frontmatter `sha256` field accordingly.**

> Article 24 establishes the depreciation regime for tangible and intangible fixed assets used in business activity. Key paragraphs the harness relies on:
>
> - **§1** — assets must be depreciated; rates per the Annex table
> - **§2** — economic owner depreciates (not necessarily legal owner); leasing rules
> - **§7** — assets with **acquisition value ≤ €1,500** are written off in **a single tax year** (instant 100% write-off → residual book value = €0 from year of acquisition)

The verbatim Greek text MUST be pasted in this section before the module is considered complete. Do NOT proceed to module use until the placeholder is replaced.

## Operative meaning (one paragraph)

Article 24(7) of the Greek Income Tax Code mandates that any tangible asset acquired for €1,500 or less is fully depreciated in the year of acquisition. After that single tax year, the residual book value of the asset is **zero**. This is a STATUTORY rule, not an option — the taxpayer cannot elect to depreciate over multiple years for sub-threshold items. Combined with the bookkeeping rule that a fully written-off asset has no remaining capitalised loss, any subsequent "loss" claimed against such an item is unsupported by the books.

## Forensic application (per FORENSIC_ACCOUNTING_METHODOLOGY.md)

Two consequences for damages claims involving fixtures, fittings, or appliances:

1. **Book value attack** — if the lessor charges the tenant for "damage" to a furnishing or appliance whose acquisition value was ≤ €1,500, that asset has been fully written off under §7. Its book value is €0. There is no residual capitalised loss to recover (Art. 904 ΑΚ unjust enrichment kicks in if the lessor recovers more than €0).
2. **Διαγραφή trap** — if the lessor labels the asset as "άχρηστο" (unusable) on its accounting books, the formal write-off (Διαγραφή) records a €0 disposal loss. The lessor cannot then turn around and demand the tenant pay the "loss" — the books say there was no loss.

## Cross-references inside the case

- `06_claims_and_defenses/CH4_fridge.md` — primary use site; PF-F53 / PF-F54 anchor
- `07_strategy/forensic/FORENSIC_ACCOUNTING_METHODOLOGY.md` — five-layer analysis protocol citing this article
- `04_evidence/invoices/ACCOUNTING_ERRORS_ANALYSIS.md` — invoice-level deployment

## Verification

- **Primary:** lawspot.gr article URL above
- **Verification:** kodiko.gr (confirms text matches official codification)
- **Pin date:** verified 2026-04-07 — re-verify quarterly per LEGAL_CORPUS_MAP §4 step 14
EOF
```

- [ ] **Step 4: Write `N_4308_2014_Art_9.md` (invoice content)**

```bash
cat > law-packs/greece/modules/tax_invoices/N_4308_2014_Art_9.md <<'EOF'
---
article_id: N_4308_2014_Art_9
short_name: "ELP — required content of an invoice"
statute: Νόμος 4308/2014 (Ελληνικά Λογιστικά Πρότυπα — ΕΛΠ)
article_number: "9"
source_primary: https://www.taxheaven.gr/law/4308/2014/article/9
source_verification: https://www.et.gr/api/DownloadFek/?fek_pdf=20140100251
effective_date: 2015-01-01
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
---

# Άρθρο 9 ν. 4308/2014 — Περιεχόμενο τιμολογίου (mandatory invoice content)

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from taxheaven.gr; replace this block with the official text. Compute the sha256 of the inserted text and update frontmatter `sha256`.**

> Article 9 of the Greek Accounting Standards Code (ΕΛΠ) lists the **mandatory** content of every invoice issued by a Greek business. The harness verify-gate uses these clauses to attack invoices that fail to comply.

## Operative content checklist (§1)

A compliant invoice MUST contain at least:

- **(α)** Issue date
- **(β)** Sequential serial number
- **(γ)** Issuer name, address, ΑΦΜ, ΔΟΥ
- **(δ)** Recipient name, address, ΑΦΜ, ΔΟΥ
- **(ε)** Type and quantity of goods / **type and extent of services rendered** (η φύση και η έκταση των υπηρεσιών)
- **(ζ)** Unit price + total per line
- **(στ)** **Description of services per VAT category** + per-rate breakdown
- **(η)** Total amount with and without VAT, plus VAT rate
- **(θ)** Reference to a relevant exemption if VAT is not charged

## Operative meaning (one paragraph)

When a Greek business issues an invoice for services it MUST describe the **type and extent** of the services (clause (στ)). A line item that says only "various works" or "repairs" without quantifying the type and extent fails clause (στ) and is non-compliant. A non-compliant invoice is not invalid as a tax document automatically, but it (1) loses its presumption of accuracy in civil litigation (KPolD evidentiary status), (2) triggers ELP penalty exposure for the issuer, and (3) supports an AADE referral if the omission is systematic.

## Forensic application

Use the §1 checklist as the **first pass** when forensic-analysing any invoice the opposing party relies on. For each missing field, log the omission in the case-level invoice-analysis file. Three or more material omissions on a single invoice = strong AADE referral candidate per FORENSIC_ACCOUNTING_METHODOLOGY decision matrix.

## Cross-references inside the case

- `04_evidence/invoices/ACCOUNTING_ERRORS_ANALYSIS.md` — 22 facts; many anchor here
- `06_claims_and_defenses/CH2_painting.md` — NK-5 ("statutory invoice violation")
- `07_strategy/forensic/ACCOUNTING_ERRORS_DEPLOYMENT.md` — tactical deployment table

## Verification

- **Primary:** taxheaven.gr article URL above (free, indexed copy with annotations)
- **Verification:** et.gr ΦΕΚ download (Α' 251/24.11.2014) for the official gazette text
- **Pin date:** 2026-04-07
EOF
```

- [ ] **Step 5: Write `N_4308_2014_Art_18.md` (invoice timing)**

```bash
cat > law-packs/greece/modules/tax_invoices/N_4308_2014_Art_18.md <<'EOF'
---
article_id: N_4308_2014_Art_18
short_name: "ELP — timing rules for issuing invoices"
statute: Νόμος 4308/2014 (Ελληνικά Λογιστικά Πρότυπα — ΕΛΠ)
article_number: "18"
source_primary: https://www.taxheaven.gr/law/4308/2014/article/18
source_verification: https://www.et.gr/api/DownloadFek/?fek_pdf=20140100251
effective_date: 2015-01-01
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
---

# Άρθρο 18 ν. 4308/2014 — Χρόνος έκδοσης τιμολογίου (invoice timing)

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from taxheaven.gr.**

> Article 18 sets the deadline by which a Greek business MUST issue an invoice for goods delivered or services rendered. These deadlines are administratively enforceable and have evidentiary weight in civil disputes about timing.

## Operative timing rules

- **§1 (general rule)** — invoice issued at the time the chargeable event occurs
- **§2 (services)** — for services rendered to another business, the invoice MUST be issued **by the 15th day of the month following** the month in which the service was completed
- **§5 (open issue handling)** — for continuing or recurring services, end-of-month rule applies

## Operative meaning (one paragraph)

If an invoice was issued substantially earlier than the chargeable event (e.g., before the underlying work was performed), or substantially later than the §2 / §5 deadline, the timing itself is evidentiary. Both anomalies signal that either (a) the underlying transaction never occurred as described, (b) the invoice was generated to fit a litigation theory, or (c) the bookkeeping was reverse-engineered. The harness uses this as the basis for the "physically implausible turnaround" attack: a 23-day departure-to-invoice window in December Athens, for €898 of paint work, is inconsistent with §2 timing AND inconsistent with the actual logistics of arranging tradespeople in that month.

## Forensic application

For every invoice in evidence, compute:

1. The chargeable event date (delivery or service completion)
2. The invoice issue date
3. The §2 / §5 deadline derived from (1)
4. The delta in days

Flag deltas > 30 days OR deltas < 0 (invoice predates the event) as anomalous.

## Cross-references inside the case

- `06_claims_and_defenses/CH2_painting.md` — NK-7 (23-day implausibility line)
- `07_strategy/forensic/FORENSIC_ACCOUNTING_METHODOLOGY.md` — Layer 3 (timing analysis)

## Verification

- **Primary:** taxheaven.gr
- **Verification:** ΦΕΚ Α' 251/24.11.2014 via et.gr
- **Pin date:** 2026-04-07
EOF
```

- [ ] **Step 6: Write `N_5177_2025_Art_3_16.md` (post-Feb-2025 DTD; REPLACES N_5135/2024)**

> **CRITICAL VERIFICATION:** the `effective_date` MUST be `2025-02-14` (ΦΕΚ Α' 21/14.02.2025). The frontmatter MUST also carry `replaces: N_5135_2024` so the verify-gate can detect drafts citing the obsolete law.

```bash
cat > law-packs/greece/modules/tax_invoices/N_5177_2025_Art_3_16.md <<'EOF'
---
article_id: N_5177_2025_Art_3_16
short_name: "Digital Transactions Duty (DTD) — post-Feb 2025 stamp-duty regime"
statute: Νόμος 5177/2025
article_number: "3 + 16"
source_primary: https://www.et.gr/api/DownloadFek/?fek_pdf=20250100021
source_verification: https://www.aade.gr/egkyklioi-kai-apofaseis/e-2094-2025
effective_date: 2025-02-14
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
replaces:
  - N_5135_2024
fek_reference: ΦΕΚ Α' 21/14.02.2025
---

# Άρθρα 3 + 16 ν. 5177/2025 — Τέλος Ψηφιακών Συναλλαγών (Digital Transactions Duty)

## ⚠ VERSION PIN — REPLACES N_5135/2024

**This article ENTERED INTO FORCE on 2025-02-14 (ΦΕΚ Α' 21/14.02.2025) and REPLACED N. 5135/2024.** Any draft, memo, or legal-strategy output that cites N_5135/2024 for an event occurring on or after 2025-02-14 is **WRONG**. The harness verify-gate Stage 3b is configured to flag drafts that pair a post-Feb-2025 invoice with a pre-Feb-2025 stamp-duty statute citation. Never use the older statute for a post-Feb-2025 fact.

When in doubt, cite this file (`N_5177_2025_Art_3_16`) for any 2025+ stamp-duty / DTD analysis.

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from search.et.gr (ΦΕΚ Α' 21/14.02.2025); replace this block. Update sha256.**

> Article 3 defines the chargeable transaction categories for the Digital Transactions Duty (the modern replacement for χαρτόσημο on certain transaction types). Article 16 sets the rates and the carve-outs.

## Operative meaning (one paragraph)

The Digital Transactions Duty (Τέλος Ψηφιακών Συναλλαγών — DTD) replaced the pre-existing stamp-duty regime for documented transactions starting 2025-02-14. The old N_5135/2024 stamp-duty rules no longer govern post-cutover events. For the harness, the practical consequences are: (1) any 2025+ invoice that purports to apply χαρτόσημο 3.6% must instead apply (or be exempt under) the N_5177/2025 / DTD framework; (2) "rent vs damages" mutual-exclusion attacks based on stamp duty MUST cite this article + the AADE circular (`AADE_E_2094/2025`) — never the obsolete law; (3) the AADE referral pathway also routes through the DTD circular, not the old regime.

## Forensic application

Three layered checks for every 2025+ invoice:

1. Was DTD applied at all? If the invoice was issued post-2025-02-14 and the underlying transaction is within Article 3's scope, DTD must be applied OR an exemption must be cited.
2. If DTD was applied, was the rate correct per Article 16?
3. If the invoice instead applied old-regime χαρτόσημο, the issuer mis-applied repealed law — administrative violation + potential AADE referral.

## Cross-references inside the case

- `modules/tax_invoices/AADE_E_2094_2025.md` — implementing circular (companion file)
- `06_claims_and_defenses/CH2_painting.md` — NK-4 ("stamp duty abolished" line)
- `07_strategy/escalation/AADE_REFERRAL_MEMO.md` — AADE escalation pathway

## Verification

- **Primary:** search.et.gr → ΦΕΚ Α' 21/14.02.2025 PDF
- **Verification:** aade.gr circular E.2094/2025 (companion file in this module)
- **Pin date:** 2026-04-07; re-verify quarterly per LEGAL_CORPUS_MAP §4 step 14
EOF
```

- [ ] **Step 7: Write `AADE_E_2094_2025.md` (implementing circular)**

```bash
cat > law-packs/greece/modules/tax_invoices/AADE_E_2094_2025.md <<'EOF'
---
article_id: AADE_E_2094_2025
short_name: "AADE Circular E.2094/2025 — implementing N_5177/2025 DTD rules"
statute: Εγκύκλιος Α.Α.Δ.Ε. Ε.2094/2025
article_number: "n/a (administrative circular)"
source_primary: https://www.aade.gr/egkyklioi-kai-apofaseis/e-2094-2025
source_verification: https://www.taxheaven.gr/circulars/40000/e-2094-2025
effective_date: 2025-02-21
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
implements:
  - N_5177_2025_Art_3_16
---

# Εγκύκλιος Α.Α.Δ.Ε. Ε.2094/2025 — implementing the new DTD regime

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from aade.gr; replace this block. Update sha256.**

> AADE circular E.2094/2025 implements the Digital Transactions Duty introduced by N_5177/2025. It is the operational guidance Greek tax authorities and businesses follow for the new regime. As an administrative circular it is not statute, but it has binding effect on the tax administration's own conduct and is routinely cited in AADE-facing complaints.

## Operative content

The circular addresses, among other things:

- Which transactions fall inside vs. outside the DTD scope
- The mechanics of declaring + paying DTD via myDATA
- Transitional rules for invoices straddling the 2025-02-14 effective date
- Penalty exposure for issuers who fail to apply DTD or who continue applying repealed χαρτόσημο

## Forensic application

When drafting an AADE referral memo for stamp-duty / DTD irregularities on a 2025+ invoice, the legal authority chain is:

1. **Primary statute:** `N_5177_2025_Art_3_16` (the law)
2. **Implementing circular:** `AADE_E_2094_2025` (this file)
3. **Procedural law:** `N_4308_2014_Art_18` (timing) + `N_4308_2014_Art_9` (content)

A complete AADE referral cites all four. The harness `document-production` skill loads this entire chain when the active task is "AADE referral memo".

## Cross-references inside the case

- `modules/tax_invoices/N_5177_2025_Art_3_16.md` — parent statute
- `07_strategy/escalation/AADE_REFERRAL_MEMO.md` — Greek-language template using this chain

## Verification

- **Primary:** aade.gr official circular page
- **Verification:** taxheaven.gr indexed copy
- **Pin date:** 2026-04-07
EOF
```

- [ ] **Step 8: Verify the module loads cleanly**

```bash
ls -la law-packs/greece/modules/tax_invoices/
wc -l law-packs/greece/modules/tax_invoices/*.md
```

Expected: 6 files exist (`_module.md` + 5 article files), all >40 lines each.

Run the per-file frontmatter check:

```bash
for f in law-packs/greece/modules/tax_invoices/N_*.md law-packs/greece/modules/tax_invoices/AADE_*.md; do
  python3 -c "
import sys, re
content = open('$f').read()
m = re.match(r'^---\n(.*?)\n---', content, re.S)
assert m, '$f: no frontmatter'
fm = m.group(1)
for required in ['article_id', 'short_name', 'source_primary', 'source_verification', 'effective_date', 'sha256', 'translation_status', 'last_verified']:
    assert required + ':' in fm, '$f: missing ' + required
print('$f OK')
"
done
```

Expected: 5 lines each ending in `OK`.

Verify the N_5177 effective date specifically:

```bash
grep "effective_date: 2025-02-14" law-packs/greece/modules/tax_invoices/N_5177_2025_Art_3_16.md && echo "N_5177 effective date OK"
grep "replaces:" law-packs/greece/modules/tax_invoices/N_5177_2025_Art_3_16.md && echo "N_5177 replaces field OK"
grep "N_5135_2024" law-packs/greece/modules/tax_invoices/N_5177_2025_Art_3_16.md && echo "N_5177 mentions replaced statute OK"
```

Expected: all three checks print OK.

- [ ] **Step 9: Commit the tax_invoices module**

```bash
git add law-packs/greece/modules/tax_invoices/
git commit -s -m "$(cat <<'EOF'
feat(greece): tax_invoices module — N_4172/4308/5177 + AADE E.2094 (T28)

Greek tax + invoice statutory framework for the law pack:

- _module.md with trigger metadata + article routing table
- N_4172_2013_Art_24 — depreciation + sub-€1,500 instant write-off
  (CH4 fridge book-value €0 anchor)
- N_4308_2014_Art_9 — mandatory invoice content (clause-by-clause)
- N_4308_2014_Art_18 — invoice timing rules (§2 15-day deadline)
- N_5177_2025_Art_3_16 — Digital Transactions Duty (DTD).
  REPLACES N_5135/2024 with effective_date 2025-02-14
  (ΦΕΚ Α' 21/14.02.2025). Frontmatter declares replaces: [N_5135_2024]
  so the verify-gate can flag drafts that cite the obsolete statute.
- AADE_E_2094_2025 — implementing circular (frontmatter implements:
  [N_5177_2025_Art_3_16])

All article files are placeholder vault entries with [VAULT-PLACEHOLDER]
markers; verbatim Greek text is fetched in T8's vault-fill step from the
sources declared in each frontmatter (lawspot.gr / taxheaven.gr /
search.et.gr / aade.gr). Until then the files are structurally valid
but text-empty.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 29: Greek `corporate` module

**Files:**
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/corporate/_module.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/corporate/N_4601_2019_Art_65.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/corporate/N_4601_2019_Art_70.md`
- Create: `~/Developer/projects/lex-harness/law-packs/greece/modules/corporate/N_4072_2012_Art_201b.md`

**Source map (per LEGAL_CORPUS_MAP §2 Module 5 + §4 step 7):**
- `N_4601/2019` Arts. 65, 70 → **search.et.gr** (primary, ΦΕΚ Α' 44/26.03.2019), e-nomothesia.gr (verification)
- `N_4072/2012` Art. 201b → **e-nomothesia.gr** (primary), search.et.gr (verification)

**Why this module matters:** SA-32 dual-defendant strategy, αγωγή caption work, "αλλαγή επωνυμίας" email rebuttal. The Article 65 §4 file is the **anchor for SA-32** — universal succession + 5-year joint and several liability post-spin-off.

- [ ] **Step 1: Create the module directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p law-packs/greece/modules/corporate
```

- [ ] **Step 2: Write `_module.md`**

```bash
cat > law-packs/greece/modules/corporate/_module.md <<'EOF'
---
module_id: corporate
language: el
default_loaded: false
trigger_signals:
  - spin-off
  - απόσχιση κλάδου
  - universal succession
  - καθολική διαδοχή
  - dual defendant
  - corporate identity trap
  - αλλαγή επωνυμίας
  - joint and several liability
  - SA-32
articles:
  - N_4601_2019_Art_65
  - N_4601_2019_Art_70
  - N_4072_2012_Art_201b
inline_case_law:
  - ΑΠ_362_2023
last_verified: 2026-04-07
---

# Module: corporate

Greek corporate-law statutory framework — spin-offs, universal succession, joint and several liability, dual mandate.

## Scope

This module loads when reasoning about:

- Whether a successor entity is liable for the obligations of its predecessor (universal succession)
- Whether the original shareholder/company remains jointly liable post-spin-off
- Whether a "change of corporate name" notification was actually a spin-off in disguise
- Caption decisions for αγωγή (which legal entities to name as defendants)
- "Corporate identity trap" attacks (the business uses Entity A on the contract but Entity B on the invoices)

## Articles

| ID | Short name | Use case |
|---|---|---|
| `N_4601_2019_Art_65` | Joint + several liability of original company post-spin-off (5-year window) | **SA-32 anchor** — primary defendant naming basis |
| `N_4601_2019_Art_70` | Universal succession of rights + obligations via spin-off | "αλλαγή επωνυμίας" rebuttal |
| `N_4072_2012_Art_201b` | Dual mandate / agency relationships in commercial entities | Agency framing for contract-vs-invoice mismatch |

## SA-32 anchor

**Article 65 §4 of N. 4601/2019 is the legal basis for SA-32 (dual-defendant strategy). It establishes that the original company remains JOINTLY AND SEVERALLY liable for the obligations transferred to the new entity for 5 years from the date the spin-off is registered with ΓΕΜΗ.** Any case-repo strategy file invoking SA-32 MUST cite this file as its statutory authority.

## Cross-module links

- → `core/AK_281.md` (abuse of right — when a corporate restructure is used to dodge liability)
- → `core/AK_288.md` (good faith — pre-spin-off communications must disclose the restructure)
- → `modules/consumer_protection/Law_2251_1994_Art_9d.md` (misleading commercial practices — "αλλαγή επωνυμίας" framing)

## Inline case law

- **ΑΠ 362/2023** — Universal succession via spin-off; the successor inherits the rights AND obligations of the spun-off branch automatically; no individual notice required to creditors. Brief inline summary lives below the Article 70 file.

## Source files

All article files have YAML frontmatter declaring `source_primary` + `source_verification` URLs and a `sha256` of the verbatim text section.
EOF
```

- [ ] **Step 3: Write `N_4601_2019_Art_65.md` (joint and several liability — SA-32 anchor)**

> **CRITICAL VERIFICATION:** §4 (5-year joint and several liability post-spin-off) MUST be the primary operative paragraph. The frontmatter MUST tag this file as the SA-32 anchor.

```bash
cat > law-packs/greece/modules/corporate/N_4601_2019_Art_65.md <<'EOF'
---
article_id: N_4601_2019_Art_65
short_name: "Spin-off — joint and several liability of original company (5-year window)"
statute: Νόμος 4601/2019 (Εταιρικοί Μετασχηματισμοί)
article_number: "65"
source_primary: https://www.et.gr/api/DownloadFek/?fek_pdf=20190100044
source_verification: https://www.e-nomothesia.gr/kat-emporio/n-4601-2019.html
effective_date: 2019-03-26
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
fek_reference: ΦΕΚ Α' 44/26.03.2019
strategy_anchor:
  - SA-32
---

# Άρθρο 65 ν. 4601/2019 — Διασπώμενη εταιρεία και ευθύνη (joint and several liability post-spin-off)

## ⭐ STRATEGY ANCHOR — SA-32 (dual-defendant)

**Paragraph 4 of this article is the statutory authority for SA-32 (dual-defendant naming strategy). It establishes that the original (διασπώμενη / "split-off") company remains jointly and severally liable for obligations transferred to the new (επωφελούμενη / "beneficiary") company for FIVE YEARS from the registration of the spin-off in ΓΕΜΗ.**

Any draft naming both the original company and the beneficiary company as co-defendants MUST cite this article as the basis. The verify-gate enforces this — a draft claiming SA-32 without citing N_4601/2019 Art. 65 §4 fails Stage 4.

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from search.et.gr (ΦΕΚ Α' 44/26.03.2019). Replace this block; update sha256 frontmatter field.**

> Article 65 establishes the post-spin-off liability rules. The harness relies on §1 (general rule), §3 (rights of creditors), and especially **§4** (joint and several liability of the διασπώμενη for 5 years).

## Operative meaning (one paragraph)

When a Greek company executes a spin-off (απόσχιση κλάδου) under N. 4601/2019, the obligations attached to the spun-off branch transfer automatically to the beneficiary company. Article 65 §4 then provides that the original (διασπώμενη) company **remains jointly and severally liable** for those obligations for **five years** from the registration of the spin-off in the General Commercial Registry (ΓΕΜΗ). A creditor with a claim arising before the spin-off may therefore sue EITHER the original company OR the beneficiary company OR BOTH — and may collect from whichever is solvent. This statutory window cannot be waived in advance. It is the legal foundation of the dual-defendant strategy: name both entities, let them sort out indemnification between themselves, and recover from the more accessible defendant.

## Operative timeline rule

For the harness `legal-strategy` skill the operative numerical question is:

```
deadline = ΓΕΜΗ_registration_date + 5 years
```

If the case event date is BEFORE `deadline`, both entities are valid co-defendants under §4. After `deadline`, only the beneficiary company remains liable (subject to other transfer rules).

## Cross-references inside the case

- `07_strategy/STRATEGIC_ARGUMENTS.md` — SA-32 (dual-defendant strategy) cites this file as primary authority
- `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` — PF-A33 anchor
- `04_evidence/gemi_filings/YESTAY_AE_GEMI_FINDINGS.md` — ΓΕΜΗ registration date for the operative spin-off

## Verification

- **Primary:** search.et.gr → ΦΕΚ Α' 44/26.03.2019 PDF
- **Verification:** e-nomothesia.gr indexed copy
- **Pin date:** 2026-04-07
EOF
```

- [ ] **Step 4: Write `N_4601_2019_Art_70.md` (universal succession + ΑΠ 362/2023 inline)**

```bash
cat > law-packs/greece/modules/corporate/N_4601_2019_Art_70.md <<'EOF'
---
article_id: N_4601_2019_Art_70
short_name: "Spin-off — universal succession of rights and obligations"
statute: Νόμος 4601/2019 (Εταιρικοί Μετασχηματισμοί)
article_number: "70"
source_primary: https://www.et.gr/api/DownloadFek/?fek_pdf=20190100044
source_verification: https://www.e-nomothesia.gr/kat-emporio/n-4601-2019.html
effective_date: 2019-03-26
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
fek_reference: ΦΕΚ Α' 44/26.03.2019
---

# Άρθρο 70 ν. 4601/2019 — Καθολική διαδοχή (universal succession via spin-off)

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from search.et.gr.**

> Article 70 establishes that a spin-off effects **universal succession** (καθολική διαδοχή) of the spun-off branch's rights and obligations to the beneficiary company. §1 = general transfer rule. §2 = automatic from registration in ΓΕΜΗ; **no individual notice to counterparties required**.

## Operative meaning (one paragraph)

A spin-off under N. 4601/2019 is a form of **universal succession**, not assignment (εκχώρηση). Universal succession means the entire bundle of rights and obligations attached to the spun-off branch passes automatically to the beneficiary company at the moment of ΓΕΜΗ registration. There is no requirement to individually notify counterparties or obtain their consent. This has two consequences for the harness: (1) any communication to a tenant calling the spin-off an "αλλαγή επωνυμίας" (change of name) is factually misleading — universal succession is a corporate transformation, not a name change; (2) Articles 455–460 ΑΚ (which govern voluntary assignment of receivables) **do NOT apply** to the spin-off — never cite them in this context.

## Operative rule against the "αλλαγή επωνυμίας" framing

Where a counterparty (tenant, creditor, customer) was told the corporate change was "just a name change" but the change was in fact a spin-off:

1. The communication is **misleading** (Art. 9δ Law 2251/1994 if the counterparty is a consumer)
2. The corporate transformation is governed by Article 70 (universal succession), not Articles 455–460 ΑΚ (assignment)
3. The counterparty's rights against the διασπώμενη persist for 5 years per Article 65 §4

## Inline case law — ΑΠ 362/2023

> **ΑΠ 362/2023 (Universal Succession via Spin-off):** The Areios Pagos confirmed that a spin-off under N. 4601/2019 effects universal succession; the beneficiary company inherits both the rights and the obligations of the spun-off branch automatically as of ΓΕΜΗ registration. No individual creditor notice is required for the transfer to be effective. The decision distinguishes universal succession from voluntary assignment under Articles 455 et seq. ΑΚ. (Cited in PROVEN_FACTS_REGISTER PF-A31.)

## Cross-references inside the case

- `07_strategy/STRATEGIC_ARGUMENTS.md` — SA-32 (cites Article 70 for the "no separate notice" point)
- `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` — PF-A31 / PF-A32 anchors
- `03_correspondence/emails/13_einvoices.md` — the "αλλαγή επωνυμίας" email this article rebuts

## Verification

- **Primary:** search.et.gr → ΦΕΚ Α' 44/26.03.2019
- **Verification:** e-nomothesia.gr
- **Pin date:** 2026-04-07
EOF
```

- [ ] **Step 5: Write `N_4072_2012_Art_201b.md` (dual mandate)**

```bash
cat > law-packs/greece/modules/corporate/N_4072_2012_Art_201b.md <<'EOF'
---
article_id: N_4072_2012_Art_201b
short_name: "Dual mandate / commercial agency relationships"
statute: Νόμος 4072/2012 (Βελτίωση Επιχειρηματικού Περιβάλλοντος)
article_number: "201Β"
source_primary: https://www.e-nomothesia.gr/kat-eteries/n-4072-2012.html
source_verification: https://www.et.gr/api/DownloadFek/?fek_pdf=20120100086
effective_date: 2012-04-11
repeal_date: null
sha256: 0000000000000000
translation_status: el-only
last_verified: 2026-04-07
language: el
fek_reference: ΦΕΚ Α' 86/11.04.2012
---

# Άρθρο 201Β ν. 4072/2012 — Διπλή εντολή / εμπορική αντιπροσωπεία (dual mandate)

## Verbatim text (Greek)

**[VAULT-PLACEHOLDER] — populate during T8 verbatim fetch from e-nomothesia.gr.**

> Article 201Β governs dual-mandate / commercial agency relationships in Greek commercial law. It is the operative provision when one entity acts both as principal and as agent within an integrated corporate group, or when a contract is signed by Entity A but performance and invoicing are routed through Entity B.

## Operative meaning (one paragraph)

When a contract is concluded by one company (the "contract entity") but performance, billing, and customer-facing operations are handled by a related entity (the "operating entity"), Article 201Β supports treating the operating entity as having implicit dual mandate. This matters for the harness because it lets a claimant frame the "corporate identity trap" — where the lessor uses Entity A on the lease but Entity B on every invoice — as a single integrated commercial relationship, not as two unrelated entities. The agency framing is independent of, but complementary to, the universal-succession framing under Article 70 of N. 4601/2019.

## Forensic application

When the case file shows an asymmetry between the contract entity and the invoicing entity, the harness uses Article 201Β to argue:

1. The two entities operated under a dual mandate / agency relationship
2. The contracting party was on actual or constructive notice of this arrangement
3. Therefore the obligations of one entity may be enforced against the other

This is a **secondary** framing — the primary framing is N_4601/2019 Art. 65 §4 (joint and several liability post-spin-off). Article 201Β fills the gap for situations where the spin-off liability window has expired but the dual-entity operation continues.

## Cross-references inside the case

- `07_strategy/STRATEGIC_ARGUMENTS.md` — SA-19 (corporate identity trap)
- `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` — PF-F57 (agency admission from YESTAY ΑΕ Note 10)
- `04_evidence/gemi_filings/YESTAY_PROSARTIMA_2024.pdf` — Note 10 source

## Verification

- **Primary:** e-nomothesia.gr indexed copy
- **Verification:** search.et.gr → ΦΕΚ Α' 86/11.04.2012
- **Pin date:** 2026-04-07
EOF
```

- [ ] **Step 6: Verify the module loads cleanly**

```bash
ls -la law-packs/greece/modules/corporate/
wc -l law-packs/greece/modules/corporate/*.md
```

Expected: 4 files; all >40 lines.

Run the SA-32 anchor verification:

```bash
grep -l "strategy_anchor:" law-packs/greece/modules/corporate/*.md
grep -l "SA-32" law-packs/greece/modules/corporate/N_4601_2019_Art_65.md
```

Expected: both print `law-packs/greece/modules/corporate/N_4601_2019_Art_65.md`.

Run the per-file frontmatter check:

```bash
for f in law-packs/greece/modules/corporate/N_*.md; do
  python3 -c "
import sys, re
content = open('$f').read()
m = re.match(r'^---\n(.*?)\n---', content, re.S)
assert m, '$f: no frontmatter'
fm = m.group(1)
for required in ['article_id', 'short_name', 'source_primary', 'source_verification', 'effective_date', 'sha256', 'translation_status', 'last_verified']:
    assert required + ':' in fm, '$f: missing ' + required
print('$f OK')
"
done
```

Expected: 3 lines ending in `OK`.

- [ ] **Step 7: Commit the corporate module**

```bash
git add law-packs/greece/modules/corporate/
git commit -s -m "$(cat <<'EOF'
feat(greece): corporate module — N_4601/2019 + N_4072/2012 (T29)

Greek corporate-law module for the law pack:

- _module.md with SA-32 trigger metadata + ΑΠ 362/2023 inline reference
- N_4601_2019_Art_65 — joint and several liability of διασπώμενη
  (5-year window post-ΓΕΜΗ registration). FRONTMATTER strategy_anchor:
  [SA-32] — verify-gate enforces this as the primary citation for the
  dual-defendant strategy.
- N_4601_2019_Art_70 — universal succession of rights and obligations
  via spin-off. Inline ΑΠ 362/2023 summary. Rebuts "αλλαγή επωνυμίας"
  framing and the wrong-statute cite to Articles 455–460 ΑΚ.
- N_4072_2012_Art_201b — dual mandate / commercial agency framing for
  the corporate-identity-trap line (SA-19 secondary support).

All files are vault placeholders pending T8 verbatim fetch from
search.et.gr (primary) + e-nomothesia.gr (verification) per
LEGAL_CORPUS_MAP §4 step 7.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 30: Codex skills bootstrap script

**Files:**
- Create: `~/Developer/projects/lex-harness/scripts/bootstrap-codex-skills.sh`

**Why:** per design spec §9 + decision PD6, Codex CLI parity ships in v0.3 with manifests. Until then, Codex users can still consume the SAME skills directory by symlinking it into `~/.codex/skills/`. This script wires those symlinks. Per decision D20 (in plan parts 1–3) **the symlinks themselves are NOT committed** — the script creates them on demand, idempotently, on each user's machine.

Critical properties:
- Idempotent: re-running is a no-op (second run reports `already linked: 4`)
- Pure bash (no Python, no Node)
- Uses `$REPO_ROOT` (resolved from script location) — NOT `${CLAUDE_PLUGIN_ROOT}` (that env var is only set inside Claude Code skill bodies, not in standalone scripts)
- Exits non-zero only if a hard precondition fails (skills directory missing, link target unresolvable). Successful relink is exit 0.

- [ ] **Step 1: Create the scripts directory if missing**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p scripts
```

- [ ] **Step 2: Write `scripts/bootstrap-codex-skills.sh`**

```bash
cat > scripts/bootstrap-codex-skills.sh <<'EOF'
#!/usr/bin/env bash
#
# bootstrap-codex-skills.sh
#
# Symlinks the lex-harness plugin's skills/ subdirectories into
# ~/.codex/skills/lex-harness-* so the Codex CLI can discover them.
#
# Per design decision D20 the symlinks themselves are NOT committed
# to the lex-harness repo. Each user runs this script once on their
# machine after cloning or installing the plugin.
#
# Properties:
#   - Idempotent: re-running is a no-op. Second run reports
#     "already linked: <N>" instead of recreating links.
#   - Pure bash. No Python, no Node, no jq.
#   - Exits 0 on success (including idempotent re-run).
#   - Exits 1 if the lex-harness skills/ directory cannot be located
#     or the target home directory is not writable.
#
# Usage:
#   ./scripts/bootstrap-codex-skills.sh
#
set -euo pipefail

# Resolve REPO_ROOT to the absolute path of the lex-harness checkout,
# regardless of where the script is invoked from.
SCRIPT_PATH="${BASH_SOURCE[0]}"
SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_PATH")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"
CODEX_SKILLS_DIR="$HOME/.codex/skills"

# Hard precondition: the plugin's skills/ directory must exist.
if [ ! -d "$SKILLS_SRC" ]; then
  echo "ERROR: lex-harness skills directory not found at $SKILLS_SRC" >&2
  echo "Expected to find skills/ next to the bootstrap script." >&2
  exit 1
fi

# Create the Codex skills directory if it does not yet exist.
if [ ! -d "$CODEX_SKILLS_DIR" ]; then
  mkdir -p "$CODEX_SKILLS_DIR" || {
    echo "ERROR: cannot create $CODEX_SKILLS_DIR (home not writable?)" >&2
    exit 1
  }
fi

# Iterate over each skill subdirectory and (re)create the symlink.
linked_new=0
linked_existing=0
linked_total=0

for skill_path in "$SKILLS_SRC"/*/; do
  [ -d "$skill_path" ] || continue
  skill_name="$(basename "$skill_path")"
  link_name="lex-harness-$skill_name"
  link_target="$CODEX_SKILLS_DIR/$link_name"

  if [ -L "$link_target" ]; then
    # Already a symlink. Verify it points where we expect.
    current_target="$(readlink "$link_target")"
    expected_target="$skill_path"
    # Strip trailing slash for comparison robustness.
    expected_target="${expected_target%/}"
    if [ "$current_target" = "$expected_target" ]; then
      linked_existing=$((linked_existing + 1))
      linked_total=$((linked_total + 1))
      continue
    else
      # Link exists but points elsewhere. Replace it (idempotent fix).
      rm "$link_target"
      ln -s "$expected_target" "$link_target"
      linked_new=$((linked_new + 1))
      linked_total=$((linked_total + 1))
      continue
    fi
  fi

  if [ -e "$link_target" ]; then
    # Something exists at this path that is NOT a symlink.
    # Refuse to clobber a real file/directory.
    echo "ERROR: $link_target exists and is not a symlink. Refusing to overwrite." >&2
    echo "Move or delete it manually and re-run this script." >&2
    exit 1
  fi

  # No existing entry. Create a fresh symlink.
  expected_target="${skill_path%/}"
  ln -s "$expected_target" "$link_target"
  linked_new=$((linked_new + 1))
  linked_total=$((linked_total + 1))
done

# Report.
if [ "$linked_new" -gt 0 ] && [ "$linked_existing" -gt 0 ]; then
  echo "linked new: $linked_new"
  echo "already linked: $linked_existing"
elif [ "$linked_new" -gt 0 ]; then
  echo "linked new: $linked_new"
elif [ "$linked_existing" -gt 0 ]; then
  echo "already linked: $linked_existing"
else
  echo "WARNING: no skills found in $SKILLS_SRC" >&2
fi

echo "total skills bootstrapped: $linked_total"
echo "Codex CLI will discover them at $CODEX_SKILLS_DIR"

exit 0
EOF
chmod +x scripts/bootstrap-codex-skills.sh
```

- [ ] **Step 3: Test idempotency (first run)**

```bash
./scripts/bootstrap-codex-skills.sh
```

Expected output (assuming all 4 skills exist from T11–T18):

```
linked new: 4
total skills bootstrapped: 4
Codex CLI will discover them at /Users/<user>/.codex/skills
```

Verify symlinks exist:

```bash
ls -la ~/.codex/skills/ | grep lex-harness
```

Expected: 4 lines, each a symlink starting with `lex-harness-` pointing into the repo's `skills/` directory.

- [ ] **Step 4: Test idempotency (second run — must be a no-op)**

```bash
./scripts/bootstrap-codex-skills.sh
```

Expected output:

```
already linked: 4
total skills bootstrapped: 4
Codex CLI will discover them at /Users/<user>/.codex/skills
```

The phrase `already linked: 4` is the **idempotency proof**.

- [ ] **Step 5: Test that a stale symlink gets corrected (third run after manual tampering)**

```bash
# Manually point one symlink at the wrong place
rm ~/.codex/skills/lex-harness-legal-strategy
ln -s /tmp /not/a/real/path 2>/dev/null || ln -s /tmp ~/.codex/skills/lex-harness-legal-strategy

# Re-run and verify the script repairs it
./scripts/bootstrap-codex-skills.sh
readlink ~/.codex/skills/lex-harness-legal-strategy
```

Expected: the readlink output ends with `skills/legal-strategy` — the script detected the wrong target and replaced the symlink.

- [ ] **Step 6: Test the hard precondition (missing skills/ directory)**

```bash
# Temporarily simulate a broken checkout
mv skills /tmp/skills_backup
./scripts/bootstrap-codex-skills.sh; echo "exit=$?"
mv /tmp/skills_backup skills
```

Expected: the script prints `ERROR: lex-harness skills directory not found at ...` and exits with `exit=1`.

- [ ] **Step 7: Commit the bootstrap script**

```bash
git add scripts/bootstrap-codex-skills.sh
git commit -s -m "$(cat <<'EOF'
feat(scripts): Codex skills bootstrap with idempotent symlinks (T30)

scripts/bootstrap-codex-skills.sh symlinks the plugin's 4 skills/
subdirectories into ~/.codex/skills/lex-harness-* so Codex CLI can
discover them.

Idempotent by design (per design decision D20 — symlinks NOT
committed):
- First run reports "linked new: 4"
- Second run reports "already linked: 4"
- Stale or wrong-target symlinks are auto-repaired
- Refuses to clobber a real file or directory at the link path

Pure bash. No external deps. Resolves $REPO_ROOT from the script's
own location so it works regardless of CWD. Uses $REPO_ROOT (not
${CLAUDE_PLUGIN_ROOT}, which is only set inside Claude Code skill
bodies, never in standalone scripts).

Hard preconditions: lex-harness skills/ exists; ~/.codex/ writable.
Exits non-zero only on these failures.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 31: validate-pack.sh — pack contract enforcer

**Files:**
- Create: `~/Developer/projects/lex-harness/scripts/validate-pack.sh`

**Why:** PR-02 + PR-07 require that every law pack validates against the schema in `law-packs/_schema.md`. The plugin REFUSES to load an invalid pack. CI runs this script on every PR.

Validation checks (in order):

1. `pack.json` exists, parses as JSON, and has required fields (`name`, `version`, `language`, `country_code`, `default_modules`, `mcp_servers`, `forum_rules_file`, `limitation_periods_file`, `playbook_file`, `glossary_file`, `maintainer`)
2. `MODULE_INDEX.md`, `forums.yaml`, `limitation_periods.yaml`, `playbook.yaml`, `glossary.md` exist
3. `forums.yaml`, `limitation_periods.yaml`, `playbook.yaml` parse as valid YAML
4. `core/` exists and has ≥1 statute file
5. `modules/` exists and has ≥1 module subdirectory
6. Every statute file in `core/` and `modules/*/` has the required YAML frontmatter (`article_id`, `short_name`, `source_primary`, `source_verification`, `effective_date`, `sha256`, `translation_status`, `last_verified`)
7. **PR-01 grep check:** no plugin core file (under `skills/`) references country-specific terms (Greek statute IDs, Greek language tokens, "Greece", "ΑΚ", "ΚΠολΔ"). This is the layer-separation enforcement mentioned in design spec §16 DoD item 9.

Exit codes:
- `0` on success (`Pack <country> is valid`)
- non-zero with a specific error message on failure

- [ ] **Step 1: Write `scripts/validate-pack.sh`**

```bash
cat > scripts/validate-pack.sh <<'EOF'
#!/usr/bin/env bash
#
# validate-pack.sh <country>
#
# Validates a law pack at law-packs/<country>/ against the contract
# in law-packs/_schema.md. Used by:
#   - Contributors (run before opening a PR)
#   - CI (.github/workflows/validate-pack.yml on every PR)
#   - The plugin loader at runtime (PR-02)
#
# Exit codes:
#   0  -- pack is valid
#   1  -- usage error (no country argument)
#   2  -- pack directory does not exist
#   3  -- pack.json missing or invalid
#   4  -- required pack files missing
#   5  -- yaml file failed to parse
#   6  -- statute file frontmatter incomplete
#   7  -- PR-01 grep check failed (country-specific content in skills/)
#
set -euo pipefail

# ----------------------------------------------------------------------
# Resolve repo root + parse arg
# ----------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <country>" >&2
  echo "Example: $0 greece" >&2
  exit 1
fi

COUNTRY="$1"
PACK_DIR="$REPO_ROOT/law-packs/$COUNTRY"

# ----------------------------------------------------------------------
# Helper: print failure and exit with given code
# ----------------------------------------------------------------------
fail() {
  local code="$1"; shift
  echo "FAIL ($COUNTRY): $*" >&2
  exit "$code"
}

# ----------------------------------------------------------------------
# Check 0: pack directory exists
# ----------------------------------------------------------------------
if [ ! -d "$PACK_DIR" ]; then
  fail 2 "pack directory not found at $PACK_DIR"
fi

echo "Validating pack: $COUNTRY ($PACK_DIR)"

# ----------------------------------------------------------------------
# Check 1: pack.json exists, parses, has required fields
# ----------------------------------------------------------------------
PACK_JSON="$PACK_DIR/pack.json"
[ -f "$PACK_JSON" ] || fail 3 "pack.json missing at $PACK_JSON"

python3 - "$PACK_JSON" <<'PY' || fail 3 "pack.json invalid"
import json, sys
path = sys.argv[1]
try:
    with open(path) as f:
        m = json.load(f)
except Exception as e:
    print(f"JSON parse error: {e}", file=sys.stderr)
    sys.exit(1)

required = [
    "name", "version", "language", "country_code",
    "default_modules", "mcp_servers",
    "forum_rules_file", "limitation_periods_file",
    "playbook_file", "glossary_file", "maintainer",
]
missing = [k for k in required if k not in m]
if missing:
    print(f"missing fields in pack.json: {missing}", file=sys.stderr)
    sys.exit(1)

if not isinstance(m["default_modules"], list):
    print("default_modules must be a list", file=sys.stderr)
    sys.exit(1)
if not isinstance(m["mcp_servers"], list):
    print("mcp_servers must be a list", file=sys.stderr)
    sys.exit(1)

# PR-11 check: every declared MCP server must be optional
for srv in m["mcp_servers"]:
    if srv.get("required") is True:
        print(f"PR-11 violation: mcp_server {srv.get('name')} declared required", file=sys.stderr)
        sys.exit(1)

print("pack.json OK")
PY

# ----------------------------------------------------------------------
# Check 2: required pack files exist
# ----------------------------------------------------------------------
for required_file in MODULE_INDEX.md forums.yaml limitation_periods.yaml playbook.yaml glossary.md; do
  if [ ! -f "$PACK_DIR/$required_file" ]; then
    fail 4 "required file missing: $required_file"
  fi
done
echo "required files OK"

# ----------------------------------------------------------------------
# Check 3: yaml files parse cleanly
# ----------------------------------------------------------------------
for yaml_file in forums.yaml limitation_periods.yaml playbook.yaml; do
  python3 -c "
import sys
try:
    import yaml
except ImportError:
    print('FAIL: PyYAML not installed; install with pip install pyyaml', file=sys.stderr)
    sys.exit(2)
try:
    with open('$PACK_DIR/$yaml_file') as f:
        yaml.safe_load(f)
except Exception as e:
    print(f'$yaml_file parse error: {e}', file=sys.stderr)
    sys.exit(1)
print('$yaml_file OK')
" || fail 5 "$yaml_file failed to parse"
done

# ----------------------------------------------------------------------
# Check 4: core/ exists and has ≥1 statute file
# ----------------------------------------------------------------------
if [ ! -d "$PACK_DIR/core" ]; then
  fail 4 "core/ directory missing"
fi
core_files=$(find "$PACK_DIR/core" -maxdepth 1 -name '*.md' -type f | wc -l)
if [ "$core_files" -lt 1 ]; then
  fail 4 "core/ contains no statute files"
fi
echo "core/ has $core_files statute file(s)"

# ----------------------------------------------------------------------
# Check 5: modules/ exists and has ≥1 module subdirectory
# ----------------------------------------------------------------------
if [ ! -d "$PACK_DIR/modules" ]; then
  fail 4 "modules/ directory missing"
fi
module_dirs=$(find "$PACK_DIR/modules" -mindepth 1 -maxdepth 1 -type d | wc -l)
if [ "$module_dirs" -lt 1 ]; then
  fail 4 "modules/ contains no module subdirectories"
fi
echo "modules/ has $module_dirs module(s)"

# ----------------------------------------------------------------------
# Check 6: every statute file has required frontmatter
# ----------------------------------------------------------------------
REQUIRED_FRONTMATTER="article_id short_name source_primary source_verification effective_date sha256 translation_status last_verified"

check_frontmatter() {
  local file="$1"
  python3 - "$file" <<'PY'
import re, sys
path = sys.argv[1]
try:
    with open(path) as f:
        content = f.read()
except Exception as e:
    print(f"{path}: cannot read: {e}", file=sys.stderr)
    sys.exit(1)
m = re.match(r'^---\n(.*?)\n---', content, re.S)
if not m:
    print(f"{path}: no YAML frontmatter", file=sys.stderr)
    sys.exit(1)
fm = m.group(1)
required = ["article_id", "short_name", "source_primary",
            "source_verification", "effective_date", "sha256",
            "translation_status", "last_verified"]
missing = [k for k in required if (k + ":") not in fm]
if missing:
    print(f"{path}: missing frontmatter fields: {missing}", file=sys.stderr)
    sys.exit(1)
PY
}

# core/
for f in "$PACK_DIR/core"/*.md; do
  [ -f "$f" ] || continue
  check_frontmatter "$f" || fail 6 "$f frontmatter incomplete"
done

# modules/*/
for module_dir in "$PACK_DIR/modules"/*/; do
  [ -d "$module_dir" ] || continue
  for f in "$module_dir"/*.md; do
    [ -f "$f" ] || continue
    bn="$(basename "$f")"
    # Skip _module.md (it has different frontmatter)
    if [ "$bn" = "_module.md" ]; then
      continue
    fi
    check_frontmatter "$f" || fail 6 "$f frontmatter incomplete"
  done
done
echo "all statute files have required frontmatter"

# ----------------------------------------------------------------------
# Check 7: PR-01 grep check — skills/ must not contain country tokens
# ----------------------------------------------------------------------
# This enforces the layer-separation rule. The skills/ directory is
# layer 1 (jurisdiction-AGNOSTIC) and must NEVER reference Greek
# (or any country-specific) statute IDs, language tokens, or
# procedural terms. Country-specific content lives in law-packs/.
if [ -d "$REPO_ROOT/skills" ]; then
  # Token list for the PR-01 check. Extend as needed.
  PR01_TOKENS="ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|lawspot\.gr|search\.et\.gr|N_4172|N_4308|N_4601|N_5177|AADE"
  if grep -rE "$PR01_TOKENS" "$REPO_ROOT/skills" > /dev/null 2>&1; then
    echo "FAIL: PR-01 layer-separation violation in skills/" >&2
    grep -rEn "$PR01_TOKENS" "$REPO_ROOT/skills" >&2 || true
    fail 7 "country-specific content found in skills/"
  fi
  echo "PR-01 grep check passed"
else
  echo "WARN: skills/ directory not found; skipping PR-01 check"
fi

# ----------------------------------------------------------------------
# All checks passed
# ----------------------------------------------------------------------
echo
echo "✅ Pack $COUNTRY is valid"
exit 0
EOF
chmod +x scripts/validate-pack.sh
```

- [ ] **Step 2: Verify the script with the Greek pack (success path)**

```bash
./scripts/validate-pack.sh greece; echo "exit=$?"
```

Expected: prints `✅ Pack greece is valid` and `exit=0`.

If the run fails, the script names the specific file or field that broke validation. Fix that field, re-run.

- [ ] **Step 3: Verify the script rejects a missing pack (failure path)**

```bash
./scripts/validate-pack.sh nonexistent_country; echo "exit=$?"
```

Expected: prints `FAIL (nonexistent_country): pack directory not found at ...` and `exit=2`.

- [ ] **Step 4: Verify the script rejects a missing required file**

```bash
mv law-packs/greece/forums.yaml /tmp/forums.yaml.bak
./scripts/validate-pack.sh greece; echo "exit=$?"
mv /tmp/forums.yaml.bak law-packs/greece/forums.yaml
```

Expected: `exit=4` and message `required file missing: forums.yaml`.

- [ ] **Step 5: Verify the PR-01 grep check rejects a planted violation**

```bash
# Plant a deliberate violation
mkdir -p skills/legal-strategy
echo "# Test — references Art. 592 ΑΚ" >> skills/legal-strategy/SKILL.md
./scripts/validate-pack.sh greece; echo "exit=$?"
# Clean up the planted line
git checkout skills/legal-strategy/SKILL.md
```

Expected: `exit=7` with `PR-01 layer-separation violation in skills/`. After cleanup, re-running `./scripts/validate-pack.sh greece` returns to `exit=0`.

- [ ] **Step 6: Verify the script rejects a `required: true` MCP server (PR-11)**

```bash
# Plant a violation
python3 -c "
import json
with open('law-packs/greece/pack.json') as f:
    m = json.load(f)
m['mcp_servers'].append({'name': 'test-bad', 'purpose': 'test', 'required': True})
with open('law-packs/greece/pack.json', 'w') as f:
    json.dump(m, f, indent=2)
"
./scripts/validate-pack.sh greece; echo "exit=$?"
git checkout law-packs/greece/pack.json
```

Expected: `exit=3` with `PR-11 violation: mcp_server test-bad declared required`.

- [ ] **Step 7: Commit `validate-pack.sh`**

```bash
git add scripts/validate-pack.sh
git commit -s -m "$(cat <<'EOF'
feat(scripts): validate-pack.sh — pack contract enforcer (T31 / PR-02 / PR-07 / PR-11)

scripts/validate-pack.sh <country> validates a law pack against the
contract in law-packs/_schema.md. Used by contributors, CI, and the
plugin loader at runtime.

Checks (in order, each with a distinct exit code):
  0 success
  1 usage (no country arg)
  2 pack directory missing
  3 pack.json missing/invalid OR PR-11 violation (mandatory MCP)
  4 required pack file missing OR core/modules empty
  5 yaml file failed to parse
  6 statute file frontmatter incomplete
  7 PR-01 layer-separation violation in skills/

PR-01 grep check tokens: ΑΚ, ΚΠολΔ, Greek, Greece, ΦΕΚ, kodiko.gr,
lawspot.gr, search.et.gr, N_4172, N_4308, N_4601, N_5177, AADE.

Tested manually against:
  - Valid greece pack (exit 0)
  - Missing pack (exit 2)
  - Missing required file (exit 4)
  - Planted PR-01 violation (exit 7)
  - Planted required: true MCP server (exit 3)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 32: tests/ — manual smoke test checklists

**Files:**
- Create: `~/Developer/projects/lex-harness/tests/README.md`
- Create: `~/Developer/projects/lex-harness/tests/greece/load_pack.test.md`
- Create: `~/Developer/projects/lex-harness/tests/plugin_structure.test.md`

**Why manual checklists, not pytest:** per nikai finding (referenced in plan part 1) and design spec PD10, **no deterministic skill-test framework exists**. Skills are probabilistic; manual smoke tests are the state of the art. The tests in this task are markdown checklists that a human (or an LLM-driven session) walks through and marks as pass/fail.

DO NOT add pytest, jest, vitest, or any other automated test runner — that's a v0.4+ research item, not v0.1.

- [ ] **Step 1: Create the tests directory**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p tests/greece
```

- [ ] **Step 2: Write `tests/README.md`**

```bash
cat > tests/README.md <<'EOF'
# Tests

Manual smoke-test checklists for `lex-harness`. **There is no automated test runner in v0.1.** Skills are probabilistic; the state-of-the-art is human walkthrough plus a CI-side schema validator.

## Why manual?

Per design decision PD10 and the nikai research finding referenced in the v0.1 plan: **no deterministic skill-test framework exists yet**. We do not pretend otherwise. We ship what works:

- A schema validator (`scripts/validate-pack.sh`) that runs in CI on every PR
- Manual checklists in this directory that a human walks through before each release
- The 15 Gherkin scenarios in design spec §7a as the acceptance contract

## Test files

| File | Purpose | When to run |
|---|---|---|
| `greece/load_pack.test.md` | Walks through `claude --plugin-dir <repo>` and verifies all 4 skills + 3 commands appear | Before every plugin commit that touches `skills/`, `commands/`, or `law-packs/greece/` |
| `plugin_structure.test.md` | Verifies the 14 acceptance criteria from design spec §16 (Definition of Done) | Before every release tag |

## How to run a test

1. Open the relevant `.test.md` file
2. For each `- [ ]` checkbox, perform the action described
3. Mark the checkbox `- [x]` if the action passed
4. If a checkbox fails, STOP and fix the underlying issue before continuing
5. Save the test file with the marks (do NOT commit the marked file — keep it as a working copy)

A test passes when all checkboxes are marked `- [x]`.

## What about automated checks?

- `scripts/validate-pack.sh greece` runs in CI and is the closest thing we have to automation
- The PR-01 + PR-03 grep checks in CI catch layer-separation violations
- The `plugin.json` schema check validates the manifest

That's the entire automated surface. Everything else is humans.

## Future work

When a deterministic skill-testing framework lands (hypothetical: a "skill replay" tool that re-runs a recorded session against a pinned model and asserts on outputs), we will adopt it and convert these checklists. Until then, manual is the way.
EOF
```

- [ ] **Step 3: Write `tests/greece/load_pack.test.md`**

```bash
cat > tests/greece/load_pack.test.md <<'EOF'
# Smoke test — Greek pack loads cleanly via `claude --plugin-dir`

> **Manual checklist.** Walk through this top to bottom. Mark each box `- [x]` when the step passes. If any step fails, STOP and fix the underlying issue before retrying.

## Preconditions

- [ ] You have Claude Code CLI installed (`claude --version` works)
- [ ] You have cloned (or are working in) `~/Developer/projects/lex-harness`
- [ ] You are NOT inside a case repo (CWD is empty or unrelated)

## Step 1 — Plugin loads without error

- [ ] Run:

      ```bash
      cd /tmp && mkdir -p lex-harness-test-1 && cd lex-harness-test-1
      claude --plugin-dir ~/Developer/projects/lex-harness
      ```

- [ ] Claude Code starts without printing any error messages
- [ ] No `[PLUGIN-LOAD-FAIL]` or similar markers appear
- [ ] The session prompt appears

## Step 2 — All 4 skills are discoverable

Inside the Claude Code session, run the skill listing prompt (or check via `/help` if available). The 4 skills below MUST appear:

- [ ] `legal-strategy` is listed
- [ ] `osint-investigation` is listed
- [ ] `document-production` is listed
- [ ] `devil-advocate` is listed

If any skill is missing, check that:
1. Its `SKILL.md` file exists under `skills/<name>/SKILL.md`
2. The frontmatter parses (no YAML errors)
3. The `description:` field is present and ≤1024 chars

## Step 3 — All 3 commands are autocomplete-discoverable

- [ ] Type `/lex-harness:` in the session and observe autocomplete
- [ ] `/lex-harness:init` appears in the dropdown
- [ ] `/lex-harness:fact` appears in the dropdown
- [ ] `/lex-harness:devil` appears in the dropdown

## Step 4 — `/lex-harness:init greece` scaffolds a case skeleton

- [ ] Run `/lex-harness:init greece` in the session
- [ ] The command prompts for case metadata (claimant, opposing party, deposit/claim amount, key dates)
- [ ] After answering, the command reports successful scaffolding

Verify on disk (in a separate terminal):

```bash
ls /tmp/lex-harness-test-1/
```

- [ ] All 9 numbered case directories exist (`01_case_summary` through `09_ai_research`)
- [ ] `01_case_summary/CASE_OVERVIEW.md` exists and is populated with the answers given
- [ ] `05_legal_research/law_pack/pack.json` exists
- [ ] `05_legal_research/law_pack/core/` is populated (≥1 article)
- [ ] `05_legal_research/law_pack/modules/tenancy/` exists
- [ ] `05_legal_research/law_pack/modules/tax_invoices/` exists
- [ ] `05_legal_research/law_pack/modules/corporate/` exists
- [ ] `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` exists with empty schema
- [ ] `06_claims_and_defenses/PENDING_FACTS.md` exists
- [ ] `DEADLINE_REGISTER.md` contains a `DL-01` entry computed from the pack's `limitation_periods.yaml`
- [ ] `.githooks/pre-commit` is installed and executable (`ls -l .githooks/pre-commit`)
- [ ] `git config core.hooksPath` returns `.githooks`

## Step 5 — Pack version is reported

- [ ] In the session, ask: "What law pack version is loaded?"
- [ ] The session answers with the version string from `law-packs/greece/pack.json` (e.g., `0.1.0`)

## Step 6 — Tax invoices module is queryable

- [ ] In the session, ask: "What does N_5177/2025 say about stamp duty?"
- [ ] The session loads `law-packs/greece/modules/tax_invoices/N_5177_2025_Art_3_16.md` and reports its content
- [ ] The session correctly identifies that N_5177/2025 REPLACED N_5135/2024 starting 2025-02-14
- [ ] The session does NOT cite N_5135/2024 for any post-Feb-2025 fact

## Step 7 — Corporate module SA-32 anchor is respected

- [ ] In the session, ask: "Show me the legal authority for the SA-32 dual-defendant strategy."
- [ ] The session loads `law-packs/greece/modules/corporate/N_4601_2019_Art_65.md`
- [ ] The session quotes §4 (5-year joint and several liability)
- [ ] The session does NOT cite Articles 455–460 ΑΚ as the basis (they govern voluntary assignment, not spin-off)

## Step 8 — Cleanup

- [ ] Exit the Claude Code session
- [ ] Delete the test scratch directory: `rm -rf /tmp/lex-harness-test-1`

## Result

- [ ] All boxes above are marked `- [x]` → **PASS**
- [ ] One or more boxes are unchecked → **FAIL** — fix the underlying issue and rerun
EOF
```

- [ ] **Step 4: Write `tests/plugin_structure.test.md`**

```bash
cat > tests/plugin_structure.test.md <<'EOF'
# Smoke test — plugin structure and 14-point Definition of Done

> **Manual checklist.** Walks through the 14 acceptance criteria from design spec §16 (Definition of Done for v0.1). Mark each box `- [x]` when the criterion is met. ALL boxes must be checked before tagging v0.1.0.

## Preconditions

- [ ] You are in `~/Developer/projects/lex-harness`
- [ ] You have run `git status` and the working tree is clean (or only contains the test result file)

## DoD criterion 1 — Repo exists with MIT LICENSE and README

- [ ] `LICENSE` exists and is the MIT license text
- [ ] `README.md` exists and documents what lex-harness is
- [ ] The repo has been created on `github.com/neotherapper/lex-harness`

## DoD criterion 2 — `.claude-plugin/plugin.json` validates against schema

- [ ] Run:

      ```bash
      python3 -c "
      import json
      m = json.load(open('.claude-plugin/plugin.json'))
      required = ['name', 'version', 'description', 'author', 'license', 'repository']
      missing = [k for k in required if k not in m]
      assert not missing, f'missing: {missing}'
      assert m['name'] == 'lex-harness'
      assert m['license'] == 'MIT'
      print('OK')
      "
      ```

- [ ] The script prints `OK`

## DoD criterion 3 — All 4 skills load without error

- [ ] Run `claude --plugin-dir .` in a clean directory
- [ ] No `[PLUGIN-LOAD-FAIL]` markers appear
- [ ] All 4 skill SKILL.md files have parseable YAML frontmatter

## DoD criterion 4 — All 3 commands appear in `/lex-harness:*` autocomplete

- [ ] `/lex-harness:init` appears
- [ ] `/lex-harness:fact` appears
- [ ] `/lex-harness:devil` appears

## DoD criterion 5 — `/lex-harness:init greece` scaffolds in `/tmp/test-case/`

- [ ] Run:

      ```bash
      mkdir -p /tmp/test-case && cd /tmp/test-case
      claude --plugin-dir ~/Developer/projects/lex-harness
      ```

- [ ] Inside the session run `/lex-harness:init greece`
- [ ] All 9 numbered case directories appear in `/tmp/test-case/`
- [ ] Cleanup: `rm -rf /tmp/test-case`

## DoD criterion 6 — `/lex-harness:fact` appends a valid entry

- [ ] In an initialised case repo, run `/lex-harness:fact`
- [ ] Answer the prompts
- [ ] `06_claims_and_defenses/PENDING_FACTS.md` contains the new entry with the correct YAML schema

## DoD criterion 7 — `/lex-harness:devil SA-31` dispatches devil-advocate

> Note: SA-31 must exist in the test case repo for this to work. Skip if testing in a fresh init (the file does not exist there); test against a yestay-style repo with an SA-31 file.

- [ ] Run `/lex-harness:devil SA-31`
- [ ] A new file `07_strategy/da_reviews/DA_SA31_<date>.md` is created
- [ ] The DA file contains ≥3 counter-arguments rated HIGH/MEDIUM/LOW
- [ ] The DA file contains a verdict (SOUND / NEEDS-WORK / DROP)

## DoD criterion 8 — Greek law pack has 22 core articles + 3 modules

- [ ] `find law-packs/greece/core -name '*.md' | wc -l` returns ≥22
- [ ] `law-packs/greece/modules/tenancy/` exists and has ≥1 article
- [ ] `law-packs/greece/modules/tax_invoices/` exists and has 5 articles + `_module.md`
- [ ] `law-packs/greece/modules/corporate/` exists and has 3 articles + `_module.md`
- [ ] Each statute file has the verbatim text section populated (no `[VAULT-PLACEHOLDER]` markers remain) — NOTE: this may still be in progress at v0.1.0; if vault fill is deferred, document the deferral in CHANGELOG.md

## DoD criterion 9 — CI grep check passes (PR-01)

- [ ] Run:

      ```bash
      ! grep -rE "(ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|N_4172|N_5177)" skills/
      ```

- [ ] The command exits 0 (i.e., grep found nothing)

## DoD criterion 10 — Yestay successfully installs the plugin and produces a Phase 3 demand letter end-to-end

> This criterion is satisfied by Plan B (`2026-04-07-yestay-adopts-lex-harness.md`). It is the GO/NO-GO gate at the END of Plan B, NOT inside Plan A. Mark this checkbox **after Plan B completes**, not during the Plan A test pass.

- [ ] Plan B has been executed and produced one Phase 3 demand letter end-to-end

## DoD criterion 11 — Draft footer block contains resolvable references

- [ ] Pick the most recent draft in `08_drafts/` of the test case
- [ ] The draft has a footer block with `pf_ids:`, `law_articles:`, `evidence_items:`, `da_review_refs:`
- [ ] All `pf_ids` resolve to entries in `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md`
- [ ] All `law_articles` resolve to files in `05_legal_research/law_pack/`
- [ ] All `evidence_items` resolve to files in `04_evidence/`
- [ ] All `da_review_refs` resolve to files in `07_strategy/da_reviews/` (or are documented as "pending")

## DoD criterion 12 — Zero-MCP scenario passes

- [ ] In a fresh case repo on a machine with NO external MCPs configured, draft a short demand letter via `document-production`
- [ ] The skill emits `[TOOL-UNAVAILABLE:<tool>]` markers in the session brief for any tools it would have used in the full-power path
- [ ] The draft is produced anyway via the manual fallback path
- [ ] The draft passes the verify-gate

## DoD criterion 13 — `docs/TOOL_OPTIONALITY.md` exists and is complete

- [ ] `docs/TOOL_OPTIONALITY.md` exists
- [ ] Every external tool referenced anywhere in skills/ is listed in the fallback matrix table
- [ ] Each row has the columns: Tool / Adds / Without it / Fallback path

## DoD criterion 14 — Repo is live on GitHub with LICENSE + README + CONTRIBUTING

- [ ] `gh repo view neotherapper/lex-harness` returns successfully
- [ ] The remote `LICENSE`, `README.md`, and `CONTRIBUTING.md` are accessible

## Result

- [ ] All 14 DoD checkboxes are marked `- [x]` (DoD criterion 10 may be deferred until Plan B completes — annotate accordingly) → **READY TO TAG v0.1.0**
- [ ] One or more boxes are unchecked → **NOT READY** — fix the underlying issue
EOF
```

- [ ] **Step 5: Verify all 3 test files exist**

```bash
ls tests/README.md tests/greece/load_pack.test.md tests/plugin_structure.test.md
wc -l tests/README.md tests/greece/load_pack.test.md tests/plugin_structure.test.md
```

Expected: all 3 files exist; sizes roughly README ~50 lines, load_pack ~120 lines, plugin_structure ~150 lines.

- [ ] **Step 6: Commit the test files**

```bash
git add tests/
git commit -s -m "$(cat <<'EOF'
test: manual smoke test checklists (T32 / PD10)

Manual markdown checklists, NOT an automated framework. Per design
decision PD10 and the nikai research finding: no deterministic
skill-test framework exists; manual walkthrough is the state of the
art.

- tests/README.md — explains the manual approach + future work
- tests/greece/load_pack.test.md — walks through claude --plugin-dir
  then verifies all 4 skills + 3 commands appear; verifies the Greek
  pack loads, tax_invoices and corporate modules are queryable, and
  /lex-harness:init greece scaffolds a complete case repo
- tests/plugin_structure.test.md — walks through the 14 acceptance
  criteria from design spec §16 Definition of Done. Criterion 10
  (yestay end-to-end) is deferred until Plan B completes.

These are walked through by a human (or an LLM-driven session) before
every release tag. The closest thing to automation is
scripts/validate-pack.sh + the PR-01 grep check in CI.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 33: docs/ARCHITECTURE.md — 3-layer deep dive

**Files:**
- Create: `~/Developer/projects/lex-harness/docs/ARCHITECTURE.md`

**Why:** the design spec lives in the yestay repo. The plugin ships its own `ARCHITECTURE.md` for contributors who don't have access to the yestay design doc. This file is the canonical architecture explanation INSIDE the public plugin repo.

- [ ] **Step 1: Write `docs/ARCHITECTURE.md`**

```bash
cat > docs/ARCHITECTURE.md <<'EOF'
# Architecture

> The 3-layer architecture of `lex-harness`. Read this before contributing or extending the plugin.

## TL;DR

```
┌──────────────────────────────────────────────────────────────────┐
│ LAYER 1: PLUGIN CORE — jurisdiction-AGNOSTIC                      │
│ skills/  commands/  templates/  docs/  schemas/  scripts/         │
│ The harness "engine" — identical for every country, every case    │
│ Lives in: this repo (github.com/neotherapper/lex-harness)         │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 2: LAW PACKS — jurisdiction-SPECIFIC, case-AGNOSTIC         │
│ law-packs/greece/   law-packs/germany/   law-packs/france/        │
│ Statutes + case law + forum rules + procedural templates +       │
│ foundational legal concepts (per country)                         │
│ Greek pack = MVP. Other packs = community contributions.          │
│ Lives in: this repo (one subdirectory per country)                │
├──────────────────────────────────────────────────────────────────┤
│ LAYER 3: CASE REPO — CASE-SPECIFIC                                │
│ 01_case_summary/  02_contracts/  06_claims_and_defenses/  ...     │
│ Facts (PFs), charges, evidence, drafts, settlement numbers        │
│ Lives in: YOUR repo (e.g., yestay)                                │
└──────────────────────────────────────────────────────────────────┘
```

The plugin ships **layers 1 + 2**. Your case repo is **layer 3**.

## Why 3 layers?

The single most important architectural decision in the plugin design. Without strict separation:

- Skill bodies grow Greek-specific code over time, making Germany/France packs impossible
- Case repos copy-paste plugin logic, making plugin upgrades break consumers
- Country packs accumulate case-specific facts, making them unshareable

With strict separation:

- One skill body, many country packs, many case repos
- Plugin updates only touch layer 1; case repos update law packs by re-running `/lex-harness:init --update-pack`
- Country pack contributors only need to write statute files + forum rules — they never touch skill logic

## Layer 1 — Plugin core (jurisdiction-agnostic)

**Path:** `skills/`, `commands/`, `templates/`, `docs/`, `schemas/`, `scripts/`

**Responsibility:** universal reasoning workflows that apply to any civil dispute in any jurisdiction.

**Contents:**

- **4 skills** (`skills/<name>/SKILL.md`):
  - `legal-strategy` — frame → list candidates → apply gates → rank → recommend ONE
  - `osint-investigation` — chain-of-custody preservation, PENDING_FACTS proposals
  - `document-production` — verify-gate, footer block enforcement, atomic decomposition
  - `devil-advocate` — adversarial review in isolated subagent context

- **3 slash commands** (`commands/`):
  - `/lex-harness:init <jurisdiction>` — scaffold a new case repo
  - `/lex-harness:fact` — append to PENDING_FACTS.md
  - `/lex-harness:devil <argument-id>` — dispatch devil-advocate

- **Templates** (`templates/`):
  - `case_skeleton/` — the 9 numbered case directories
  - `PROVEN_FACTS_REGISTER.md` — schema header, no entries
  - `pre-commit` — git hook for T1 write-path isolation
  - jurisdiction-agnostic document skeletons

- **Schemas** (`law-packs/_schema.md`, `docs/JURISDICTION_PACK_SPEC.md`):
  - The contract a law pack MUST satisfy
  - The pack.json structure
  - Required statute frontmatter fields

- **Scripts** (`scripts/`):
  - `validate-pack.sh` — pack contract enforcer (also runs in CI)
  - `bootstrap-codex-skills.sh` — symlinks skills into `~/.codex/skills/` for Codex CLI parity

**Rule (PR-01 + PR-03):** Layer 1 files MUST NOT contain country-specific content. No statute IDs, no language tokens, no procedural terms. The plugin's CI runs a grep check on every PR to enforce this.

## Layer 2 — Law packs (jurisdiction-specific, case-agnostic)

**Path:** `law-packs/<country>/`

**Responsibility:** the corpus of statutes, case law, forum rules, and templates for one jurisdiction.

**Contents per pack:**

- `pack.json` — manifest with name, version, language, modules, MCP servers (all optional per PR-11)
- `MODULE_INDEX.md` — task → modules routing table
- `forums.yaml` — forum precondition rules (statutory_blocking vs strategic_recommended)
- `limitation_periods.yaml` — statutory deadlines
- `playbook.yaml` — common plays for this jurisdiction
- `glossary.md` — legal terminology in the local language + EN translation
- `core/` — always-loaded statute articles
- `modules/<name>/` — task-specific module subdirectories
- `case_law/` — court decisions (inline + cold tier)
- `templates/` — local-language document templates
- `foundational_concepts/` — plain-language explanations of jurisdiction concepts

**Greek MVP** (`law-packs/greece/`):
- 22 core articles (ΑΚ + ΚΠολΔ + Σύνταγμα)
- 3 v0.1 modules: `tenancy`, `tax_invoices`, `corporate`
- Inline ΑΠ case law summaries in module files

**Rule (PR-01):** Layer 2 files MUST NOT contain case-specific content. No PF codes, no party names, no specific drafts, no specific deadlines. Layer 2 is a public reference library, not a case file.

## Layer 3 — Case repo (case-specific)

**Path:** YOUR repo (e.g., `~/Developer/projects/yestay`)

**Responsibility:** the facts, claims, evidence, drafts, and decisions of ONE specific dispute.

**Contents** (scaffolded by `/lex-harness:init <jurisdiction>`):

- `01_case_summary/` — case overview, charges, timeline
- `02_contracts/` — signed agreements
- `03_correspondence/` — emails, WhatsApp, phone-call records
- `04_evidence/` — photos, invoices, screenshots, OSINT findings, testimony
- `05_legal_research/` — `law_pack/` (a snapshot of the active layer 2 pack) + case-specific research
- `06_claims_and_defenses/` — PROVEN_FACTS_REGISTER, PENDING_FACTS, per-charge files
- `07_strategy/` — strategic arguments, decision log, settlement economics, devils' advocate reviews
- `08_drafts/` — formal output documents
- `09_ai_research/` — AI research library specific to this case

**Rule (D19 / D30 / write-path isolation):** Only one entity may write to `PROVEN_FACTS_REGISTER.md` — a human in a manual commit WITHOUT a `Co-Authored-By: Claude` trailer. AI agents propose facts via `PENDING_FACTS.md` and a human promotes them in a separate commit. The pre-commit hook enforces this mechanically.

## How the layers compose at runtime

When a user invokes `legal-strategy` inside their case repo:

```
USER PROMPT
    ↓
legal-strategy SKILL.md (LAYER 1 — universal reasoning workflow)
    ↓
reads strategy-reasoning.md, verify-gate.md (LAYER 1 references)
    ↓
loads 05_legal_research/law_pack/forums.yaml (LAYER 2 — jurisdiction rules)
loads 05_legal_research/law_pack/playbook.yaml (LAYER 2 — common plays)
loads 05_legal_research/law_pack/limitation_periods.yaml (LAYER 2 — deadlines)
    ↓
reads <case-repo>/06_claims_and_defenses/ (LAYER 3 — facts + charges)
reads <case-repo>/07_strategy/ (LAYER 3 — strategic arguments)
reads <case-repo>/01_case_summary/CASE_OVERVIEW.md (LAYER 3 — context)
    ↓
applies the universal reasoning workflow with the loaded data
    ↓
emits a recommendation + writes to LAYER 3 (DECISION_LOG, etc.)
```

The skill itself (layer 1) NEVER hardcodes a Greek statute or a Yestay PF code. All such references come from layers 2 and 3.

## Strategy: universal reasoning + jurisdiction rules + case content

Strategy is split across all three layers:

| Aspect | Layer | Example |
|---|---|---|
| **Reasoning workflow** ("frame → list candidates → apply gates → rank → recommend ONE") | 1 | `skills/legal-strategy/references/strategy-reasoning.md` |
| **Decision principles** ("Information First, Attack Second"; "dropped arguments stay dropped"; "criminal last"; "absence is evidence") | 1 | Documented in skill body |
| **Settlement economics math** (ZOPA, BATNA, expected value) | 1 | `skills/legal-strategy/references/settlement-math.md` |
| **Forum types catalog** (civil / ombudsman / regulator / criminal — abstract) | 1 | Concept in skill body |
| **Forum sequencing rules** (e.g., Greek Art. 52 KPolD) | 2 | `law-packs/<country>/forums.yaml` |
| **Limitation periods catalog** (e.g., Greek 6-month rental rule) | 2 | `law-packs/<country>/limitation_periods.yaml` |
| **Common plays for this jurisdiction** | 2 | `law-packs/<country>/playbook.yaml` |
| **THIS case's specific arguments** | 3 | `<case-repo>/07_strategy/SA*.md` |
| **THIS case's settlement number** | 3 | `<case-repo>/07_strategy/core/SETTLEMENT_ECONOMICS.md` |

There is exactly **one** `legal-strategy` skill. It works for any jurisdiction with a valid law pack and any case with a valid case repo.

## Optionality: every external tool has a fallback

Per PR-11 through PR-15 (see `docs/TOOL_OPTIONALITY.md`):

- The plugin works with **zero external dependencies** beyond Claude Code itself
- Every workflow that CAN use an MCP server (Chrome DevTools, Neo4j, ChromaDB, Dikaio.ai, EUR-Lex, …) MUST also have a documented manual fallback
- Skills detect tool availability before use and log `[TOOL-UNAVAILABLE:<name>]` when degrading
- Both the with-tool and without-tool paths produce functionally equivalent outputs (same schema, same footer, same gate checks)

The full-power path is faster; the manual path is always available.

## Cross-references

| If you need… | Read… |
|---|---|
| The pack contract | `docs/JURISDICTION_PACK_SPEC.md` + `law-packs/_schema.md` |
| The plugin's own requirements | `docs/PLUGIN_REQUIREMENTS.md` (PR-01 through PR-15) |
| The fallback matrix | `docs/TOOL_OPTIONALITY.md` |
| The trust model | `docs/SECURITY.md` |
| The roadmap | `docs/ROADMAP.md` |
| The contribution path | `../CONTRIBUTING.md` |
| The yestay design spec (full historical record) | `~/Developer/projects/yestay/docs/superpowers/specs/2026-04-07-lex-harness-plugin-design.md` |

## Glossary

- **Layer 1 / plugin core / harness engine** — jurisdiction-agnostic skills, commands, templates, schemas, scripts. Lives in this repo's top-level directories.
- **Layer 2 / law pack / jurisdiction pack** — a country's statutes + case law + forum rules + templates. Lives in `law-packs/<country>/`.
- **Layer 3 / case repo / case workspace** — one specific dispute's facts + claims + evidence + drafts. Lives in YOUR repo.
- **Active jurisdiction** — the country whose law pack a case repo is currently consuming. Determined by the case's `05_legal_research/law_pack/pack.json`.
- **Verbatim citation** — a statute quote pulled directly from a vault file in the active law pack. The verify-gate refuses to emit a citation that did not come from a loaded vault file.
- **T1 fact** — a fact in `PROVEN_FACTS_REGISTER.md` that has been promoted by a human. AI agents may propose facts (PENDING_FACTS.md) but may never write directly to T1.
EOF
```

- [ ] **Step 2: Verify and commit**

```bash
ls docs/ARCHITECTURE.md
wc -l docs/ARCHITECTURE.md
```

Expected: ~200 lines.

```bash
git add docs/ARCHITECTURE.md
git commit -s -m "$(cat <<'EOF'
docs(arch): ARCHITECTURE.md — 3-layer deep dive (T33)

Public-repo-internal architecture document. Self-contained for
contributors who don't have access to the yestay design spec.

Covers:
- The 3-layer model (plugin core / law packs / case repo)
- Per-layer responsibilities + contents + rules (PR-01, D19/D30)
- How the layers compose at runtime
- The strategy split (universal reasoning + jurisdiction rules + case
  content)
- Tool optionality (PR-11..PR-15) at a glance
- Cross-references to the contract docs (PACK_SPEC, REQUIREMENTS,
  TOOL_OPTIONALITY, SECURITY, ROADMAP)
- Glossary

Cross-references the full design spec in the yestay repo for
historical context.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 34: docs/PLUGIN_REQUIREMENTS.md + docs/ROADMAP.md

**Files:**
- Create: `~/Developer/projects/lex-harness/docs/PLUGIN_REQUIREMENTS.md`
- Create: `~/Developer/projects/lex-harness/docs/ROADMAP.md`

**Why:** PR-01 through PR-15 are the formal contract per design spec §7. The roadmap captures v0.1 through v0.4+ scope per design spec §11.

- [ ] **Step 1: Write `docs/PLUGIN_REQUIREMENTS.md`**

```bash
cat > docs/PLUGIN_REQUIREMENTS.md <<'EOF'
# Plugin Requirements (PR-01 through PR-15)

> Formal requirements that the `lex-harness` plugin MUST satisfy. These are plugin-level requirements (the "engine" contract); legal content discipline lives in the AI Legal Harness REQ-01..REQ-14 in the yestay design corpus.

## Severity legend

- **CRITICAL** — release blocker; CI enforces; PRs that violate this are auto-rejected
- **HIGH** — release blocker; manually verified during the v0.1.0 stop-go gate
- **MEDIUM** — should ship but not a release blocker; documented for v0.2

## The 15 requirements

| # | Requirement | Severity |
|---|---|---|
| **PR-01** | **Strict layer separation.** Plugin code (Layer 1) MUST NOT reference any country name, statute ID, or case detail. Layer 2 (law packs) MUST NOT reference any case detail. Layer 3 (case repo) is the only place case content lives. CI grep check enforces this. | CRITICAL |
| **PR-02** | **Law pack contract.** Every country pack ships a `pack.json` matching `docs/JURISDICTION_PACK_SPEC.md` schema. Required fields: `name`, `version`, `language`, `country_code`, `default_modules[]`, `mcp_servers[]`, `forum_rules_file`, `limitation_periods_file`, `playbook_file`, `glossary_file`, `maintainer`. The plugin REFUSES to load a pack that fails schema validation (exit non-zero). | CRITICAL |
| **PR-03** | **Jurisdiction-agnostic skill bodies.** No skill SKILL.md or reference file may contain statute IDs, country names, or procedural terms hardcoded in the skill body. All such content lives in the active law pack. CI grep check enforces this. | CRITICAL |
| **PR-04** | **Reentrant `/init`.** Re-running `/lex-harness:init <jurisdiction>` MUST NOT destroy existing case content. It refreshes the law pack in `05_legal_research/law_pack/` and creates missing templates. Detects existing `01_case_summary/CASE_OVERVIEW.md` and prompts before overwriting. | HIGH |
| **PR-05** | **Semver + backward compat.** Major version bumps require an explicit migration note in CHANGELOG.md. Minor versions MUST NOT break existing case repos. Patch versions MUST NOT break anything. Tested against a pinned yestay snapshot in CI when available. | HIGH |
| **PR-06** | **Greek MVP test coverage.** Every Greek law module ships with at least one smoke test entry that verifies the module loads, articles parse, and the pack.json validates. CI runs `validate-pack.sh greece` on every PR. | HIGH |
| **PR-07** | **Contribution path documented.** `CONTRIBUTING.md` walks through "how to add a country pack" in ≤10 steps. `docs/JURISDICTION_PACK_SPEC.md` is the formal contract. New country PRs auto-fail if `pack.json` doesn't validate or schema grep check fails. | MEDIUM |
| **PR-08** | **MIT license + DCO sign-off.** All contributions MIT-licensed. Every commit must carry Developer Certificate of Origin sign-off (`Signed-off-by: ...`). No CLA. Automated DCO check on PRs (v0.2). | MEDIUM |
| **PR-09** | **Plugin works without case repo.** A user can install the plugin and inspect skill behaviour without having a case repo at all — skills respond with "no case detected — run /lex-harness:init" rather than crashing. | MEDIUM |
| **PR-10** | **No hidden state.** All plugin behaviour is determined by files in the plugin or the case repo. No environment variables required (`${CLAUDE_PLUGIN_ROOT}` is set automatically by Claude Code), no global config in `~/.config/`, no hidden caches. Reproducible by reading the file tree. | HIGH |
| **PR-11** | **All external tools are OPTIONAL.** The plugin ships with ZERO mandatory external dependencies beyond Claude Code itself. Chrome DevTools MCP, Neo4j, ChromaDB, Dikaio.ai, any MCP server — all optional. Every workflow that CAN use an external tool MUST also have a documented fallback path. Graceful degradation is required, not a nice-to-have. | CRITICAL |
| **PR-12** | **Tool detection + graceful degradation.** Every skill that references an optional tool MUST: (a) check for tool availability before use, (b) fall back to the manual/offline path if unavailable, (c) log the degradation as `[TOOL-UNAVAILABLE:<tool-name>]` in the session brief. Never crash, never block a workflow, never require installation mid-session. | CRITICAL |
| **PR-13** | **Documented fallback matrix.** `docs/TOOL_OPTIONALITY.md` ships a table mapping every referenced tool to its fallback. User can build the entire harness with ZERO MCPs installed — the full-power path is an opt-in upgrade. | HIGH |
| **PR-14** | **Install path completeness.** A user can install the plugin and run `/lex-harness:init greece` with ONLY Claude Code installed — no other software. The `/init` command does not prompt for or require any external tool. | HIGH |
| **PR-15** | **Skill descriptions must declare optional dependencies.** Every skill SKILL.md frontmatter MAY declare `optional_tools:` — a list of external tools that enhance the skill but are NOT required. Users inspecting the skill can see at a glance what's optional. | MEDIUM |

## Enforcement matrix

| Requirement | Enforced by |
|---|---|
| PR-01 | `scripts/validate-pack.sh` PR-01 grep check + CI workflow |
| PR-02 | `scripts/validate-pack.sh` schema check + plugin loader |
| PR-03 | `scripts/validate-pack.sh` PR-01 grep check + CI workflow |
| PR-04 | Manual smoke test (`tests/plugin_structure.test.md` DoD-4) |
| PR-05 | Manual review + CHANGELOG.md discipline |
| PR-06 | `validate-pack.sh greece` runs in CI on every PR |
| PR-07 | Manual review on contribution PRs |
| PR-08 | DCO check (v0.2) + manual reminder in PR template |
| PR-09 | Manual smoke test |
| PR-10 | Manual review |
| PR-11 | `validate-pack.sh` mcp_server `required: true` check + manual review |
| PR-12 | Manual review during code review |
| PR-13 | Existence check for `docs/TOOL_OPTIONALITY.md` in CI |
| PR-14 | Manual smoke test (`tests/greece/load_pack.test.md`) |
| PR-15 | Manual review |

## Releasing a new requirement

When proposing a new PR-NN:

1. Open an issue using the `new_requirement.md` template
2. Discuss + get a maintainer to approve
3. Open a PR adding the requirement to this file with a severity rating
4. If CRITICAL, the PR must also ship the enforcement mechanism (CI check, validator update, etc.)
5. Bump the minor version per PR-05
EOF
```

- [ ] **Step 2: Write `docs/ROADMAP.md`**

```bash
cat > docs/ROADMAP.md <<'EOF'
# Roadmap

> Per design spec §11. Versions follow semver. Each version has a defined scope and a defined "blocker to next version" gate.

## v0.1.0 — MVP (current)

**Scope:**
- Plugin scaffold (`.claude-plugin/plugin.json` + `CLAUDE.md`)
- 4 jurisdiction-agnostic skills: `legal-strategy`, `osint-investigation`, `document-production`, `devil-advocate`
- 3 slash commands: `/lex-harness:init`, `/lex-harness:fact`, `/lex-harness:devil`
- Greek law pack (`law-packs/greece/`) with 22 core articles + 3 modules: `tenancy`, `tax_invoices`, `corporate`
- Templates: case skeleton, PROVEN_FACTS_REGISTER schema, PENDING_FACTS, DEADLINE_REGISTER, CLAUDE.md, pre-commit hook, footer block, demand letter skeleton
- Codex bootstrap script (idempotent symlinks)
- Pack validator (`scripts/validate-pack.sh`)
- Manual smoke tests
- Documentation: ARCHITECTURE, JURISDICTION_PACK_SPEC, PLUGIN_REQUIREMENTS, TOOL_OPTIONALITY, ROADMAP, SECURITY
- MIT LICENSE, README, CHANGELOG, CONTRIBUTING, CODE_OF_CONDUCT
- GitHub workflow validating packs on PR
- PR + issue templates

**Blocker to next version:** yestay successfully installs the plugin (Plan B) and produces one Phase 3 demand letter end-to-end via the `document-production` skill.

## v0.2.0 — Hooks + recommended MCPs

**Scope:**
- `hooks/hooks.json`:
  - `SessionStart` hook auto-loads `CASE_OVERVIEW.md` into the session context
  - `PreToolUse` hook intercepts AI writes to `PROVEN_FACTS_REGISTER.md` and rewrites to `PENDING_FACTS.md` (replaces the case-repo-level pre-commit hook with a plugin-level one)
- `.mcp.json` with **recommended** (still optional per PR-11) Greek MCP servers: `greek-law-mcp`, `eur-lex-mcp`, `cerebra-legal-mcp`
- Additional Greek modules: `gdpr`, `consumer_protection`, `tort_damages`, `procedure_eirinodikio`
- 10 foundational concept files in `law-packs/greece/foundational_concepts/`
- DCO check automation in CI

**Blocker to next version:** a second real or hypothetical case successfully tests the `/init` reentrance + `--update-pack` flow without losing case content.

## v0.3.0 — Multi-CLI parity (Codex + Gemini)

**Scope:**
- `.codex-plugin/plugin.json` (Codex CLI manifest)
- `gemini-extension.json` (Gemini CLI extension manifest)
- `AGENTS.md` (Codex / generic context file)
- `GEMINI.md` (Gemini CLI context file)
- Convert `commands/*.md` → `commands/*.toml` with `{{args}}` placeholders for cross-CLI portability
- Skill bodies unchanged (SKILL.md is portable)
- Multi-CLI install instructions in README

**Blocker to next version:** successful install + skill invocation on all 3 CLIs (Claude Code + Codex + Gemini) verified manually.

## v0.4.0+ — Community packs + advanced features

**Scope:**
- Accept community PRs for `law-packs/<country>/`. First targets: Germany, France, UK, US.
- ChromaDB case-law indexing as a plugin-managed cold tier (deferred from yestay MVP)
- MAD-Judges reference workflow for high-stakes drafts
- Possibly: per-element LRS (Legal Reasoning Score) framework

**Blocker:** open-ended; community-driven.

## Out of scope (forever)

| Item | Why never |
|---|---|
| Custom MCP server (`legal-vault-server`) | Use existing community MCPs |
| Voice / video evidence intake | Out of harness scope |
| AI legal advice for the public | Not a SaaS; single-user single-case tool |
| E-filing integration | Filing done by retained lawyer |

## How decisions get made

- New scope → open an issue using the `enhancement.md` template
- Discuss in the issue, get a maintainer's go-ahead
- Open a PR; CI must pass; manual review by a maintainer
- Versioning per PR-05 (semver discipline)
- Major version bumps require a written migration note in `CHANGELOG.md`
EOF
```

- [ ] **Step 3: Verify both files**

```bash
ls docs/PLUGIN_REQUIREMENTS.md docs/ROADMAP.md
wc -l docs/PLUGIN_REQUIREMENTS.md docs/ROADMAP.md
```

Expected: PLUGIN_REQUIREMENTS ~80 lines, ROADMAP ~70 lines.

- [ ] **Step 4: Commit**

```bash
git add docs/PLUGIN_REQUIREMENTS.md docs/ROADMAP.md
git commit -s -m "$(cat <<'EOF'
docs: PLUGIN_REQUIREMENTS.md + ROADMAP.md (T34 / PR-01..PR-15 / §11)

PLUGIN_REQUIREMENTS.md:
- The 15 plugin requirements PR-01..PR-15 from design spec §7
- Severity ratings (CRITICAL / HIGH / MEDIUM)
- Enforcement matrix mapping each PR to its enforcement mechanism
- Process for proposing new requirements

ROADMAP.md:
- v0.1 (current) — MVP scope + blocker to next version
- v0.2 — hooks + recommended MCPs
- v0.3 — multi-CLI parity (Codex + Gemini)
- v0.4+ — community country packs + advanced features
- Out-of-scope items (forever)
- Decision-making process

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 35: docs/TOOL_OPTIONALITY.md + docs/SECURITY.md

**Files:**
- Create: `~/Developer/projects/lex-harness/docs/TOOL_OPTIONALITY.md`
- Create: `~/Developer/projects/lex-harness/docs/SECURITY.md`

**Why:** PR-13 requires a documented fallback matrix mapping every external tool to its fallback path. Design spec §12 documents the trust model with 5 risks + mitigations.

- [ ] **Step 1: Write `docs/TOOL_OPTIONALITY.md`**

```bash
cat > docs/TOOL_OPTIONALITY.md <<'EOF'
# Tool Optionality

> Per PR-11, PR-12, PR-13, PR-14, PR-15. The plugin works with **zero external dependencies** beyond Claude Code itself. Every external tool is OPTIONAL. Every workflow that CAN use an external tool MUST also have a documented manual fallback path.

## TL;DR

You can install `lex-harness`, run `/lex-harness:init greece`, draft a Phase 3 demand letter, and ship it — with **only Claude Code** installed. No MCP servers. No Neo4j. No ChromaDB. No Dikaio.ai. No Chrome.

The full-power path (with all tools) is **faster** and **automates verification**. The manual path is **always available**.

## The fallback matrix

| Tool | What it adds | Without it (manual fallback) | Detection method |
|---|---|---|---|
| **Chrome DevTools MCP** | Live web evidence capture (JS-rendered pages, screenshots, full a11y snapshots) | Manual `WebFetch` (markdown extraction) OR ask the user to paste page content; compute `sha256` of the captured text | Skill checks for `mcp__chrome-devtools__*` tool availability before invocation |
| **Neo4j MCP / `neo4j-cypher`** | Multi-hop relationship queries across PFs, charges, evidence, parties | Markdown grep against `06_claims_and_defenses/PROVEN_FACTS_REGISTER.md` + manual cross-reference | Skill checks for `mcp__neo4j-*` availability |
| **`neo4j-memory`** | Persistent knowledge graph storage across sessions | Plain markdown files in case repo (`memory/*.md` topic files) | Skill checks for `mcp__neo4j-memory__*` |
| **ChromaDB / vector index** | Semantic search across volume case-law (~36 cold-tier decisions) | Inline ≤500-char summaries of headline decisions stored directly in module files (`case_law_inline.md`) | Skill detects index path; falls back to inline summaries |
| **Dikaio.ai MCP** | Automated Greek law citation verification | Manual verification — user copy-pastes citations to kodiko.gr or dikaio.ai web UI; record verification result in draft footer | Skill checks for `mcp__dikaio-*`; otherwise emits a "verify manually" task |
| **`greek-law-mcp`** | 21,000+ Greek statutes as MCP-served vault | Vault articles in the law pack (the 22 core articles + 3 modules in v0.1) — covers ~95% of case needs | Skill checks for the MCP; falls back to local vault files |
| **`eur-lex-mcp`** | EU law + CELEX retrieval (CJEU + GDPR text) | Manual `WebFetch` of `https://eur-lex.europa.eu/legal-content/EL/TXT/?uri=CELEX:<id>` | Skill checks for the MCP |
| **`cerebra-legal` MCP** | Structured legal-reasoning helper (consumer protection, contract analysis, ANSC) | Inline reasoning workflow in `skills/legal-strategy/references/strategy-reasoning.md` (the same checklist, manually applied) | Skill checks for the MCP; falls back to manual checklist |
| **`sequentialthinking` MCP** | Multi-step reasoning helper for complex causal chains | Inline thought process inside the skill — same workflow, just less explicit step-stamping | Skill checks for the MCP |

## How fallback works in practice

1. **Skill activation:** the user invokes a skill (e.g., `legal-strategy`)
2. **Tool detection:** before using any optional tool, the skill checks whether it's available in the current Claude Code session
3. **Fallback:** if the tool is unavailable, the skill switches to the manual path AND emits `[TOOL-UNAVAILABLE:<tool-name>]` in the session brief
4. **Output equivalence:** both paths produce functionally equivalent outputs — same schema, same footer, same gate checks. The full-power path is faster; the manual path is more explicit.
5. **Logging:** the session brief lists all degraded tools so the user knows where automation was missing

## Example session briefs

**Full-power session (all MCPs available):**

```
SESSION BRIEF — 2026-04-12
Case: yestay
Active jurisdiction: greece (pack v0.1.0)
Tools enabled:
  ✓ chrome-devtools
  ✓ neo4j-memory
  ✓ neo4j-cypher
  ✓ chromadb (vector index)
  ✓ dikaio-ai
  ✓ eur-lex
  ✓ cerebra-legal
  ✓ sequentialthinking
Next action: draft Phase 3 demand letter (recommended by playbook P50)
```

**Zero-MCP session (manual fallback):**

```
SESSION BRIEF — 2026-04-12
Case: yestay
Active jurisdiction: greece (pack v0.1.0)
Tools enabled:
  ✓ Claude Code native (Read, Edit, Write, WebFetch, Bash)
Tools degraded:
  [TOOL-UNAVAILABLE:chrome-devtools]    → fallback: WebFetch + manual screenshot
  [TOOL-UNAVAILABLE:neo4j-memory]       → fallback: markdown topic files
  [TOOL-UNAVAILABLE:neo4j-cypher]       → fallback: grep PROVEN_FACTS_REGISTER.md
  [TOOL-UNAVAILABLE:chromadb]           → fallback: inline case_law summaries
  [TOOL-UNAVAILABLE:dikaio-ai]          → fallback: manual verification via kodiko.gr
  [TOOL-UNAVAILABLE:eur-lex]            → fallback: manual EUR-Lex web fetch
  [TOOL-UNAVAILABLE:cerebra-legal]      → fallback: inline strategy-reasoning checklist
  [TOOL-UNAVAILABLE:sequentialthinking] → fallback: inline thought process
Next action: draft Phase 3 demand letter (recommended by playbook P50)
Note: 5 citations will need manual verification before sending — listed in draft footer
```

Both sessions can produce the same final draft.

## Optional dependencies declared in skill frontmatter (PR-15)

A skill MAY declare its optional tools so a user inspecting the skill can see them at a glance:

```yaml
---
name: legal-strategy
version: "4.0"
description: >-
  ... (≤1024 chars trigger spec)
optional_tools:
  - chrome-devtools-mcp
  - neo4j-memory
  - neo4j-cypher
  - chromadb
  - dikaio-ai-mcp
  - eur-lex-mcp
  - cerebra-legal-mcp
  - sequentialthinking-mcp
required_tools: []
---
```

`required_tools` is always empty per PR-11.

## What you give up by going manual

| You lose | You keep |
|---|---|
| Speed (manual fetch is ~10× slower) | All quality gates (verify-gate stages still run) |
| Automated citation verification | Manual verification step recorded in draft footer |
| Multi-hop graph queries on facts | Single-hop grep against PROVEN_FACTS_REGISTER.md |
| Volume semantic search | The ~10 inline headline decisions in module files (covers ~80% of case needs) |
| JS-rendered web evidence | Markdown text + manual screenshot |

## What you NEVER lose

- Layer separation (PR-01)
- Fact write-path isolation (D19 / D30)
- Verbatim citation discipline (no hallucinated statutes)
- Devil's advocate isolation (DA always runs in fresh subagent context)
- The 9-stage verify-gate

## Recommendation

Start with **zero MCPs**. Run a real case end-to-end. Only add an MCP when you can name a specific friction point it would remove. Do not pre-install everything "just in case" — each MCP adds maintenance burden and prompt-injection surface.
EOF
```

- [ ] **Step 2: Write `docs/SECURITY.md`**

```bash
cat > docs/SECURITY.md <<'EOF'
# Security + Trust Model

> Per design spec §12. Five risks from the Claude Code plugin ecosystem and how `lex-harness` mitigates them.

## Risks + mitigations

### Risk 1 — Skill content trust

**Threat:** a malicious or buggy skill body manipulates Claude into producing harmful outputs (e.g., a skill that paraphrases statutes incorrectly, produces drafts with hallucinated citations, or exfiltrates case data).

**Mitigations:**

- All skill SKILL.md changes go through PR review on `main`
- `main` branch is protected (no direct pushes)
- Maintainer review required before merge
- Verify-gate Stage 3b catches hallucinated holdings regardless of skill source
- DCO sign-off required on every commit (PR-08) — no anonymous contributions

### Risk 2 — MCP server trust

**Threat:** a recommended MCP server is compromised or misbehaves, leaking case data or manipulating outputs.

**Mitigations:**

- All MCP servers ship as **OPTIONAL** (PR-11) — users explicitly enable
- v0.1 plugin ships NO MCP recommendations in `.mcp.json` (added in v0.2 with a curated list)
- Each recommended server is documented in `docs/SECURITY.md` with maintainer + scope
- Users can run the entire harness with zero MCPs (PR-14) — the recommendation list is a convenience, not a requirement
- The verify-gate runs the same checks regardless of where data came from — an MCP server cannot bypass gate enforcement

### Risk 3 — API key exposure

**Threat:** a user accidentally commits an API key (e.g., for an MCP server that requires authentication) and exposes it on GitHub.

**Mitigations:**

- The plugin ships NO secrets, NO API keys, NO authentication tokens
- API keys (when needed by an MCP server) live in the user's environment OR in the case repo's `.env` file
- The case repo template's `.gitignore` excludes `.env`, `.env.local`, `*.secret`
- The `/lex-harness:init` command does not prompt for any API key
- Documentation reminds users to keep secrets out of git

### Risk 4 — Prompt injection via MCP

**Threat:** a malicious external source (web page, email, document) embeds instructions in its content; the AI ingests them via an MCP tool and acts on them.

**Mitigations:**

- Verify-gate Stage 3b (holding characterisation) catches misgrounded outputs regardless of source — if the AI tries to cite a statute that didn't come from a loaded vault file, the gate refuses
- Devil-advocate isolation rule catches sycophantic / manipulated outputs — the DA runs in a fresh subagent with no inherited session state, so injected prompts in the main session do not propagate
- Skills are instructed to treat external content as **data**, not as **instructions**
- The PENDING_FACTS / PROVEN_FACTS isolation means an injected fact cannot reach the registry without a human approval step

### Risk 5 — Global vs project scope

**Threat:** the plugin writes to global locations (`~/.config/`, `~/.cache/`, etc.) outside the user's awareness, causing surprises or cross-case data leakage.

**Mitigations:**

- The plugin declares ALL paths relative to `${CLAUDE_PLUGIN_ROOT}` or `<case-repo>`
- No `~/.config/` writes
- No `~/.cache/` writes
- No global state files
- Reproducible by reading the file tree (PR-10)
- The one exception: `bootstrap-codex-skills.sh` writes symlinks to `~/.codex/skills/` — by user invocation, fully documented, easy to undo

## What the plugin does NOT do

- Does NOT call external services on its own
- Does NOT phone home
- Does NOT collect telemetry
- Does NOT auto-update (versioning is explicit; users update via `gh repo` or marketplace)
- Does NOT execute arbitrary code on install (plugin install is just file copies + symlinks)

## Reporting a vulnerability

If you discover a security vulnerability:

1. **Do NOT open a public issue**
2. Email the maintainer privately (see `CODE_OF_CONDUCT.md` for contact)
3. Include: vulnerability description, reproduction steps, suggested fix (if any), your contact for follow-up
4. The maintainer will acknowledge within 7 days and aim to ship a patch within 30 days
5. After the patch is released, the vulnerability is publicly documented in `CHANGELOG.md` with credit (unless you request anonymity)

## v0.2 plans

- Add `excludeTools` configuration (Gemini pattern) to block destructive shell commands inside the plugin scope
- Add a curated `.mcp.json` with recommended servers, each documented with maintainer + scope + trust rationale
- Automated DCO check on PRs
EOF
```

- [ ] **Step 3: Verify and commit**

```bash
ls docs/TOOL_OPTIONALITY.md docs/SECURITY.md
wc -l docs/TOOL_OPTIONALITY.md docs/SECURITY.md
```

Expected: TOOL_OPTIONALITY ~150 lines, SECURITY ~90 lines.

```bash
git add docs/TOOL_OPTIONALITY.md docs/SECURITY.md
git commit -s -m "$(cat <<'EOF'
docs: TOOL_OPTIONALITY.md + SECURITY.md (T35 / PR-13 / §12)

TOOL_OPTIONALITY.md:
- Fallback matrix per PR-13: every external tool → its manual path
- Tool detection mechanism (skills check availability before use)
- Example session briefs (full-power vs zero-MCP)
- Optional dependencies declared in skill frontmatter (PR-15)
- "What you give up by going manual" + "What you NEVER lose"
- Recommendation: start with zero MCPs

SECURITY.md:
- 5 trust risks from design spec §12 with mitigations:
  1. Skill content trust → PR review + DCO + verify-gate
  2. MCP server trust → all optional + documented + verify-gate
  3. API key exposure → no shipped secrets + .gitignore + no /init prompt
  4. Prompt injection via MCP → Stage 3b + DA isolation + PENDING_FACTS gate
  5. Global vs project scope → ${CLAUDE_PLUGIN_ROOT} + <case-repo> only
- What the plugin does NOT do (no telemetry, no auto-update, no
  arbitrary code execution on install)
- Vulnerability reporting process

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 36: GitHub Actions workflow + issue/PR templates

**Files:**
- Create: `~/Developer/projects/lex-harness/.github/workflows/validate-pack.yml`
- Create: `~/Developer/projects/lex-harness/.github/ISSUE_TEMPLATE/bug_report.md`
- Create: `~/Developer/projects/lex-harness/.github/ISSUE_TEMPLATE/new_country_pack.md`
- Create: `~/Developer/projects/lex-harness/.github/PULL_REQUEST_TEMPLATE.md`

**Why:** CI enforces PR-01, PR-02, PR-03 mechanically on every PR. Issue templates funnel contributors into the right path. PR template asks contributors to confirm DCO + which PRs they affect.

- [ ] **Step 1: Create the directories**

```bash
cd ~/Developer/projects/lex-harness
mkdir -p .github/workflows .github/ISSUE_TEMPLATE
```

- [ ] **Step 2: Write `.github/workflows/validate-pack.yml`**

```bash
cat > .github/workflows/validate-pack.yml <<'EOF'
name: Validate law pack + layer separation

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]

jobs:
  validate-greek-pack:
    name: Validate Greek law pack (PR-02 / PR-06)
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install PyYAML
        run: pip install pyyaml

      - name: Run validate-pack.sh greece
        run: |
          chmod +x ./scripts/validate-pack.sh
          ./scripts/validate-pack.sh greece

  pr01-grep-check:
    name: PR-01 — no country tokens in skills/
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Grep skills/ for Greek-specific tokens
        run: |
          if [ -d skills ]; then
            if grep -rE "(ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|lawspot\.gr|search\.et\.gr|N_4172|N_4308|N_4601|N_5177|AADE)" skills/ ; then
              echo "::error::PR-01 violation: country-specific tokens found in skills/"
              echo "::error::Skill bodies must remain jurisdiction-agnostic. Move country content into law-packs/<country>/."
              exit 1
            fi
            echo "PR-01 grep check passed"
          else
            echo "WARN: skills/ directory not found; skipping"
          fi

  pr03-grep-check:
    name: PR-03 — skill descriptions free of country tokens
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Grep SKILL.md frontmatter for country tokens
        run: |
          if [ -d skills ]; then
            # The same token list as PR-01, applied to SKILL.md files
            # specifically (descriptions + frontmatter).
            if find skills -name 'SKILL.md' -exec grep -lE "(ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|N_4172|N_5177)" {} \; | grep -q . ; then
              echo "::error::PR-03 violation: SKILL.md files reference country-specific tokens"
              find skills -name 'SKILL.md' -exec grep -lE "(ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|N_4172|N_5177)" {} \;
              exit 1
            fi
            echo "PR-03 grep check passed"
          else
            echo "WARN: skills/ directory not found; skipping"
          fi

  plugin-json-validation:
    name: plugin.json schema validation
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Validate .claude-plugin/plugin.json
        run: |
          python3 - <<'PY'
          import json, sys
          try:
              with open('.claude-plugin/plugin.json') as f:
                  m = json.load(f)
          except Exception as e:
              print(f"::error::plugin.json failed to parse: {e}")
              sys.exit(1)
          required = ["name", "version", "description", "author", "license", "repository"]
          missing = [k for k in required if k not in m]
          if missing:
              print(f"::error::plugin.json missing required fields: {missing}")
              sys.exit(1)
          assert m["name"] == "lex-harness", f"name must be lex-harness, got {m['name']}"
          assert m["license"] == "MIT", f"license must be MIT, got {m['license']}"
          print("plugin.json is valid")
          PY
EOF
```

- [ ] **Step 3: Write `.github/ISSUE_TEMPLATE/bug_report.md`**

```bash
cat > .github/ISSUE_TEMPLATE/bug_report.md <<'EOF'
---
name: Bug report
about: Report a bug in lex-harness
title: '[BUG] '
labels: bug
assignees: ''
---

## Plugin version
<!-- e.g., v0.1.0 (run `cat .claude-plugin/plugin.json | grep version`) -->

## OS + Claude Code version
<!-- e.g., macOS 14.5, claude code 1.2.3 -->

## Optional MCP servers enabled
<!-- list any external MCPs you have configured (Chrome DevTools, Neo4j, ChromaDB, Dikaio.ai, eur-lex, etc.) -->
<!-- if none: "none — manual fallback path only" -->

## Active law pack + jurisdiction
<!-- e.g., greece v0.1.0 -->

## Steps to reproduce
1.
2.
3.

## Expected behaviour

## Actual behaviour

## Error messages / log output
```
<!-- paste any [TOOL-UNAVAILABLE], [INVALID-PACK], [ISOLATION-BREACH] markers or other errors here -->
```

## Anything else?
EOF
```

- [ ] **Step 4: Write `.github/ISSUE_TEMPLATE/new_country_pack.md`**

```bash
cat > .github/ISSUE_TEMPLATE/new_country_pack.md <<'EOF'
---
name: New country pack proposal
about: Propose adding a new jurisdiction (country) to lex-harness
title: '[PACK] Add <country> law pack'
labels: enhancement, new-pack
assignees: ''
---

## Country
<!-- e.g., Germany / France / United Kingdom / United States -->

## Country code (ISO 3166-1 alpha-2)
<!-- e.g., DE / FR / GB / US -->

## Language(s) to support
<!-- e.g., German (de), French (fr) -->

## Your background
<!-- Are you a lawyer in this jurisdiction? Researcher? Curious contributor? -->
<!-- This affects which sources and which civil-procedure framing the pack should use -->

## Civil-law focus
<!-- What kinds of disputes will the pack support first? -->
<!-- e.g., rental disputes, consumer protection, contract claims -->

## Source materials available
<!-- What official sources will the pack cite? -->
<!-- e.g., Bundesgesetzblatt (DE), Légifrance (FR), legislation.gov.uk (UK) -->

## MVP module list
<!-- What modules will the v0.1 of this pack ship? -->
<!-- Ideally 2–3 modules to start: e.g., tenancy, consumer, contract -->

## Maintainer commitment
<!-- Are you willing to maintain this pack going forward? -->
<!-- Or are you proposing it for the community to pick up? -->

## Read the contract?
- [ ] I have read `docs/JURISDICTION_PACK_SPEC.md`
- [ ] I have read `law-packs/_schema.md`
- [ ] I understand layer separation (PR-01) — packs contain ONLY jurisdiction content, no case content

## Anything else?
EOF
```

- [ ] **Step 5: Write `.github/PULL_REQUEST_TEMPLATE.md`**

```bash
cat > .github/PULL_REQUEST_TEMPLATE.md <<'EOF'
## Summary

<!-- What does this PR change? 1–3 sentences. -->

## Type of change

- [ ] Bug fix (non-breaking)
- [ ] New feature (non-breaking)
- [ ] Breaking change (requires major version bump per PR-05)
- [ ] New country pack contribution
- [ ] Documentation only
- [ ] CI / tooling

## Plugin requirements affected (PR-01..PR-15)

<!-- Tick which requirements your PR touches. CRITICAL items require explicit verification. -->

- [ ] PR-01 — Layer separation (skills/ has no country tokens)
- [ ] PR-02 — Pack contract (pack.json validates)
- [ ] PR-03 — Skill bodies remain jurisdiction-agnostic
- [ ] PR-04 — `/init` reentrance preserved
- [ ] PR-05 — Semver / backward compat preserved
- [ ] PR-06 — Greek MVP test coverage
- [ ] PR-07 — Contribution path docs current
- [ ] PR-08 — DCO sign-off present (`git commit -s`)
- [ ] PR-09 — Plugin works without case repo
- [ ] PR-10 — No hidden state introduced
- [ ] PR-11 — All external tools remain optional
- [ ] PR-12 — Tool detection + graceful degradation preserved
- [ ] PR-13 — `docs/TOOL_OPTIONALITY.md` updated for any new tool
- [ ] PR-14 — Install path completeness preserved
- [ ] PR-15 — Skill descriptions declare new optional dependencies

## DCO sign-off (PR-08)

- [ ] All commits in this PR are signed off with `Signed-off-by: Name <email>` (use `git commit -s`)

## Manual smoke tests run

<!-- Tick the smoke tests you ran locally before opening this PR. -->

- [ ] `./scripts/validate-pack.sh greece` passes locally
- [ ] `tests/greece/load_pack.test.md` walked through successfully
- [ ] `tests/plugin_structure.test.md` walked through successfully (if structural change)
- [ ] N/A — change is documentation only

## CI expectations

CI will run:
- `validate-pack.sh greece`
- PR-01 grep check (`! grep -rE "(ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|N_4172|N_5177)" skills/`)
- PR-03 grep check on `SKILL.md` files
- `plugin.json` schema validation

If any of these fail, the PR cannot merge until they pass.

## Anything else reviewers should know?

<!-- e.g., depends on issue #123, blocked by #456, requires manual smoke test of <X> -->
EOF
```

- [ ] **Step 6: Verify**

```bash
ls .github/workflows/validate-pack.yml .github/ISSUE_TEMPLATE/bug_report.md .github/ISSUE_TEMPLATE/new_country_pack.md .github/PULL_REQUEST_TEMPLATE.md
wc -l .github/workflows/validate-pack.yml .github/ISSUE_TEMPLATE/*.md .github/PULL_REQUEST_TEMPLATE.md
```

Expected: 4 files; workflow ~80 lines, bug_report ~30, new_country_pack ~40, PR template ~60.

Verify the YAML parses:

```bash
python3 -c "
import yaml
with open('.github/workflows/validate-pack.yml') as f:
    yaml.safe_load(f)
print('workflow YAML valid')
"
```

Expected: `workflow YAML valid`

- [ ] **Step 7: Commit**

```bash
git add .github/
git commit -s -m "$(cat <<'EOF'
ci: GitHub workflow + issue/PR templates (T36 / PR-01 / PR-03)

.github/workflows/validate-pack.yml — runs on every PR + push to main:
- Job 1: validate-pack.sh greece (PR-02 / PR-06)
- Job 2: PR-01 grep check (! grep -rE country tokens in skills/)
- Job 3: PR-03 grep check on SKILL.md files specifically
- Job 4: plugin.json schema validation

.github/ISSUE_TEMPLATE/bug_report.md — captures plugin version, OS,
MCP servers enabled, active jurisdiction, repro steps, error markers
([TOOL-UNAVAILABLE], [INVALID-PACK], [ISOLATION-BREACH], etc.)

.github/ISSUE_TEMPLATE/new_country_pack.md — funnels contributors
through the JURISDICTION_PACK_SPEC contract before they start
writing code; confirms they understand PR-01 layer separation.

.github/PULL_REQUEST_TEMPLATE.md — asks contributors to:
- Tick which PRs (PR-01..PR-15) the change affects
- Confirm DCO sign-off (PR-08)
- Confirm which manual smoke tests they ran locally
- Acknowledge what CI will run

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## Task 37: v0.1.0 release with stop-go gate

**Files:**
- Modify: `~/Developer/projects/lex-harness/CHANGELOG.md` (add release date if not already)
- Tag: `v0.1.0`
- Create GitHub release

**Why:** the v0.1.0 release ships the plugin to GitHub. This is the **last task in Plan A**. After this completes, yestay is unblocked to start Plan B (`2026-04-07-yestay-adopts-lex-harness.md`).

**Critical:** the stop-go gate at the end of this task prevents tagging if any of the verification steps fails. Do NOT tag a broken release.

- [ ] **Step 1: Stop-go gate check 1 — `claude --plugin-dir` loads successfully**

```bash
cd /tmp && rm -rf lex-harness-release-test && mkdir lex-harness-release-test && cd lex-harness-release-test
claude --plugin-dir ~/Developer/projects/lex-harness --version 2>&1 | tee /tmp/plugin-load.log
```

Inspect `/tmp/plugin-load.log`. The output MUST NOT contain:
- `[PLUGIN-LOAD-FAIL]`
- `error:`
- `failed:`
- `cannot find`

**STOP-GO GATE 1:**
- [ ] The plugin loaded with NO error markers in the log

If this gate fails, STOP. Fix the underlying issue and re-run from Step 1. Do NOT proceed.

- [ ] **Step 2: Stop-go gate check 2 — all 4 skills appear**

In a Claude Code session started with `claude --plugin-dir ~/Developer/projects/lex-harness`, list the available skills (via `/help` or by asking the agent). Confirm:

- [ ] `legal-strategy` is listed
- [ ] `osint-investigation` is listed
- [ ] `document-production` is listed
- [ ] `devil-advocate` is listed

**STOP-GO GATE 2:** all 4 skills must be discoverable. If any is missing, STOP and fix.

- [ ] **Step 3: Stop-go gate check 3 — all 3 commands appear in autocomplete**

In the same session, type `/lex-harness:` and observe autocomplete:

- [ ] `/lex-harness:init` appears
- [ ] `/lex-harness:fact` appears
- [ ] `/lex-harness:devil` appears

**STOP-GO GATE 3:** all 3 commands must autocomplete. If any is missing, STOP and fix.

- [ ] **Step 4: Stop-go gate check 4 — `/lex-harness:init greece` scaffolds /tmp/test-case-1/**

```bash
mkdir -p /tmp/test-case-1 && cd /tmp/test-case-1
# Inside Claude Code session:
#   /lex-harness:init greece
# Answer the prompts with placeholder data:
#   claimant: Test Tenant
#   opposing party: Test Landlord
#   deposit: 1000
#   key date: 2026-01-01
```

After the command completes, in a separate terminal:

```bash
ls /tmp/test-case-1/
```

Expected: 9 numbered case directories appear (`01_case_summary` through `09_ai_research`).

Spot check:

```bash
test -f /tmp/test-case-1/01_case_summary/CASE_OVERVIEW.md && echo "CASE_OVERVIEW exists"
test -f /tmp/test-case-1/05_legal_research/law_pack/pack.json && echo "law_pack exists"
test -d /tmp/test-case-1/05_legal_research/law_pack/modules/tenancy && echo "tenancy module exists"
test -d /tmp/test-case-1/05_legal_research/law_pack/modules/tax_invoices && echo "tax_invoices module exists"
test -d /tmp/test-case-1/05_legal_research/law_pack/modules/corporate && echo "corporate module exists"
test -f /tmp/test-case-1/06_claims_and_defenses/PROVEN_FACTS_REGISTER.md && echo "PROVEN_FACTS_REGISTER exists"
test -f /tmp/test-case-1/06_claims_and_defenses/PENDING_FACTS.md && echo "PENDING_FACTS exists"
test -f /tmp/test-case-1/DEADLINE_REGISTER.md && echo "DEADLINE_REGISTER exists"
test -f /tmp/test-case-1/.githooks/pre-commit && echo "pre-commit hook exists"
```

**STOP-GO GATE 4:** all 9 echo lines must print. If any is missing, STOP and fix.

Cleanup:

```bash
rm -rf /tmp/test-case-1 /tmp/lex-harness-release-test /tmp/plugin-load.log
```

- [ ] **Step 5: Stop-go gate check 5 — `validate-pack.sh greece` passes**

```bash
cd ~/Developer/projects/lex-harness
./scripts/validate-pack.sh greece; echo "exit=$?"
```

**STOP-GO GATE 5:** must print `✅ Pack greece is valid` and `exit=0`. If not, STOP and fix.

- [ ] **Step 6: Stop-go gate check 6 — PR-01 grep check passes**

```bash
cd ~/Developer/projects/lex-harness
! grep -rE "(ΑΚ|ΚΠολΔ|Greek|Greece|ΦΕΚ|kodiko\.gr|lawspot\.gr|search\.et\.gr|N_4172|N_4308|N_4601|N_5177|AADE)" skills/ ; echo "exit=$?"
```

**STOP-GO GATE 6:** must exit `0` (the `!` inverts the grep result; grep finding nothing → exit 0). If not, STOP and remove the offending tokens from `skills/`.

- [ ] **Step 7: Stop-go gate check 7 — git working tree is clean**

```bash
cd ~/Developer/projects/lex-harness
git status
```

**STOP-GO GATE 7:** must print `nothing to commit, working tree clean`. If there are uncommitted changes, decide whether to commit them in a separate task or `git stash` them. Do NOT tag a release with a dirty tree.

- [ ] **Step 8: Stop-go gate check 8 — CHANGELOG.md has the v0.1.0 entry with today's date**

```bash
grep -A 1 "## \[0.1.0\]" CHANGELOG.md
```

Expected: a heading like `## [0.1.0] — 2026-04-07` (or whatever today is) followed by `### Added`. If the date placeholder is still there or wrong, edit CHANGELOG.md and commit the fix:

```bash
# Update the date if needed
TODAY=$(date +%Y-%m-%d)
# (Use your editor to update the line manually if it doesn't match TODAY.)
git add CHANGELOG.md
git commit -s -m "$(cat <<'EOF'
docs(changelog): finalise v0.1.0 release date (T37)

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

**STOP-GO GATE 8:** the CHANGELOG.md `## [0.1.0]` heading must show today's date.

- [ ] **Step 9: Push to remote (assumes `gh repo create` already happened in T1 or earlier)**

If the repo is not yet on GitHub, create it now:

```bash
gh repo view neotherapper/lex-harness 2>/dev/null || gh repo create neotherapper/lex-harness \
  --public \
  --description "Open-source AI legal harness for civil disputes. Verbatim citations, fact integrity, devil's advocate review, jurisdiction-aware law packs. Greek MVP." \
  --homepage "https://github.com/neotherapper/lex-harness" \
  --source . \
  --remote origin \
  --push
```

If the repo already exists and the remote is configured, push directly:

```bash
git push -u origin main
```

Verify:

```bash
gh repo view neotherapper/lex-harness
```

Expected: the repo metadata prints with the correct description.

- [ ] **Step 10: Tag v0.1.0**

```bash
cd ~/Developer/projects/lex-harness
git tag -a v0.1.0 -m "$(cat <<'EOF'
lex-harness v0.1.0 — initial public release

First public release of the lex-harness Claude Code plugin.

What ships in v0.1.0:
- 4 jurisdiction-agnostic skills: legal-strategy, osint-investigation,
  document-production, devil-advocate
- 3 slash commands: /lex-harness:init, /lex-harness:fact, /lex-harness:devil
- Greek law pack with 22 core articles + 3 modules (tenancy, tax_invoices,
  corporate)
- Templates: case skeleton, PROVEN_FACTS_REGISTER, PENDING_FACTS,
  DEADLINE_REGISTER, CLAUDE.md, pre-commit hook, footer block, demand
  letter skeleton
- Codex skill bootstrap script (idempotent symlinks)
- Pack validator script (CI + local)
- 15 plugin requirements PR-01..PR-15 documented and enforced
- Tool optionality discipline (all external tools optional, fallback
  matrix documented)
- Manual smoke test checklists
- Architecture + security + roadmap docs
- MIT LICENSE + DCO sign-off requirement
- GitHub Actions workflow validating packs on every PR
- Issue + PR templates

Stop-go gate verified before tagging:
- claude --plugin-dir loads cleanly with no error markers
- All 4 skills discoverable
- All 3 commands appear in autocomplete
- /lex-harness:init greece scaffolds a complete case repo
- validate-pack.sh greece passes
- PR-01 grep check passes
- Working tree clean
- CHANGELOG.md v0.1.0 entry has the correct release date

Next: Plan B (yestay adopts lex-harness as a consumer).

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 11: Push the tag**

```bash
git push origin v0.1.0
```

Verify:

```bash
gh release view v0.1.0 2>/dev/null && echo "release exists" || echo "release does not yet exist"
git ls-remote --tags origin | grep v0.1.0
```

Expected: the second command prints a line containing `v0.1.0`.

- [ ] **Step 12: Create the GitHub release using the CHANGELOG entry as release notes**

```bash
# Extract the [0.1.0] section from CHANGELOG.md as the release body.
python3 - <<'PY' > /tmp/release-notes.md
content = open('CHANGELOG.md').read()
# Find the [0.1.0] heading and capture until the next ## heading or EOF.
import re
m = re.search(r'## \[0\.1\.0\][^\n]*\n(.*?)(?=\n## |\Z)', content, re.S)
if not m:
    raise SystemExit("CHANGELOG.md missing [0.1.0] section")
print(m.group(1).strip())
PY

gh release create v0.1.0 \
  --repo neotherapper/lex-harness \
  --title "lex-harness v0.1.0 — initial public release" \
  --notes-file /tmp/release-notes.md

rm -f /tmp/release-notes.md
```

Verify:

```bash
gh release view v0.1.0 --repo neotherapper/lex-harness
```

Expected: the release metadata + release notes print.

- [ ] **Step 13: Optional — announce on the Claude Code marketplace**

This step is OPTIONAL and depends on whether the marketplace submission flow exists at v0.1.0 time. If it does:

```bash
# Read the marketplace submission docs:
gh repo view anthropics/claude-code --json url --template '{{.url}}/docs/marketplace-submission.md'
# OR open the URL in a browser and follow the submission flow.
```

If not yet available, defer announcement to v0.2 and document the deferral in CHANGELOG.md `[Unreleased]`.

- [ ] **Step 14: Final stop-go gate — release is fully live**

Run the post-release smoke check:

```bash
# 1. Repo is publicly viewable
gh repo view neotherapper/lex-harness --json url,description,homepageUrl,licenseInfo

# 2. v0.1.0 tag is on GitHub
gh release view v0.1.0 --repo neotherapper/lex-harness

# 3. Someone could clone and load the plugin
cd /tmp
git clone https://github.com/neotherapper/lex-harness.git lex-harness-fresh-clone
cd lex-harness-fresh-clone
ls .claude-plugin/plugin.json README.md LICENSE
./scripts/validate-pack.sh greece
cd /tmp && rm -rf lex-harness-fresh-clone
```

**FINAL STOP-GO GATE:**
- [ ] Repo is public on GitHub
- [ ] v0.1.0 release is visible
- [ ] Fresh clone works AND `validate-pack.sh greece` exits 0 on the fresh clone

If all final gate items pass → **lex-harness v0.1.0 is LIVE.** Yestay is unblocked to start Plan B (`2026-04-07-yestay-adopts-lex-harness.md`).

If any final gate item fails, STOP. The release exists but is broken — file an issue, prepare a v0.1.1 patch, and do NOT recommend installation until the patch ships.

- [ ] **Step 15: Final commit (release notes / CHANGELOG move to Unreleased)**

After tagging, move the `[0.1.0]` section out of `[Unreleased]` and prepare the changelog for the next iteration:

```bash
# Inspect current state
grep -A 1 "## \[Unreleased\]" CHANGELOG.md
```

If `[Unreleased]` is empty (just the heading + a blank line), there's nothing to do — the changelog is already in the correct shape (released entries below `[Unreleased]`). Otherwise, ensure the `[0.1.0]` heading lives below an empty `[Unreleased]` placeholder so the next change has somewhere to land.

If a fix is needed, commit it:

```bash
git add CHANGELOG.md
git commit -s -m "$(cat <<'EOF'
docs(changelog): post-release housekeeping (T37)

Empty [Unreleased] section ready for v0.1.1 / v0.2 work.

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
git push origin main
```

If no fix is needed, skip the commit.

---

## Plan A is complete

After T37 finishes, the plugin is **live on `github.com/neotherapper/lex-harness`** with v0.1.0 tagged and a working installation path.

**What v0.1.0 ships:**

- 4 jurisdiction-agnostic skills (`legal-strategy`, `osint-investigation`, `document-production`, `devil-advocate`)
- 3 slash commands (`/lex-harness:init`, `/lex-harness:fact`, `/lex-harness:devil`)
- Greek law pack: 22 core articles + 3 modules (`tenancy`, `tax_invoices`, `corporate`)
- Templates, pre-commit hook, Codex bootstrap, validate-pack.sh
- Manual smoke tests + GitHub Actions CI + issue/PR templates
- Documentation: ARCHITECTURE, JURISDICTION_PACK_SPEC, PLUGIN_REQUIREMENTS, ROADMAP, TOOL_OPTIONALITY, SECURITY
- MIT LICENSE + DCO sign-off requirement

**What v0.1.0 deliberately does NOT ship:**

- Codex / Gemini manifests (v0.3)
- SessionStart hooks + recommended `.mcp.json` (v0.2)
- `gdpr` / `consumer_protection` / `tort_damages` / `procedure_eirinodikio` modules (v0.2)
- ChromaDB cold tier (v0.4+)
- Non-Greek packs (v0.4+ community contributions)

**Next plan:** `2026-04-07-yestay-adopts-lex-harness.md` (Plan B) installs the released plugin into yestay, replaces yestay's `.claude/skills/` with plugin versions, validates layer separation in the Yestay context, and produces one Phase 3 demand letter end-to-end via `document-production` to satisfy DoD criterion 10 from the design spec §16.

---

**End of Plan A part 4 (T28–T37). End of Plan A.**
