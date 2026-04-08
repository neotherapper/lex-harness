---
title: "et.gr — Εθνικό Τυπογραφείο (Government Gazette)"
jurisdiction: greece
source: "https://www.et.gr"
last_verified: "2026-04-08"
---

# search.et.gr — Research Report

> **URL:** https://search.et.gr/el/
> **Researched:** 2026-03-08 (via Chrome DevTools MCP)
> **Operator:** Εθνικό Τυπογραφείο (National Printing House of Greece), Καποδιστρίου 34, Athens 10432
> **Access model:** Free (core search); Registration adds alerts and library features
> **Primary use:** Full-text search of Φ.Ε.Κ. (Government Gazette), company filings, and codified legislation

## Executive Summary

- The **official Greek Government Gazette search engine**, operated by Εθνικό Τυπογραφείο under gov.gr
- Six distinct search modes: Simple ΦΕΚ search, Smart/Semantic search, Legislation search (by law number), Company search (by ΑΦΜ/ΓΕΜΗ/ΑΡΜΑΕ), Κ.Α.Δ. search, and ΑΣΕΠ search
- **Backend API** routes to `https://nationalprintinghousefek.azurewebsites.net/` (Azure-hosted) — this domain did not resolve directly in testing, suggesting it requires same-origin context from the site
- **Company search** accepts ΑΦΜ or ΓΕΜΗ number — e.g. search by ΑΦΜ for a party to find related legislation
- Registration enables: saved alerts on topics, library saving with tags, email notifications for new publications

## Site Overview

Εθνικό Τυπογραφείο is the official publisher of the Greek Government Gazette (ΦΕΚ — Φύλλο Εφημερίδας της Κυβέρνησης). This search portal is the primary public interface for finding ΦΕΚ publications. It was built on WordPress and runs the backend search engine on Azure.

The site does NOT contain court decisions. It is exclusively for legislative and regulatory publications.

## Access and Registration

- **Core search**: Fully free, no registration required
- **Registration** (free account): Unlocks alerts (email notifications for keyword matches), personal library with tags, ability to save favourite ΦΕΚ documents
- **No paid tier visible**: All content appears free once published

## Search Capabilities

### Search Modes Available

| Mode | URL | What it searches |
|------|-----|-----------------|
| Απλή Αναζήτηση | `/el/simple-search/` | ΦΕΚ by year/issue/number/keywords |
| Έξυπνη Αναζήτηση (semantic) | `/el/advanced-search/` | Full-text semantic search with filters: year, issue type, date range, tags, legislation groups, entity type |
| Αναζήτηση Νομοθεσίας | `/el/search-legislation/` | By type (Νόμος, ΠΔ, ΠΝΠ, ΒΔ, etc.) + year + number |
| Αναζήτηση Εταιρειών | `/el/search-company/` | By company name OR ΑΦΜ/ΓΕΜΗ/ΑΡΜΑΕ |
| Αναζήτηση Κ.Α.Δ. | `/el/search-kad/` | KAD activity codes |
| Αναζήτηση Α.Σ.Ε.Π. | `/el/search-asep/` | Civil service exam notices |

### Smart Search Features (Έξυπνη Αναζήτηση)
- Free text query with semantic similarity
- Exact phrase matching using quotation marks (e.g., `"αποθεματικό"`)
- Filters: year (multi-select, back to 1997+), issue type (Τεύχος), ΦΕΚ number range, date published, date released, tags, legislation groups, entity type
- Boolean-style operators implied by free text

### Legislation Search Parameters
- Year: 2026 back to at least 2018 visible (likely complete from 1975+)
- Type: Νόμος | Προεδρικό Διάταγμα | Πράξη Νομοθετικού Περιεχομένου | Βασιλικό Διάταγμα | Νομοθετικό Προεδρικό Διάταγμα | Νομοθετικό Διάταγμα | Αναγκαστικός Νόμος
- Number field: exact law number

## Document Types

- **ΦΕΚ Α** (Τεύχος Α): Νόμοι (laws), Προεδρικά Διατάγματα (presidential decrees), Πράξεις Νομοθετικού Περιεχομένου (legislative acts)
- **ΦΕΚ Β** (Τεύχος Β): Υπουργικές Αποφάσεις (ministerial decisions), ΚΥΑ
- **ΦΕΚ Γ**: Public servant appointments
- **ΦΕΚ ΑΑΠ** (Ανώνυμες Εταιρείες & ΕΠΕ): Company publication notices (incorporations, amendments, dissolutions)
- **ΦΕΚ Δ**: Expropriations
- **ΑΣΕΠ**: Civil service announcements

## Network API Analysis

The search forms submit to: `https://nationalprintinghousefek.azurewebsites.net/` (GET method)

Key observed URL parameters:
- `field_name` = free text query
- `field_year` = year (multi-select)
- `field_issue` = issue type (Τεύχος)
- `field_number` = ΦΕΚ number
- `datefilter_published` = publication date range
- `datefilter_released` = release date range
- `field_tags[]` = tags (multi-select)
- `field_label[]` = legislation groups
- `field_entity_type` + `field_entity[]` = entity filters
- `lposts_per_page` = results per page
- `lorderby` / `lorder` = sort field / direction

For company search:
- `filter_company_name` = company name
- `field_company_id` = identifier type (afm | gemi | armae)
- `field_company_id_number` = the actual number

For legislation search:
- `field_year[]` = year
- `legislation_catalogues` = type (Νόμος, ΠΔ, etc.)
- `field_number_legislation` = law/decree number

Note: The Azure backend (`nationalprintinghousefek.azurewebsites.net`) is not directly accessible from outside the site context — it appears to use CORS restrictions. Queries must be made through the website interface.

## Example Searches

### Legislation lookups

- **Legislation search: N. 4601/2019** → `legislation_catalogues=Νόμος&field_year[]=2019&field_number_legislation=4601`
  - Expected: ΦΕΚ Α 44/2019 — confirms spin-off law articles

- **Smart search by company name** in ΦΕΚ ΑΑΠ
  - Expected: All official company publications involving named entities

### Precedents to look for

This site does NOT contain court decisions — use Isocrates (dsanet.gr) or Qualex/Sakkoulas-Online for precedents.

## Comparison to Other Tools

| Aspect | search.et.gr | kodiko.gr | lawspot.gr |
|--------|-------------|-----------|-----------|
| ΦΕΚ full-text | Yes (primary) | Yes (secondary) | No |
| Company filings | Yes (ΑΦΜ/ΓΕΜΗ search) | No | No |
| Court decisions | No | No | No |
| Law text | By ΦΕΚ | Codified + amended | Full text |
| Free tier | Full | Partial | Full |

## Limitations

- **No court decisions** — purely legislative/regulatory
- Azure backend not directly accessible via API calls (CORS restriction)
- Year coverage starts around 1997 in the UI but may have earlier records
- Company search requires exact ΑΦΜ/ΓΕΜΗ — no fuzzy name matching confirmed
- Semantic search quality unknown without active subscription testing

## Screenshot Description

Homepage shows: Greek government header with gov.gr logo; clean interface with large search bar and dropdown for year/issue; six subsections listed below: Απλή Αναζήτηση, Έξυπνη Αναζήτηση, Αναζήτηση Κ.Α.Δ., Αναζήτηση Νομοθεσίας, Αναζήτηση Εταιρειών, Αναζήτηση Α.Σ.Ε.Π. Blue and white color scheme consistent with Greek government sites. Login/register links visible top right.
