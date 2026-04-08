---
title: "kodiko.gr — Codified Greek Legislation"
jurisdiction: greece
source: "https://www.kodiko.gr"
last_verified: "2026-04-08"
---

# kodiko.gr — Research Report (Bonus Site)

> **URL:** https://www.kodiko.gr/
> **Researched:** 2026-03-08 (via Chrome DevTools MCP)
> **Operator:** kodiko.gr (private company, Athens — contact via kodiko.gr/contact)
> **Access model:** Mixed — free basic legislation search; subscription for full features (case law, annotations, alerts)
> **Primary use:** Codified Greek legislation with real-time amendment tracking; case law search; KAD search; AI assistant

## Executive Summary

- **Kodiko.gr** is one of the two main free Greek legislation search engines (alongside search.et.gr)
- Contains: **5,479 νόμοι** | **22,681 ΠΔ** | **59,254 Υπ. Αποφάσεις** — all codified and cross-linked
- **Daily updates**: New laws appear same day as ΦΕΚ publication (latest: N. 5286/2026 from 06.03.2026)
- **Direct article links**: Every provision has a stable URL — `https://www.kodiko.gr/nomothesia/diataksi/[ID]`
- **Nomologia section**: Case law search available (scope requires login to verify)
- **AI Assistant** ("Kodiko Assistant") — new feature for legal queries (subscription/login required)
- **Forum** (forum.kodiko.gr) — public legal discussion forum
- Free for legislation text; subscription for advanced features (favorites, notes, AI assistant)

## Site Overview

Kodiko.gr is a professional-grade Greek legislation search engine. It tracks every ΦΕΚ publication and maintains codified versions of all laws in real-time. The key advantage over lawspot.gr is that kodiko.gr codifies laws with their amendments applied — you see the current version of any article as it stands today, not just the original text.

The site shows 5,479 laws, 22,681 presidential decrees, and 59,254 ministerial decisions — comprehensive coverage of Greek primary and secondary legislation.

## Access and Registration

- **Free**: Browse and read all legislation text
- **Free account** (registration): Favorites, notes, extended history
- **Subscription**: AI Assistant, advanced features, group packages
- **Pricing**: Ατομική συνδρομή (individual) + Ομαδικά πακέτα (group) — pricing page at `/main/payment_methods` but not viewed in detail

## Search Capabilities

### Free tier
- **Full-text search**: Search box on homepage across all legislation
- **Browse by latest**: ΦΕΚ Α (laws/PD), ΦΕΚ Β (ministerial decisions) listed daily
- **Direct URL access**: `/nomothesia/document/[ID]/[slug]` for specific laws
- **Nomologia search**: `/nomologia` — scope confirmed (case law search section exists)
- **KAD search**: `/kad` — business activity codes

### Subscription features
- AI Assistant (`/assistant`) — legal queries with verified responses
- Favorites and personal notes
- Alerts for specific legislation changes
- "Ψάχνω και δε βρίσκω" support (request specific content)

### URL Patterns for Direct Access

Legislation by ID (stable, direct-linkable):
```
https://www.kodiko.gr/nomothesia/document/[ID]/[slug]
```

Example confirmed:
- N. 5286/2026: `https://www.kodiko.gr/nomothesia/document/1295621/nomos-5286-2026`

The `nomologia` section for case law is accessible at:
```
https://www.kodiko.gr/nomologia
```
(Requires login to use fully — scope of case law coverage not confirmed from public interface)

## Document Types

### Confirmed covered
- **Νόμοι** (Laws): 5,479 entries, codified with amendments
- **Προεδρικά Διατάγματα**: 22,681 entries
- **Υπουργικές Αποφάσεις**: 59,254 entries
- **ΚΥΑ** (Joint Ministerial Decisions): Included in Υπ. Αποφάσεις count
- **Νομολογία** (Case Law): Available (scope unclear without subscription)
- **KAD** (Business activity codes): Full database

### NOT confirmed
- Whether case law covers Ειρηνοδικείο decisions
- Whether administrative court decisions included
- HDPA/APDPCH decisions specifically

## Network API Analysis

Kodiko uses a SPA (Single Page Application) architecture. Navigation triggers JavaScript-based page transitions rather than full page loads. Key observations:

- Main search is at `https://www.kodiko.gr/` with a search box
- Legislation URLs: `/nomothesia/document/[numeric-id]/[slug]`
- Article-level URLs: `/nomothesia/diataksi/[ID]` — tested and confirmed (though the tested ID 537066 was an unrelated P.D. article)
- Nomologia: `/nomologia` section confirmed exists
- Forum: `https://forum.kodiko.gr/` (separate subdomain)
- AI Assistant: `/assistant` (subscription required)

No public JSON/REST API observed. The site uses JavaScript-rendered content.

## Typical Use Cases

### Primary use: Verify law text before citing in formal documents

Kodiko is the **fastest free tool** to look up and verify current codified text of any Greek law.

**Key law categories to search on kodiko.gr**:

| Category | Search Query | Purpose |
|----------|-------------|---------|
| Αστικός Κώδικας (ΑΚ) | Search "αστικός κώδικας" | Civil code provisions (tenancy, obligations, unjust enrichment) |
| Consumer protection laws | Search "2251 1994" | Law 2251/1994 Arts. 9γ/9δ/9ε |
| Spin-off / corporate law | Search "4601 2019" | Art. 65 §4 (joint liability), Art. 70 §2 (universal succession) |
| GDPR implementing law | Search "4624 2019" | Greek GDPR implementation |
| Accounting/invoice standards | Search "4308 2014" | Art. 9(1)(δ) mandatory invoice fields |

### Monitoring new legislation
- **Bookmark**: `https://www.kodiko.gr/` — homepage shows latest ΦΕΚ A/B publications daily
- Useful to check for new laws affecting tenancy or consumer protection

### Case law check
- Navigate to `/nomologia` and search for relevant ΑΚ article citations

## Comparison to Other Tools

| Aspect | kodiko.gr | lawspot.gr | search.et.gr | Qualex |
|--------|----------|-----------|-------------|--------|
| Codified (amended) text | Yes (real-time) | Partial (may lag) | Via ΦΕΚ (not codified) | Yes |
| Article-level stable URLs | Yes | Yes (law-level) | No | No (subscription) |
| Case law | Yes (scope unclear) | News only | No | 260K+ |
| Daily ΦΕΚ updates | Yes | No | Yes | Yes |
| Free full text | Yes | Yes | Yes | No |
| AI assistant | Yes (subscription) | No | No | Yes (chatbook, subscription) |
| Company search | No (KAD only) | No | Yes (ΑΦΜ/ΓΕΜΗ) | No |

## Limitations

- Case law scope not confirmed from public interface (may be limited compared to Qualex)
- AI assistant requires subscription — quality unverified
- Forum content is user-generated (not authoritative)
- No confirmed coverage of HDPA/APDPCH decisions specifically
