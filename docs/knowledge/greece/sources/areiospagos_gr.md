---
title: "areiospagos.gr — Supreme Court of Greece"
jurisdiction: greece
source: "https://www.areiospagos.gr"
last_verified: "2026-04-08"
---

# areiospagos.gr — Research Report

> **URL:** https://areiospagos.gr/
> **Researched:** 2026-04-06 (via Chrome DevTools MCP — live POST/GET probes; supersedes earlier "DEAD" misclassification)
> **Operator:** Άρειος Πάγος (Supreme Court of Greece) — official site, served from IIS 8.5 (Windows)
> **Access model:** Free, no registration, no captcha, no rate-limit observed
> **Primary use:** Free full-text retrieval of Άρειος Πάγος (ΑΠ) decisions — civil and criminal — by number/year, department, and Google Custom Search

## Executive Summary

- **Free, official, fully working ΑΠ decision database** — earlier notes flagging this as "DEAD" / "non-functional 404" were **wrong**. The search lives at a non-obvious path (`/nomologia/apofaseis.asp`), which is why a previous probe of `/nomologia/apofaseis_list.asp` returned 404.
- Returns **complete HTML decision text** (skeptiko + operative part), often 80–120 KB per decision, encoded **windows-1253** (legacy Greek codepage — must be decoded explicitly when fetched programmatically).
- Live verification on 2026-04-06 confirmed all tested lead precedents return hits — each retrievable in under 500 ms.
- Three search modes coexist: (1) **POST criteria form** by department + number + year; (2) **Google Custom Search Engine** for full-text; (3) **thematic index** of criminal decisions (paginated, up to 2018).
- Provides **first-tier free access** to the same ΑΠ corpus that dsanet.gr (Isocrates) gates behind ΔΣΑ login and Qualex/Sakkoulas gate behind paid subscription. **Use this site BEFORE paying or asking the lawyer.**

## Site Overview

`areiospagos.gr` is the official institutional website of the Άρειος Πάγος. The architecture is unmistakably late-1990s: a 4-frame `<frameset>` (`top`, `contents`, `main`, `main1`) loading from `/INDEX_HD.htm`, `/INDEX_LF.htm`, `/LOGO.htm`, `/INDEX_FT.htm`, all served with `charset=windows-1253` and Google Analytics UA-20313280-4 still embedded. Pages run as classic ASP (`.asp`) on IIS 8.5.

The left frame (`INDEX_LF.htm`) is the navigation menu, listing 19 sections including Αρχική σελίδα, Ιστορικά στοιχεία, Δελτία Τύπου, **Αποφάσεις**, **Πολιτικές υποθέσεις**, **Ποινικές υποθέσεις**, Συνθέσεις Τμημάτων, Συνήθεις ερωτήσεις, **Προσωπικά δεδομένα** (links to a `44_2024_GDPR.pdf` privacy notice), Ανώτατο Δικαστικό Συμβούλιο, Επικοινωνία, and English.

## Access and Registration

- **Fully free**, no login, no email capture, no captcha.
- **No `robots.txt`** (returns IIS 404). No `noindex` meta on result pages (the `<meta name="robots" content="noindex">` line is HTML-commented out).
- No rate limit encountered across ~10 sequential POST queries from a single IP. Be considerate — this is a frail legacy server.
- HTTPS works on the apex domain (`https://areiospagos.gr/`); the `www.` prefix may not have a valid cert in all client contexts.

## Search Capabilities

Three independent search interfaces coexist:

### 1. POST criteria form — `/nomologia/apofaseis.asp` (the main one)

Form action: `https://areiospagos.gr/nomologia/apofaseis_result.asp?S=1` (POST, `application/x-www-form-urlencoded`).

| Field | Type | Values |
|-------|------|--------|
| `X_TMHMA` | select | `1`=ΠΟΛΙΤΙΚΕΣ, `2`=ΠΟΙΝΙΚΕΣ, `3`=Ν. 3068/2002, `4`=Ν. 4239/2014, `5`=Πράξεις Ν. 4842/2021, `6`=ΟΛΕΣ |
| `X_SUB_TMHMA` | select | `1`=ΟΛΕΣ, `2`=Α, `13`=Α1, `12`=Α2, `3`=Β, `4`=Β1, `5`=Β2, `6`=Γ, `7`=Δ, `8`=Ε, `9`=ΣΤ, `10`=Ζ, `11`=ΟΛΟΜΕΛΕΙΑ, `15`=Α Ποιν. Διακ., `16`=Β Ποιν. Διακ. |
| `x_number` | text | Decision number (e.g. `777`) |
| `X_TELESTIS_number` | select | `1`=`=`, `2`=`>=`, `3`=`<=` |
| `x_ETOS` | text | Year (e.g. `2022`) |
| `X_TELESTIS_ETOS` | select | `1`=`=`, `2`=`>=`, `3`=`<=` |
| `submit_krit` | submit | `Αναζήτηση` |

