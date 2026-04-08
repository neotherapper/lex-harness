---
title: "Νομική Βιβλιοθήκη (Nomiki Vivliothiki) — Subscription Legal Database"
jurisdiction: greece
source: "https://www.nomiki-vivliothiki.gr"
last_verified: "2026-04-08"
---

# Νομική Βιβλιοθήκη / Qualex — Research Report

> **URLs:**
>   - Publisher site: https://www.nb.org/
>   - Legal database (Qualex): https://www.qualex.gr/
>   - AI interface: https://chatbook.nb.org/
> **Researched:** 2026-03-08 (via Chrome DevTools MCP)
> **Operator:** Νομική Βιβλιοθήκη Α.Ε. (NOMIKI BIBLIOTHIKI S.A.), Μαυρομιχάλη 23, Athens — T: 210 3678800
> **Access model:** Subscription required for full access; some free content available
> **Primary use:** Comprehensive Greek legal database — legislation, case law, doctrine, journal articles, templates

## Executive Summary

- **Qualex** (qualex.gr) is the flagship legal database of Νομική Βιβλιοθήκη — the largest Greek legal publisher
- Contains: 469,719 legislative texts (codified + cross-linked) | 260,123 court decisions (all levels) | 28,423 legal articles | 99,157 administrative documents | 4,259 document templates | 1,739 books
- **21 scientific periodicals** fully indexed from first issue
- Subscription-based with per-subject packages (Ιδιωτικό/Δημόσιο/Ποινικό Δίκαιο); no confirmed pricing visible
- **AI.chatbook** (chatbook.nb.org) — dedicated AI assistant with legal database grounding; subscription required; described as "verified answers, trusted sources"
- **Case workflow tool** included: diagrams for case types, reminders, calendar sync
- **Thesaurus** of 64 legal topic areas with hierarchical term structure for semantic searching

## Site Overview

Νομική Βιβλιοθήκη has been Greece's dominant legal publisher since 1958. Qualex is their online legal research platform, described as the "most ambitious legal informatics project of the last 20 years." It combines codified legislation linked to case law, doctrine, administrative documents, and templates in a single searchable database.

The main nb.org website is an e-commerce platform (Magento-based) for purchasing books, seminar registrations, and conference tickets. Qualex (qualex.gr) is the separate database access portal.

## Access and Registration

- **Subscriptions**: Per-subject packages
  - Ιδιωτικό Δίκαιο (Civil + Procedural + Commercial + Labour): most relevant for civil dispute cases
  - Δημόσιο Δίκαιο (Administrative, Constitutional, EU)
  - Ποινικό Δίκαιο
  - Combined packages available (Ιδιωτικό + Δημόσιο; all three)
- **Pricing**: Not published on the subscription page; requires contacting Νομική Βιβλιοθήκη
- **Free content**: Some documents visible without login (marked "Δωρεάν Περιεχόμενο" category); exact scope unclear
- **Trial**: Site mentions "Δοκιμάστε Δωρεάν" (try for free) but no duration specified
- **Institutional/group packages**: Available for law firms, companies, public bodies

## Search Capabilities

### Search Modes on Qualex

1. **Απλή Αναζήτηση** (Simple): Free text across all categories
   - Checkbox filters: Νομοθεσία | Νομολογία | Βιβλιογραφία | Αρθρογραφία | Διοικητικά Έγγραφα | Υποδείγματα

2. **Εξειδικευμένη Αναζήτηση** (Advanced): Up to 19 criteria (fields not confirmed from public interface)

3. **Αναζήτηση με νομοθετική διάταξη** (New — search by statutory provision): Search for case law and doctrine linked to a specific article

4. **Thesaurus search**: 64 legal topic areas with hierarchical vocabulary for conceptual queries

### Key Features
- **Cross-linking**: Every law article links directly to related decisions, articles, templates
- **My Alerts**: System learns user interests and sends notifications for new matching content
- **Non-stop Search**: Saves incomplete searches; continues monitoring and notifies via email
- **Search history**: Stored per session and across sessions
- **Case folders**: Organize searches by matter
- **Annotations**: Add margin notes to texts
- **Legal Calculators**: Interest calculation (default, public, judicial, contractual), court stamp calculation
- **Case Workflow**: Flowcharts for case handling procedures
- **Mobile access**: Web app, dedicated mobile app

