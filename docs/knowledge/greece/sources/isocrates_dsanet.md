---
title: "Isocrates (ΔΣΑ) + DSAnet — Athens Bar Legal Databases"
jurisdiction: greece
source: "https://www.dsanet.gr"
last_verified: "2026-04-08"
---

# Isocrates (ΔΣΑ) + DSAnet — Athens Bar Legal Databases

> dsanet.gr is the domain for the Athens Bar Association's "Ισοκράτης" Τράπεζα Νομικών Πληροφοριών. The domain `dsanet.gr` and the product name "Ισοκράτης" refer to the same system.

## Isocrates (Athens Bar)

> **URL:** https://www.dsanet.gr/
> **Researched:** 2026-03-08 (via Chrome DevTools MCP)
> **Operator:** Δικηγορικός Σύλλογος Αθηνών (Athens Bar Association — ΔΣΑ)
> **Access model:** Member-only (ΔΣΑ lawyers); some sections may be publicly viewable
> **Primary use:** National legislation (codified, full life-cycle) + national case law (all court levels, full text, anonymized)

### Executive Summary

- **Ισοκράτης** is the Athens Bar Association's "Τράπεζα Νομικών Πληροφοριών" (Legal Information Bank)
- Confirmed to contain: **Εθνική Νομοθεσία** (full codified Greek legislation, from founding to today) + **Εθνική Νομολογία** (all court levels, full text, anonymized, with headnotes + summaries + linked provisions)
- Also includes: Interest calculators (default/public/judicial/contractual), court stamp calculator
- Access appears to require ΔΣΑ membership login; the `ΣΥΝΔΕΣΗ` button runs a JavaScript function `connectSites()`
- The main navigation shows "Περιεχόμενα Ισοκράτη" and "Ηλεκτρονικές υπηρεσίες" sub-menus but these resolve to 404 in public browsing
- The site also links to the ΔΣΑ library (`dsalib.gr`) and the Ολομέλεια (Bar Council federation, `olomeleia.gr`)

### Site Overview

Isocrates is the flagship database of the Athens Bar Association, provided to its members. The name "Ισοκράτης" (Isocrates — the ancient Greek orator) is used for this system. It is a well-established database, described as containing "gigantic" numbers of decisions across all Greek courts.

Key differentiator from Qualex and Sakkoulas-Online: Isocrates specifically includes **first-instance court decisions** (Ειρηνοδικείο, Μονομελές/Πολυμελές Πρωτοδικείο) that commercial databases often omit. This is critical for cases where the Ειρηνοδικείο is the likely forum (small claims, tenancy disputes up to €20,000).

The database covers:
1. **National Legislation**: Codified from founding of the Greek state; tracks amendments through the life of each legislative text
2. **National Case Law**: Full text of decisions from:
   - Άρειος Πάγος (Supreme Court)
   - Εφετεία (Courts of Appeal)
   - Πρωτοδικεία (Courts of First Instance) — including Μονομελές
   - **Ειρηνοδικεία** (Peace Courts) — critical for small claims (≤€20,000)
   - Διοικητικά Δικαστήρια (Administrative courts)
   - Each decision: anonymized, with Λήμματα (headnotes), Περίληψη (summary), and linked to statutory provisions

### Access and Registration

- **Primary access**: ΔΣΑ member lawyers via login (`connectSites()` JavaScript function)
- **Email access**: Email link connects to `mail.dsa.gr/horde/imp` — suggests membership webmail integration
- **Public content**: "Επίκαιρη Νομολογία" (recent case law) and "Επίκαιρη Νομοθεσία" (recent legislation) pages exist in navigation but redirect to login
- **Cost**: Included in ΔΣΑ bar membership fees; not separately priced

**Important note**: Non-lawyers cannot access Isocrates directly. A ΔΣΑ member lawyer could run specific searches. Alternatively, Qualex and Sakkoulas-Online serve as commercial equivalents with subscription access.

### Search Capabilities

Access to the search interface requires login. Based on public documentation and standard Greek legal database conventions, Isocrates supports:

- Full-text search across legislation and case law
- Search by court (ΑΠ, Εφετείο, Πρωτοδικείο, Ειρηνοδικείο)
- Search by decision number (e.g., "ΑΠ 777/2022")
- Search by statutory provision cited (e.g., "άρθρο 592 ΑΚ")
- Search by legal headword (λήμμα)
- Date range filtering
- Party name search (useful for prior litigation checks — anonymization process may affect results)

The anonymization process removes party names from decisions, BUT party name searches may still work on the non-anonymized metadata (this varies by system implementation).

### Document Types

#### Εθνική Νομολογία (Case Law)
- Full text of decisions from ALL Greek courts
- Each decision enriched with:
  - **Λήμματα**: Legal headwords/keywords
  - **Περίληψη**: Summary of holding
  - **Νομικές Διατάξεις**: Linked statutory provisions
- **Anonymized**: Personal data of natural persons removed
- All courts including **Ειρηνοδικεία** — critical differentiator for small claims deposit cases

