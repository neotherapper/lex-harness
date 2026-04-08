---
title: "N-Lex — EU Gateway to National Law"
jurisdiction: greece
source: "https://n-lex.europa.eu"
last_verified: "2026-04-08"
---

# N-Lex — EU Gateway to National Law

N-Lex (n-lex.europa.eu) is the EU-managed gateway that links to national legal databases across all EU member states. It supports ELI (European Legislation Identifier) URIs for cross-border citation.

## Access

- **No public API.** N-Lex is web-only. There is no REST endpoint for programmatic access.
- **ELI search:** If a national instrument has an ELI URI assigned, N-Lex can resolve it.
- **Expert search:** `https://n-lex.europa.eu/n-lex/recherche/rechercheExpert?lang=en`

## Use Cases

- Cross-referencing Greek national law with EU instruments
- Finding ELI URIs for use in `n_lex_url` manifest fields
- Multi-country search when researching EU-wide legal standards

## Limitations

- Greek law is not fully indexed in N-Lex (as of 2026-04)
- Prefer EUR-Lex for EU instruments and kodiko.gr/et.gr for Greek statutes
- NLexFetcher in `scripts/shared/n_lex.py` requires a direct `n_lex_url` or `eli_url` in the manifest entry — it cannot search by keyword

## ELI Format for Greek Law

```
https://www.et.gr/eli/law/{year}/{number}/fek/{fek_series}/{fek_year}/{fek_number}/
```

If an ELI URI is known for a Greek statute, store it as `eli_url` in the manifest entry and the NLexFetcher can retrieve it.