### Coverage Depth
- Legislation: **469,719 items** — codified, cross-linked, full history (initial → current form)
- Case law: **260,123 decisions** — all court levels; anonymized; enriched with headnotes (λήμματα), summaries, linked to statutory provisions
- Scientific periodicals: 21 journals fully indexed, including:
  - ΕΦΑΡΜΟΓΕΣ ΑΣΤΙΚΟΥ ΔΙΚΑΙΟΥ & ΠΟΛΙΤΙΚΗΣ ΔΙΚΟΝΟΜΙΑΣ (civil law and procedure)
  - ΔΙΚΑΙΟ ΕΠΙΧΕΙΡΗΣΕΩΝ & ΕΤΑΙΡΙΩΝ (corporate issues)
  - ΔΙΚΑΙΟ ΤΕΧΝΟΛΟΓΙΑΣ & ΕΠΙΚΟΙΝΩΝΙΑΣ (GDPR/data)
  - ΕΥΡΩΠΑΪΚΟ ΔΙΚΑΙΟ
  - ΕΓΚΛΗΜΑΤΟΛΟΓΙΑ

## Document Types

| Category | Count | Relevance to Civil Disputes |
|----------|-------|---------------------|
| Νομοθεσία | 469,719 | Civil code articles codified |
| Νομολογία | 260,123 | ΑΠ decisions on tenancy, consumer protection |
| Αρθρογραφία | 28,423 | Doctrine on consumer protection, GDPR |
| Διοικητικά Έγγραφα | 99,157 | NSK opinions, regulatory acts |
| Υποδείγματα | 4,259 | Draft complaints, demand letters |
| Βιβλιογραφία | 1,739 | Monographs (Astiko Dikaio commentaries) |

## Network API Analysis

Qualex uses .NET/ASP.NET WebForms (`__VIEWSTATE`, `__CMSCsrfToken` present in forms). The search form at `/el-GR/Apli-Anazitisi` posts to itself. This is a classic server-side rendering architecture — no observable public REST API. Search fields identified:

- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$AllCheckBox` — all categories
- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$LegislationCheckBox`
- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$CaselawCheckBox`
- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$BooksCheckBox`
- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$ArticlesCheckBox`
- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$OtherCheckBox`
- `p$lt$ctl01$pageplaceholder$p$lt$ctl00$NVSearchbar$SamplesCheckBox`
- `searchBar` — main text input

No public API endpoint observed. Subscription content delivery appears to use session cookies.

AI.chatbook backend not inspectable (requires login).

## Typical Searches (once subscribed)

For a civil tenancy or consumer dispute, the **Ιδιωτικό Δίκαιο** subscription covers all relevant issues:

1. **"φυσιολογική φθορά μίσθωση"** [Νομολογία + Νομοθεσία]
   - Expected: ΑΠ decisions on Art. 592 ΑΚ; doctrine on what qualifies as normal wear

2. **Αναζήτηση με νομοθετική διάταξη: Art. 592 ΑΚ**
   - Expected: All decisions and articles that cite or interpret Art. 592 ΑΚ

3. **"κατάθεση εγγύηση μίσθωση αφαίρεση"** [Νομολογία]
   - Expected: Decisions on security deposit retention; what landlords can lawfully deduct

4. **"GDPR Art. 82 αποζημίωση"** in Αρθρογραφία + ΔΙΚΑΙΟ ΤΕΧΝΟΛΟΓΙΑΣ & ΕΠΙΚΟΙΝΩΝΙΑΣ
   - Expected: GDPR damages quantum guidance

## Comparison to Other Tools

| Aspect | Qualex (nb.org) | Sakkoulas-Online | Isocrates (dsanet.gr) |
|--------|----------------|-----------------|----------------------|
| Volume | 260K decisions | Smaller | Large but access-restricted |
| Periodicals | 21 journals | Multiple Sakkoulas journals | None |
| Templates | 4,259 | Some | None |
| AI interface | Yes (chatbook) | No | No |
| Article-linked search | Yes (new feature) | No | No |
| Free tier | Very limited | Very limited | Bar members only |
| Pricing | Subscription (opaque) | Subscription | Bar membership |

## Limitations

- Subscription pricing not published; likely expensive for individual litigants
- No confirmed free trial duration
- Public interface does not expose the number of decisions per specific article (requires login)
- AI.chatbook quality unverified (requires subscription to test)
- Coverage staleness: last update date for specific decisions not visible from public interface