Results are an HTML table of links to `apofaseis_DISPLAY.asp?cd=<32-char session token>&apof=<num>_<year>&info=<dept>`. The `cd` token appears to be a per-query session key (regenerated on every search) but the URL is openly fetchable for the duration of the session.

### 2. Google Custom Search (full-text)

Embedded on the main `/Nomologia.asp` page; uses `cx=` parameter pointing to a Google CSE limited to `areiospagos.gr`. Best for keyword/concept searches when the decision number is unknown (e.g., search for "φυσιολογική φθορά μίσθιο").

### 3. Criminal thematic index — `/poiniko_search.asp`

Separate page with its own POST form (`x_number`, `x_etos`, `x_dik`, `x_ekth`, `submit_krit`). Provides browsing by criminal-law thematic categories. Coverage of the thematic index runs **up to 2018**; for criminal decisions after 2018 use the main `/nomologia/apofaseis.asp` form with `X_TMHMA=2`.

A parallel `/politiko.htm` page exists for civil cases — it is a styled landing page (modern CSS, 17 KB) summarising recent civil decisions with deeper links into the same `apofaseis_DISPLAY.asp` endpoint.

## Document Types

- **HTML decision text** — full skeptiko (reasoning) + operative part ("ΓΙΑ ΤΟΥΣ ΛΟΓΟΥΣ ΑΥΤΟΥΣ"), with composition of the panel and publication date. Verified on ΑΠ 777/2022 (99,939 bytes). No PDFs for decisions.
- **PDF documents** — the site does host some PDFs (e.g., `44_2024_GDPR.pdf` privacy notice, press releases, court regulations) but **not for decisions themselves**.
- **Δελτία Τύπου** (press releases) — separate section, modern HTML, summaries of important rulings.
- **Γνωμοδοτήσεις Εισαγγελέα Α.Π.** (prosecutor opinions) and **Εγκύκλιοι** — listed in left nav.

## Programmatic Access

### curl example — search for a decision by number/year

```bash
curl -X POST 'https://areiospagos.gr/nomologia/apofaseis_result.asp?S=1' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  --data-urlencode 'X_TMHMA=6' \
  --data-urlencode 'X_SUB_TMHMA=1' \
  --data-urlencode 'X_TELESTIS_number=1' \
  --data-urlencode 'x_number=777' \
  --data-urlencode 'X_TELESTIS_ETOS=1' \
  --data-urlencode 'x_ETOS=2022' \
  --data-urlencode 'submit_krit=Αναζήτηση' \
  | iconv -f WINDOWS-1253 -t UTF-8 > ap_results.html
```

The response contains `<a href="apofaseis_DISPLAY.asp?cd=...&apof=777_2022&info=...">777/2022</a>` links. Follow each (relative to `/nomologia/`) with a plain GET to retrieve the full decision text.

### Python example (with charset handling)

```python
import requests, urllib.parse
r = requests.post(
    'https://areiospagos.gr/nomologia/apofaseis_result.asp?S=1',
    data={'X_TMHMA': '6', 'X_SUB_TMHMA': '1',
          'X_TELESTIS_number': '1', 'x_number': '777',
          'X_TELESTIS_ETOS': '1', 'x_ETOS': '2022',
          'submit_krit': 'Αναζήτηση'.encode('windows-1253')})
r.encoding = 'windows-1253'   # critical
html = r.text
```

### Chrome DevTools MCP example (when JS is needed)

```javascript
// Inside mcp__chrome-devtools__evaluate_script — handles cookies + frameset context
const body = new URLSearchParams({
  X_TMHMA: '6', X_SUB_TMHMA: '1',
  X_TELESTIS_number: '1', x_number: '985',
  X_TELESTIS_ETOS: '1',  x_ETOS: '2020',
  submit_krit: 'Αναζήτηση'
});
const r = await fetch('https://areiospagos.gr/nomologia/apofaseis_result.asp?S=1',
  {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: body.toString()});
return new TextDecoder('windows-1253').decode(await r.arrayBuffer());
```

