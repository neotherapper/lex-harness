---
title: "EUR-Lex — EU Law in Greek (EL)"
jurisdiction: greece
source: "https://eur-lex.europa.eu"
last_verified: "2026-04-08"
---

# EUR-Lex — EU Law in Greek (EL)

EUR-Lex is the official portal for EU law. Greek law derives authority from EU regulations and directives through EU supremacy (Art. 28 Syntagma). EUR-Lex provides Greek-language (EL) versions of all EU instruments.

## Access Methods

### CELEX Number (Primary)

Every EU legal instrument has a CELEX number. Format:
- Regulations: `32006R0561` (year + instrument type + sequential number)
- Directives: `31993L0013` (Directive 93/13 on unfair contract terms)

HTML full text (Greek):
```
https://eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:{celex}
```

JSON metadata:
```
https://eur-lex.europa.eu/legal-content/EL/TXT/?uri=CELEX:{celex}&format=json
```

### MCP Tool

The `eur-lex` MCP server (available in Claude Code) provides:
- `expert_search` — broad keyword search
- `resource://eurlex/document/{celex_number}` — direct document access

### Key Greek-Relevant CELEX Numbers

| Instrument | CELEX | Description |
|---|---|---|
| Directive 93/13/EEC | 31993L0013 | Unfair contract terms in consumer contracts |
| GDPR (Regulation 2016/679) | 32016R0679 | Data protection |
| Consumer Rights Directive 2011/83 | 32011L0083 | Consumer rights |
| Regulation 261/2004 | 32004R0261 | Air passenger rights |

## Citation Format

Per `law-packs/greece/jurisdiction.yaml`:
```
CELEX:{celex} — {eur_lex_url}
```

Example: `CELEX:31993L0013 — https://eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:31993L0013`

## Notes

- Always request EL (Greek) language version for Greek court filings
- EUR-Lex is the `eur_lex` fallback source in the Greek jurisdiction source priority
- EU regulations are directly applicable in Greek law (no transposition needed)
- Directives require national transposition — cite both the directive and the Greek implementing law
