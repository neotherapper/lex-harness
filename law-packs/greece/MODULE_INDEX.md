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