## Limitations and Quirks

- **windows-1253 encoding** — fetching without explicit decoding produces mojibake. UTF-8 clients (curl by default) must pipe through `iconv` or set `r.encoding = 'windows-1253'`.
- **Frameset architecture** — direct browser bookmarks of `apofaseis.asp` show only the form, not the navigation. Search engines also struggle to index frameset content.
- **Empty-field SQL behaviour** — submitting the form with empty `x_number` and `x_ETOS` returns a results page that effectively concatenates user input into a SQL `WHERE` clause; this surfaces as either an "Δεν βρέθηκαν εγγραφές" message or an ASP error trace. **Do not** stress-test or attempt injection — the site is the official Supreme Court and any abuse would be visible in their access logs.
- **`cd=` session token in result URLs** — opaque, regenerated per query, but the URL remains valid for follow-up GETs within the same session/IP for at least several minutes. For long-running scrapes, re-issue the POST whenever a `cd=` URL stops resolving.
- **No bulk download** — there is no XML/JSON feed, no "all decisions in 2024" export, no sitemap of decisions. Each decision must be requested individually.
- **Coverage of older decisions is incomplete** — the database is strongest from the mid-2000s onward; pre-2000 decisions may be missing.
- **No decision-level metadata API** — title, parties, publication date, and panel composition must be parsed out of the HTML.
- **IIS 8.5 + ASP** — server is old; expect occasional 500s and slow responses. No CDN.
- **Earlier "site DEAD" claim** was wrong because the prior probe hit `/nomologia/apofaseis_list.asp` (a path that does not exist) instead of the actual `/nomologia/apofaseis.asp`.

## Comparison vs dsanet.gr (and Qualex / Sakkoulas)

| Aspect | areiospagos.gr | dsanet.gr (Isocrates) | Qualex / Sakkoulas-Online |
|--------|----------------|------------------------|---------------------------|
| Cost | **Free** | Free for ΔΣΑ members only (login wall) | Paid subscription |
| Officiality | **Court itself** (most authoritative) | Athens Bar | Commercial publisher |
| ΑΠ decisions full text | Yes — verified on multiple cited cases | Yes (broader, including Ειρηνοδικείο) | Yes (with editorial summaries) |
| Ειρηνοδικείο / Πρωτοδικείο | **No** | Yes | Partial |
| Editorial headnotes | No | Some | **Yes** (curated) |
| Cross-linking to articles | No | Yes (article-by-article) | Yes (best in class) |
| Bulk export / API | No | No | Subscription tier dependent |
| Search by free text | Google CSE only | Yes (full-text) | Yes (faceted) |
| Search by article cited | No | Yes | Yes |
| Citation network | No | Limited | Yes |
| Login required | **No** | Yes (ΔΣΑ) | Yes (paid) |

**Bottom line:** For **retrieving the text of an ΑΠ decision when you already know the number/year**, areiospagos.gr is now the **first stop** — free, official, no login. For **finding decisions by article cited or by topic**, dsanet.gr (via the lawyer) and Qualex remain superior.

## Recommended Workflow

1. Build a small Python or Node script that iterates the citation list and POSTs each `(num, year)` pair to `/nomologia/apofaseis_result.asp?S=1`.
2. Parse the result HTML for `apofaseis_DISPLAY.asp?cd=...` links.
3. GET each link, decode windows-1253, save to `case_law/AP_<num>_<year>_<dept>.html`.
4. For each, extract the operative paragraph and add to the case law file as a verified quote with the official URL.
5. Cross-check the operative wording against any quotes already in claim or counter-claim files — flag any paraphrase mismatches.

### Strategic value

- **Eliminates a vault gap**: prior workflow assumed ΑΠ text was paywalled / login-walled; this is no longer true.
- **Authoritative citation**: a court annex citing `https://areiospagos.gr/nomologia/apofaseis_DISPLAY.asp?...` is the most defensible link possible (it is the court citing itself).
- **Verifies paraphrases**: catches any case where memory or notes have a quote subtly wrong.
- **Reduces dependency** on Qualex (paid) and dsanet.gr (lawyer login) for the simplest task — full text retrieval by number.
