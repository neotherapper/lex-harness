---
title: "lawspot.gr — Free Greek Law Summaries"
jurisdiction: greece
source: "https://www.lawspot.gr"
last_verified: "2026-04-08"
---

# Lawspot.gr — Research Report

> **URL:** https://www.lawspot.gr/
> **Researched:** 2026-03-08 (via Chrome DevTools MCP)
> **Operator:** Lawspot (associated with Sakkoulas — Sakkoulas ad banner present; may be a jointly operated portal)
> **Access model:** Primarily free; some content requires login
> **Primary use:** Free access to Greek legislation text; legal news; lawyer directory; supplementary legal articles from practitioner-lawyers

## Executive Summary

- **Free, public Greek legal resource** — largest free Greek law site
- **Full text of Greek laws** available without login or subscription (verified: Law 2251/1994 confirmed fully accessible)
- **URL pattern for laws**: `lawspot.gr/nomothesia/nomos-[number]-[year]/` — predictable and direct-linkable
- Contains: Νομικά Νέα (legal news, daily updated) | Νομοθεσία (legislation text) | Αρθρογραφία (practitioner articles) | Βοηθητικά Κείμενα (guidance documents) | Δικηγόροι (lawyer directory)
- **Last modification** of laws is displayed (e.g., Law 2251/1994: "ΤΕΛΕΥΤΑΙΑ ΤΡΟΠΟΠΟΙΗΣΗ: 07.07.2016" — note: this may be outdated and needs verification for current text)
- Legal news updated daily; covers ΑΠ/court decisions, new legislation, APDPCH decisions, EU law
- **Topic filters** for legislation include "Μισθώσεις" (tenancies) — directly relevant
- Partnership/sponsorship with Εκδόσεις Σάκκουλα (ad banner for books on site)

## Site Overview

Lawspot is a Greek legal portal aimed at both lawyers and the general public. Its primary value is:

1. **Free law text**: Full text of Greek laws organized by number/year, at-a-glance article-by-article structure
2. **Legal news**: Daily coverage of court decisions, legislation changes, HDPA/APDPCH decisions, EU law
3. **Practitioner articles**: Written by registered lawyer-members; free to read
4. **Lawyer finder**: Directory of lawyers by specialization (Αστικό, Μισθώσεις, GDPR, etc.)
5. **Βοηθητικά Κείμενα**: Practical guidance on administrative procedures (e.g., ΑΑΔ instructions, ΑΣΕΠ processes)

The site does NOT contain full case law text (no decisions database). It reports on individual decisions as news items, not as a searchable case law repository.

## Access and Registration

- **Legislation text**: Fully free, no login required
- **Legal news**: Fully free, no login required
- **Practitioner articles**: Fully free, no login required
- **Lawyer directory**: Fully free, no login required
- **Login/account**: Available (`/accounts/login/`) but not required for any verified content type
- **No subscription tiers found**: This appears to be a fully free service

## Search Capabilities

- **Search icon** in header (`/search/`) — likely full-text search across all content
- **URL-predictable law access**: `/nomothesia/nomos-[N]-[YYYY]/` (e.g., `/nomothesia/nomos-2251-1994/`)
- **Topic filter on Βοηθητικά Κείμενα**: 80+ legal topic areas including "Μισθώσεις", "Αστικό Δίκαιο", "Δίκαιο Καταναλωτή", "Προσωπικά Δεδομένα"
- **Category filters on news**: Ελλάδα | Διεθνή | Νέες Τεχνολογίες | Για Νομικούς | Νομοθεσία

## Document Types

### Νομοθεσία (Legislation)
Full text of Greek laws, organized article-by-article. Confirmed accessible:
- **Law 2251/1994** (Consumer Protection): All articles visible including Art. 9γ, 9δ, 9ε (unfair commercial practices), Art. 2 (ΓΟΣ)
- Laws listed by number going back to at least 2022 (most recently added)
- **Important caveat**: "ΤΕΛΕΥΤΑΙΑ ΤΡΟΠΟΠΟΙΗΣΗ" date shown — some laws may show an older date that does not reflect recent amendments. Always cross-check with kodiko.gr or search.et.gr for current codified text.
- URL pattern confirmed: `/nomothesia/nomos-[NUMBER]-[YEAR]/`

### Νομικά Νέα (Legal News)
- **Daily coverage** of:
  - ΑΠ decisions (e.g., "ΟλΑΠ 1/2026: Καρτέλ εταιρειών εμπορίας γάλακτος — αδικαιολόγητος πλουτισμός")
  - HDPA/APDPCH decisions (e.g., "ΑΠΔΠΧ 24/2025: Δικαίωμα στη λήθη εταίρου δικηγορικής εταιρείας")
  - New legislation (e.g., "Νέες διατάξεις για τις μεταβιβάσεις ακινήτων")
  - CJEU Advocate General opinions
  - DSA/Ombudsman announcements