#### Εθνική Νομοθεσία (Legislation)
- Complete codified legislation from founding of Greek state
- Tracks full amendment history: initial form → current form
- Sourced from official ΦΕΚ + official websites of legislative bodies

#### Υπολογιστικές Εφαρμογές (Calculators)
- **Τόκοι υπερημερίας**: Default interest rate calculator
- **Τόκοι Δημοσίου**: Public sector interest
- **Τόκοι Επιδικίας**: Judicial award interest
- **Τόκοι Συμβατικοί**: Contractual interest
- **Δικαστικό ένσημο**: Court stamp fee calculator
- The system accounts for exact number of days per year (leap years handled correctly)

### Network API Analysis

The main `connectSites()` function is a JavaScript-handled login redirect — not a public API. The site serves static HTML for its public-facing pages. No REST API endpoints observed from public browsing. The backend is likely a proprietary database system behind the login gateway.

Navigation patterns:
- `https://www.dsanet.gr/Epikairothta/Nomologia/nomologia-latest.html` — recent case law (requires login)
- `https://www.dsanet.gr/Epikairothta/Nomothesia/nomothesia-latest.html` — recent legislation (requires login)
- Both return to homepage when accessed without login

### Typical Search Queries (via a ΔΣΑ lawyer)

1. **"άρθρο 592 ΑΚ φυσιολογική φθορά"** → All courts, 2015-present
   - Target: ΑΠ decisions on normal wear-and-tear in tenancy; any Ειρηνοδικείο decisions

2. **"εγγύηση μίσθωση αποζημίωση"** → All courts, 2018-present
   - Target: Decisions on what landlords can lawfully retain from security deposits

3. **"art. 288 ΑΚ μίσθωση καλή πίστη"** → ΑΠ level, 2015-present
   - Target: Good faith doctrine in tenancy disputes

4. **Ειρηνοδικείο-specific deposit cases** → "Ειρηνοδικείο" + "κατάθεση εγγύηση"
   - These are not typically in Sakkoulas-Online or Qualex; Isocrates unique value

### Comparison to Other Tools

| Aspect | Isocrates (dsanet.gr) | Qualex | Sakkoulas-Online |
|--------|----------------------|--------|-----------------|
| Ειρηνοδικείο decisions | Yes | Partial | No |
| Access | ΔΣΑ members only | Subscription | Subscription |
| Cost for non-lawyer | Not accessible | Subscription fee | Subscription fee |
| Coverage | All courts | All courts | Focus on published decisions |
| Administrative docs | No | Yes (99K) | Partial |
| Templates | No | Yes | No |

### Limitations

- **Access barrier**: Not available to non-lawyers directly.
- Party name search post-anonymization: uncertain whether party search works
- The 404 errors on direct section URLs suggest some pages are entirely behind login
- No semantic/AI search confirmed (may have basic full-text only)
- Coverage cutoff for older decisions: unknown from public interface

---

## DSAnet

> **URL:** https://www.dsanet.gr/
> **Note:** dsanet.gr IS the Isocrates database (same site)

dsanet.gr is the domain for the Athens Bar Association's "Ισοκράτης" Τράπεζα Νομικών Πληροφοριών.

### Clarification on Naming

- **dsanet.gr**: The domain/server operated by ΔΣΑ (Δικηγορικός Σύλλογος Αθηνών)
- **Ισοκράτης (Isocrates)**: The brand name for the legal database system running at dsanet.gr
- Both names are used interchangeably in Greek legal practice

The homepage explicitly states: "Η Τράπεζα Νομικών Πληροφοριών 'ΙΣΟΚΡΑΤΗΣ' τώρα και στο κινητό σου"

### Key Confirmed Facts

- **ΔΣΑ email server**: Links to `mail.dsa.gr/horde/imp` (Horde webmail)
- **External links from homepage**: Ministry of Justice | EUR-Lex | NSK (Νομικό Συμβούλιο Κράτους) | ΕΕΔΑ | kostasbeys.gr (judicial commentary)
- **Mobile access**: Explicitly advertised ("τώρα και στο κινητό σου")
- **Related sites linked**: olomeleia.gr (Bar Council federation), dsalib.gr (ΔΣΑ library), dsa.gr (ΔΣΑ main site)
- **Copyright**: © 2026 Τράπεζα Νομικών Πληροφοριών ΙΣΟΚΡΑΤΗΣ

### Note on the Name "Isocrates" vs justice.gov.gr

There is a separate, unrelated system sometimes also called "Isocrates" operated by the Ministry of Justice at justice.gov.gr. That system:
- URL: isocrates.justice.gr (resolved to DNS error during testing — may be offline or renamed)
- Was the Ministry of Justice's own case management and search system
- Different from the ΔΣΑ Isocrates at dsanet.gr

The Ministry of Justice portal justice.gov.gr was also unreachable during testing (navigation timeout). This may indicate temporary downtime or infrastructure changes.

For practical purposes, **dsanet.gr is the accessible and functioning Isocrates database** for case law research.