- **Not full text** of decisions — just summaries/news articles with citation references
- Very useful for **monitoring new ΑΠ decisions** on relevant articles that appear after initial case research

### Αρθρογραφία (Legal Articles)
- Written by practitioner-lawyers who are registered Lawspot members
- Topics include consumer protection, tenancy, GDPR, civil law
- Free to read
- Variable quality (practitioner-level, not academic journals like Ελληνική Δικαιοσύνη)

### Βοηθητικά Κείμενα (Guidance Documents)
- Practical administrative guidance
- Examples: AADE instructions, ASEP procedures, data transfer guidance post-Schrems II
- Dated (most recent: 09.02.2022 — possibly no longer updated)

## Network API Analysis

The site appears to be a CMS-based portal (likely WordPress or Drupal). URLs are human-readable slugs. No REST API observed.

Confirmed URL patterns:
- Laws: `https://www.lawspot.gr/nomothesia/nomos-[N]-[YYYY]/` — works for confirmed laws
- News items: `https://www.lawspot.gr/nomika-nea/[slug]/`
- Articles: `https://www.lawspot.gr/nomika-blogs/[slug]/`
- Lawyer profiles: `https://www.lawspot.gr/dikigoros/[username]/`
- Topic filter: `https://www.lawspot.gr/voithitika-keimena/?filter_category=[topic]` (implied)

**Direct linking advantage**: The predictable URL pattern means law texts can be directly cited in legal documents. Example:
- `https://www.lawspot.gr/nomothesia/nomos-2251-1994/` = Law 2251/1994 full text

## Accuracy Verification — Sample Laws

**Law 2251/1994 VERIFIED**: Full article-by-article text accessible. Article structure matches expected content including:
- Art. 9γ: Απαγόρευση αθέμιτων εμπορικών πρακτικών (unfair commercial practices prohibition)
- Art. 9δ: Παραπλανητικές πράξεις (misleading acts)
- Art. 9ε: Παραπλανητικές παραλείψεις (misleading omissions)
- Art. 2: ΓΟΣ (standard form contracts)

**Caveat**: Law 2251/1994 shows last amendment as 07.07.2016 — but the law has likely been amended after that date. Cross-check current text with kodiko.gr (which shows real-time codification).

## Typical Use Cases

### Immediate free resources

1. **Law 2251/1994 full text** (confirmed free):
   `https://www.lawspot.gr/nomothesia/nomos-2251-1994/`

2. **Monitor legal news for new decisions**:
   - Search `https://www.lawspot.gr/nomika-nea/` for relevant article citations
   - Monitor for new HDPA/APDPCH decisions on data protection
   - Monitor for new ΑΠ decisions on GDPR Art. 82

3. **Find lawyer directory** — if a claimant needs a specialist:
   - `https://www.lawspot.gr/vres-dikigoro/` with specialization "Μισθώσεις" or "Δίκαιο Καταναλωτή"

4. **Verify legislation text** before formal document citation — always cross-check last-amendment date

### Topic-filtered searches

- **Μισθώσεις** filter in Βοηθητικά Κείμενα → guidance documents on tenancy
- **Δίκαιο Καταναλωτή** in Αρθρογραφία → consumer protection articles
- **Προσωπικά Δεδομένα** in Αρθρογραφία → GDPR practitioner articles

### Monitoring for new decisions

Lawspot reports on major court decisions as news. Set browser bookmarks for:
- `https://www.lawspot.gr/katigories-eidiseon/ellada/` — Greek court decisions news
- `https://www.lawspot.gr/katigories-eidiseon/nees-tehnologies/` — technology/GDPR news

## Comparison to Other Tools

| Aspect | Lawspot.gr | kodiko.gr | search.et.gr | Qualex |
|--------|-----------|-----------|-------------|--------|
| Free law text | Yes (full) | Yes (free basic) | Yes (ΦΕΚ) | No (subscription) |
| Case law | News summaries only | Partial | No | Full (260K+) |
| Direct-linkable URLs | Yes | Yes | No (dynamic) | No |
| News monitoring | Yes (daily) | No | No | Yes (alerts) |
| Practitioner articles | Yes (free) | No | No | Yes (28K, subscription) |
| Accuracy of codified text | Good (may lag amendments) | Better (real-time) | Authoritative (ΦΕΚ source) | Best (cross-linked) |

## Limitations

- **Not a case law database** — no searchable decisions
- Law text may not reflect latest amendments (shows last amendment date)
- Practitioner articles are not peer-reviewed academic publications — lower citation weight
- Βοηθητικά Κείμενα appears to not have been updated since 2022
- No API for programmatic access
