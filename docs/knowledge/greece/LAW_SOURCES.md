---
title: "Greek Law Source Discovery & Download Strategy"
jurisdiction: greece
source: "https://www.et.gr, https://www.kodiko.gr, https://eur-lex.europa.eu (researched 2026-04-04)"
last_verified: "2026-04-08"
---

# Greek Law Source Discovery & Download Strategy

> **Purpose:** Map every authoritative Greek and EU law source, document what each contains, how to access it programmatically, and provide a prioritised download strategy for building a Legal Authority Vault that grounds AI citations in verified law text.
>
> **Researched:** 2026-04-04 (live HTTP probes + cross-reference with `docs/knowledge/greece/sources/`)

---

## Table of Contents

1. [What Is the Legal Authority Vault?](#1-what-is-the-legal-authority-vault)
2. [Greek Law Sources](#2-greek-law-sources)
3. [EU and International Sources](#3-eu-and-international-sources)
4. [Law Type Taxonomy — Applicability to Civil Disputes](#4-law-type-taxonomy)
5. [Download Strategy Table](#5-download-strategy-table)
6. [Priority Matrix — Hot vs Cold Vault](#6-priority-matrix)
7. [Implementation Recommendations](#7-implementation-recommendations)
8. [Anti-Hallucination Protocol](#8-anti-hallucination-protocol)

---

## 1. What Is the Legal Authority Vault?

An AI system that cites law without grounding it in verified text will hallucinate article numbers, invent case holdings, and confabulate statutory language. The Legal Authority Vault solves this by pre-downloading authoritative law text and storing it in two tiers:

**Hot Vault** — 30–50 key articles stored as markdown, loaded directly into AI context. Zero retrieval latency. Used for every AI session. Contains only the articles that appear repeatedly in the dispute type.

**Cold Vault** — Large corpora (full ΑΚ, all ΑΠ decisions, all HDPA decisions, all CJEU GDPR cases) stored as structured files and indexed for semantic retrieval (RAG). The AI queries this only when it needs to cite something outside the hot vault.

Together they eliminate two failure modes:
- Citation hallucination: citing an article that does not say what the AI claims
- Completeness gaps: missing a precedent that would hurt or help the case

---

## 2. Greek Law Sources

### 2.1 ΦΕΚ — Εθνικό Τυπογραφείο (et.gr)

**What it contains:** Every piece of legislation promulgated in Greece since the modern state. This includes:
- Νόμοι (Laws) — e.g., N. 4601/2019 (spin-off), N. 5177/2025 (DTD/stamp duty)
- Προεδρικά Διατάγματα (ΠΔ) — e.g., ΠΔ 212/2006 (technical safety)
- Υπουργικές Αποφάσεις (ΥΑ) and Κοινές Υπουργικές Αποφάσεις (ΚΥΑ)
- ΦΕΚ corporate publications (company registrations, spin-offs)

**Live probe findings:**
- Site: `https://et.gr` — responds HTTP 200, Apache 2.4.65, WordPress-backed
- The site exposes a WordPress REST API at `https://et.gr/wp-json/wp/v2/`
- Search endpoint: `https://et.gr/search/{law_number}/{year}/` returns results as HTML (no structured JSON for law content)
- Searching "5177/2025" returned "Nothing Found" via the search route — the ΦΕΚ content itself is served through a separate subdomain `search.et.gr` with its own interface
- No public REST API with JSON law text was found; the WordPress API covers blog-style posts only

**Actual access method:**
- Primary: `https://search.et.gr` — the authoritative ΦΕΚ search portal
  - Select: Τύπος (Νόμος / ΠΔ / ΚΥΑ), Τεύχος (Α΄ / Β΄ / Γ΄), year, number
  - Downloads PDFs of the original gazette publication (scanned or born-digital)
  - Company search: search by ΑΦΜ to find all ΦΕΚ publications for an entity
- Recent ΦΕΚ (post-2000): free PDF download
- Historical ΦΕΚ (pre-2000): partial digitisation, some require visiting Εθνικό Τυπογραφείο

**Format:** PDF (Greek text). Born-digital PDFs for post-~2010 laws are text-selectable. Older issues are scanned images requiring OCR.

**Limitations for vault use:**
- PDFs contain the exact promulgated text, which may since have been amended
- Consolidated (codified) text is NOT available on et.gr — only the original enactment
- No machine-readable API; must scrape or manually download
- Search interface requires human navigation; not scriptable via documented API

**What to download (typical tenancy/civil dispute):**
- N. 4601/2019 (ΦΕΚ Α΄ 44/26.03.2019) — spin-off law, Arts. 65 + 70
- N. 5177/2025 (ΦΕΚ Α΄ 21/14.02.2025) — DTD/stamp duty reform, Art. 16
- N. 2251/1994 (ΦΕΚ Α΄ 191/16.11.1994) — consumer protection (original enactment)
- ΠΔ 212/2006 — technical safety standards
- Any relevant ΦΕΚ corporate publications for the defendant entity (spin-off announcement)

**Frequency:** One-time for each law (static historical documents). Only re-download if an amending law is passed.

---

### 2.2 Kodiko.gr

**What it contains:** Consolidated (codified) Greek law text in real time. When a law article is amended, kodiko.gr updates the displayed text to reflect the current version. This is what you want for citation — not the original ΦΕΚ enactment, but the currently operative text.

**Live probe findings:**
- Site: `https://www.kodiko.gr` — responds HTTP 200 after redirect from http
- Direct article URLs work: `https://www.kodiko.gr/nomologia/document_navigation/[ID]/[slug]`
- Free browsing without login confirmed; HTML content downloadable
- Full article text is available in HTML; response size ~40KB for law text pages
- Login/subscription required for: commentary (σχόλια), case law links, AI assistant

**Authoritative status:** Kodiko.gr is unofficial (not published by the Greek state) but widely cited by lawyers as a reliable consolidation service. It should be used to verify current article text, not as the primary citation source in court documents. Primary citation = law number + ΦΕΚ reference; kodiko.gr = verification tool.

**Scraping approach:** Direct URL construction works because kodiko.gr uses predictable slugs:
```
https://www.kodiko.gr/nomologia/document_navigation/[doc_id]/astikos-kodikas-arthro-[N]
```
For example, Art. 592 ΑΚ: `https://www.kodiko.gr/nomologia/document_navigation/168266/astikos-kodikas-arthro-592`

Python `requests` + BeautifulSoup can extract article text. No API key required for public text.

**What to download:** All hot vault ΑΚ and ΚΠολΔ articles (see Section 6). The text is short (typically 100–400 words per article) and can be stored as markdown directly.

**Format:** HTML → convert to markdown via `html2text` or `markdownify`

**Cost:** Free for law text. Subscription (~€30/month) unlocks commentary and case law links — worth considering for the Phase 3 research phase.

---

### 2.3 Lawspot.gr

**What it contains:** A legal news and law text portal. Provides:
- Law text (Νόμοι, ΚΥΑ, ΠΔ) with article-level URLs
- Daily Greek legal news (new court decisions, legislative developments)
- HDPA decisions (partial coverage through news articles)
- Law 2251/1994 articles (confirmed accessible via direct URL)

**Live probe findings:**
- Site: `https://www.lawspot.gr` — responds HTTP 200 after redirect
- Direct article URL confirmed accessible: `https://www.lawspot.gr/nomikes-plirofories/nomothesia/n-2251-1994/arthro-9`
  - Response: 24KB HTML, contains article text
  - Note: the response for Art. 9 of N. 2251/1994 returned "Κώδικας Καταναλωτικής Δεοντολογίας" content — URL structure may differ from expectation; verify each URL manually
- No public API documented; web scraping works for law text pages

**Authoritative status:** Same as kodiko.gr — unofficial consolidation, useful for verification and monitoring. Not authoritative for court citation purposes.

**Best use for civil dispute research:**
- Monitor `https://www.lawspot.gr/nomika-nea/` daily for new ΑΠ decisions on relevant topics
- Verify law text for hot vault articles before loading into AI context
- Find HDPA decision news coverage when direct HDPA site access fails

**Format:** HTML. Text content easily extractable.

---

### 2.4 ΙΣΟΚΡΑΤΗΣ / DSANet (dsanet.gr)

**What it contains:** The Athens Bar Association's (ΔΣΑ) legal information database. This is the primary Greek-language case law repository for practising lawyers.

**Live probe findings:**
- Site: `https://dsanet.gr` — responds HTTP 200; title confirmed "ΙΣΟΚΡΑΤΗΣ Τράπεζα Νομικών Πληροφοριών - Καλωσήρθατε"
- The `/apps/index.jsp` endpoint redirects to `https://apps.olomeleia.gr` — an SSO login page (Keycloak authentication)
- The `/Epikairothta/Nomologia/nomologia-latest.html` path also loads from dsanet.gr domain but displays a login-gated Angular app
- No public search API confirmed; all decision retrieval requires ΔΣΑ member login

**Coverage:** All levels of Greek courts:
- Άρειος Πάγος (ΑΠ) — Supreme Court
- Εφετεία — Courts of Appeal
- Πρωτοδικεία — Courts of First Instance
- Ειρηνοδικεία — Justice of the Peace (critical for claims under €20,000)
- Administrative courts (ΣτΕ, διοικητικά δικαστήρια)

**Access reality:** ΔΣΑ membership required. The claimant cannot access directly. Options:
1. Lawyer access (the most practical path for research)
2. Some ΑΠ decisions are published with free excerpts on dsanet.gr for public users — but coverage is partial and unpredictable
3. olomeleia.gr (the new ΔΣΑ portal) appears to be the successor system — also login-gated

**What to request via lawyer:**
- ΑΠ decisions on Art. 592 ΑΚ (normal wear and tear), last 10 years
- ΑΠ decisions on Art. 576 ΑΚ (rent reduction for defects)
- ΑΠ decisions on Art. 604-606 ΑΚ (security deposit return)
- Ειρηνοδικείο decisions on deposit deductions in relevant jurisdiction
- Key ΑΠ decisions: 777/2022, 985/2020, 938/2018, 806/2023 (full text)

---

### 2.5 Areiospagos.gr (Supreme Court Official Site) — ✅ ALIVE (corrected 2026-04-06)

**What it contains:** The official website of the Άρειος Πάγος. In practice, the most authoritative free source for ΑΠ decision text.

**Corrected live probe findings (2026-04-06, Chrome DevTools MCP):**
- Site: `https://areiospagos.gr/` — fully functional, frameset architecture (charset windows-1253), running classic ASP on IIS 8.5
- The earlier "DEAD" verdict was wrong — it probed `/nomologia/apofaseis_list.asp` (a path that does not exist). The actual decision search lives at **`/nomologia/apofaseis.asp`** — POST form with fields `X_TMHMA`, `X_SUB_TMHMA`, `x_number`, `x_ETOS`, `X_TELESTIS_number`, `X_TELESTIS_ETOS`, `submit_krit`. Action: `/nomologia/apofaseis_result.asp?S=1`.
- Verified retrieval of full HTML decision text for key ΑΠ precedents. Decision pages return ~80–120 KB of skeptiko + operative part.
- Three search modes: (1) POST criteria form, (2) Google CSE for full-text, (3) thematic criminal index up to 2018.
- Free, no login, no captcha, no rate limit observed.

**Practical conclusion:** Areiospagos.gr is a **first-tier free source** for ΑΠ decision text retrieval. Use it BEFORE dsanet.gr (login-walled) or Qualex/Sakkoulas (paid). See `docs/knowledge/greece/sources/areiospagos_gr.md` for the full report including curl/Python/Chrome DevTools MCP examples.

**What is also accessible on areiospagos.gr:** Press releases (Δελτία Τύπου), court regulations, GDPR notice, prosecutor opinions, and the criminal thematic index.

---

### 2.6 HDPA — Αρχή Προστασίας Δεδομένων Προσωπικού Χαρακτήρα (dpa.gr / apdpx.gr)

**What it contains:** All decisions of the Greek Data Protection Authority, spanning from its establishment to present. Directly relevant to data protection claims: enforcement decisions on GDPR Art. 15 (access rights), Art. 5 (purpose limitation), Art. 13/14 (transparency), and Art. 82/83 (liability and penalties).

**Key precedents for data protection disputes:**
- HDPA 36/2021 — rental/property sector GDPR enforcement
- HDPA 1/2025 — recent enforcement; data access refusal
- HDPA 31/2025 — recent; unlawful retention
- HDPA 30/2024 — blanket refusal to provide data
- HDPA 27/2024 — proportionality of access

**Live probe findings:**
- `https://www.apdpx.gr/decisions/apofaseis` — returns empty body (0 bytes); the old domain appears to redirect or fail
- `https://www.dpa.gr/el/decisions` — returns 3,662 bytes (likely JavaScript SPA shell); actual decision content not accessible without JavaScript rendering
- `https://www.dpa.gr/en/decisions.html` — returns 3,667 bytes (same SPA issue)
- The HDPA site is a JavaScript-rendered Single Page Application; raw HTTP requests return only the app shell, not decision content

**Access method for vault use:**
- Decisions are published as PDFs on the HDPA site, accessible when JavaScript renders the page
- Chrome DevTools MCP can navigate the rendered SPA and download individual decision PDFs
- Search: `site:dpa.gr filetype:pdf` in a search engine to locate direct PDF URLs
- Lawspot.gr and Qualex publish HDPA decision summaries (searchable without SPA)
- Direct PDF URL pattern (confirmed in prior research): `https://www.dpa.gr/sites/default/files/[year]/[decision-id].pdf`

**What to download for vault:**
- HDPA 36/2021 (rental sector)
- HDPA 1/2025, 31/2025, 30/2024, 27/2024 (frequently cited in data protection claims)
- Any HDPA decision involving: landlord GDPR compliance, security deposit data, inspection photo data subject access requests

**Format:** PDF (Greek text, usually born-digital and text-selectable post-2019)

---

### 2.7 Qualex / Νομική Βιβλιοθήκη (nb.org)

**What it contains:** The most comprehensive Greek commercial legal database. Subscription required.
- 260,000+ court decisions (all levels, all topics)
- 99,000+ administrative documents
- 21 legal journals (including Ελληνική Δικαιοσύνη, Lex&Forum, Ιδιωτικό Δίκαιο)
- Doctrine (βιβλιογραφία) linked to articles
- AI chat (chatbook.nb.org) for exploratory queries
- "Αναζήτηση με νομοθετική διάταξη" — search by article number → all decisions citing that article

**Access:** Subscription (~€80–150/month for individual lawyers). The claimant does not have direct access. A lawyer with Qualex access can retrieve specific decisions on request.

**Priority retrieval list via lawyer:**
1. ΑΠ 777/2022 — full text (most recent ΑΚ Art. 592 + depreciation framework)
2. ΑΠ 985/2020 — full text (primary depreciation decision)
3. ΑΠ 938/2018 — family use = agreed use
4. ΑΠ 806/2023 — moral damages without medical evidence (Art. 932 ΑΚ)
5. ΑΠ 362/2023 — universal succession under N. 4601/2019
6. All ΑΠ decisions on Arts. 576, 592, 602, 904 ΑΚ in tenancy context, 2015–2026

---

### 2.8 Sakkoulas-Online (sakkoulas-online.gr)

**What it contains:** Legal publisher database (not sakolaw.com which is a parked domain).
- Ελληνική Δικαιοσύνη journal (case law)
- Επιθεώρηση Ακινήτων journal (real estate law — directly relevant)
- Legal doctrine and commentary
- Smaller decision corpus than Qualex but stronger on doctrine

**Access:** Subscription. Useful for: tenancy law doctrine (σχόλια on Arts. 592, 576, 604), depreciation methodology commentary, deposit deduction jurisprudence.

---

## 3. EU and International Sources

### 3.1 EUR-Lex (eur-lex.europa.eu)

**What it contains:** The official EU law repository. All EU legislation, CJEU case law, GDPR, Directives, Regulations, and the EU Official Journal.

**Live probe findings (confirmed working):**
- `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32016R0679` — HTTP 200, 806,546 bytes, confirmed "Article 15" present
- `https://eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:32016R0679` — HTTP 200, 841,244 bytes, confirmed Greek text with "Άρθρο" structure
- `https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:62016CJ0434` — HTTP 200, 83,269 bytes, confirmed "Nowak" text (C-434/16 Nowak judgment)
- Publications Office SPARQL endpoint: `https://publications.europa.eu/webapi/rdf/sparql` — confirmed live, returns proper JSON-LD

**CELEX number system:**
```
32016R0679        → Regulation 2016/679 (GDPR)
62016CJ0434       → Case C-434/16 (Nowak)
62022CJ0203       → Case C-203/22
62021CJ0487       → Case C-487/21
62021CJ0579       → Case C-579/21 (Pankki S)
62021CJ0154       → Case C-154/21
62022CJ0307       → Case C-307/22
32011L0083        → Consumer Rights Directive 2011/83
32005L0029        → Unfair Commercial Practices Directive 2005/29
12016P/TXT        → EU Charter of Fundamental Rights
```

**Download method (programmatic):**
```python
import requests

def download_eurlex(celex, lang='EL', fmt='HTML'):
    url = f"https://eur-lex.europa.eu/legal-content/{lang}/TXT/{fmt}/?uri=CELEX:{celex}"
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    return r.text  # Full HTML of the document

# GDPR in Greek
gdpr_el = download_eurlex('32016R0679', lang='EL', fmt='HTML')

# Nowak judgment in English
nowak_en = download_eurlex('62016CJ0434', lang='EN', fmt='HTML')
```

No API key required. Rate limiting is gentle; one request per second is safe.

**Available formats per document:**
- HTML (best for text extraction and markdown conversion)
- PDF (official, with proper formatting)
- XML (FORMEX 4 format — structured but complex)
- TXT (plain text, no formatting)

**Languages available:** All 24 EU official languages, including Greek (EL) and English (EN). For vault use: download both EL (for Greek court citations) and EN (for AI reasoning which performs better in English).

**SPARQL API for structured queries:**
```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?work ?title
WHERE {
  ?work cdm:work_is_about_concept_eurovoc <http://eurovoc.europa.eu/5455> ;  # GDPR concept
        cdm:expression_title ?title .
  FILTER(lang(?title) = 'en')
}
LIMIT 10
```
Endpoint: `https://publications.europa.eu/webapi/rdf/sparql`

**Cost:** Free. No registration required.

---

### 3.2 CURIA (curia.europa.eu → infocuria.curia.europa.eu)

**What it contains:** Official CJEU case database. All Court of Justice and General Court judgments, opinions, and orders.

**Live probe findings:**
- Old URL `https://curia.europa.eu` now permanently redirects (301) to `https://infocuria.curia.europa.eu`
- `https://infocuria.curia.europa.eu/tabs/redirect/juris/liste.jsf?num=C-434/16` — HTTP 200, 130,758 bytes — confirmed working (listing/search results page)
- The CURIA interface is JSF-based (Java Server Faces) — not easily scriptable via direct HTTP

**Practical access:** Use EUR-Lex instead of CURIA for programmatic downloads. EUR-Lex hosts the same CJEU judgments under their CELEX codes, in HTML/PDF/TXT, with confirmed download functionality. CURIA's own download is less reliable for automation.

**Key cases for vault (download via EUR-Lex):**
| Case | CELEX | Topic |
|------|-------|-------|
| C-434/16 Nowak | 62016CJ0434 | "Relating to" test for personal data |
| C-203/22 | 62022CJ0203 | Blanket refusals prohibited (Art. 15) |
| C-487/21 | 62021CJ0487 | Right to copy of documents |
| C-579/21 Pankki S | 62021CJ0579 | Third-party identity in Art. 15 |
| C-154/21 | 62021CJ0154 | Recipient identification requirement |
| C-307/22 | 62022CJ0307 | Healthcare data access |

---

### 3.3 HUDOC — European Court of Human Rights (hudoc.echr.coe.int)

**What it contains:** All ECHR judgments, decisions, advisory opinions, and resolutions from the European Court of Human Rights (Council of Europe, not EU).

**Live probe findings:**
- HUDOC REST API confirmed live: `https://hudoc.echr.coe.int/app/query/results`
- Test query for recent judgments returned: `{"resultcount":101535,...}` — 101,535 judgment records
- Query format: `query=(documentcollectionid2:"JUDGMENTS")&select=itemid,docname,kpdate&sort=kpdate Descending`
- Name search works: query `(docname:"Volkov")` returned 71 results with item IDs
- **The API requires GET requests with specific field names; the initial test with wrong parameters returned an error**

**Working API query structure:**
```python
import requests

def search_hudoc(query_term, max_results=10):
    params = {
        'query': f'(docname:"{query_term}") AND (documentcollectionid2:"JUDGMENTS")',
        'select': 'itemid,docname,kpdate,kpdateAsText',
        'sort': 'kpdate Descending',
        'start': 0,
        'length': max_results
    }
    r = requests.get('https://hudoc.echr.coe.int/app/query/results', params=params)
    return r.json()

# Download full judgment text
def get_judgment_text(item_id):
    # item_id format: "001-152988"
    url = f"https://hudoc.echr.coe.int/eng?i={item_id}"
    # Returns HTML page with embedded judgment text
    return requests.get(url).text
```

**Relevant ECHR case law for rental/property disputes:**
- Art. 8 ECHR (right to private life / home) — supports tenant's right to privacy regarding inspection photos taken without their presence
- Art. 1 Protocol 1 ECHR (peaceful enjoyment of possessions) — deposit withholding as interference with property rights
- Art. 6 ECHR (fair trial) — access to evidence principles (reinforces GDPR Art. 15 argument that evidence used against a party must be disclosed)

**Specific case searches:**
- "security deposit" + tenant → Art. 1 P1 cases
- "data protection" + "right of access" → Art. 8 cases overlapping with GDPR

**Format:** HTML (judgment text embedded in page), also available as PDF and DOCX for individual judgments

**Cost:** Free. API is public and documented.

---

## 4. Law Type Taxonomy

Applicability of each law type to Greek civil disputes (tenancy deposit as reference scenario):

| Law Type | Key Provisions | Applicable? | Why |
|----------|---------------|-------------|-----|
| Civil Code (ΑΚ) | Arts. 281, 288, 576, 592, 602, 904 | **YES — CORE** | Governs the entire tenancy relationship, deposit, tort, limitation period |
| Civil Procedure (ΚΠολΔ) | Arts. 216, 237, 338-340, 442, 591-614 | **YES — CORE** | Eirinodikio pleading requirements, burden of proof, adverse inference |
| Consumer Protection | N. 2251/1994 Arts. 1, 9γ, 9δ, 9ε | **YES — HIGH** | Professional landlord; unfair commercial practices |
| GDPR | Reg. 2016/679 Arts. 4, 6, 13-15, 17, 82, 83 | **YES — HIGH** | Data protection violations; Art. 82 damages claim |
| N. 4624/2019 | Art. 38 (DPO criminal liability) | **YES — ESCALATION** | Corporate officer personal criminal exposure |
| Company Law | N. 4601/2019 Arts. 65 §4, 70 §2 | **YES — CRITICAL** | Spin-off joint liability; dual defendant strategy; universal succession |
| Tax Law | N. 5177/2025 Art. 16; AADE E.2094/2025 | **YES — HIGH** | Stamp duty violations; AADE referral |
| Property Law | Arts. 592-612 ΑΚ | **YES — CORE** | Tenancy chapter of Civil Code |
| Criminal Code (ΠΚ) | Arts. 362-363 (defamation), 386 (fraud) | **POSSIBLE — PHASE 4** | Fraud exposure for coordinated false positions; use last |
| Greek GDPR Implementation | N. 4624/2019 | **YES — HDPA** | National GDPR implementation law; Art. 38 criminal referral |
| DTD / Stamp Duty | N. 5177/2025; formerly N. 3557/2007 | **YES — FORENSIC** | Stamp duty abolished 01/12/2024; invoice date verification |
| Technical Safety | ΠΔ 212/2006 | **YES** | Demolition without permit; Art. 914 ΑΚ tort |
| Consumer Rights Dir. | 2011/83/EU | **SUPPLEMENTARY** | Reinforces N. 2251/1994 consumer protection |
| Unfair Commercial Practices | 2005/29/EU | **SUPPLEMENTARY** | Background for Art. 9δ N. 2251/1994 unfair practice |
| EU Charter | Arts. 7 (privacy), 38 (consumer), 47 (remedy) | **SUPPLEMENTARY** | Grounds consumer and GDPR arguments in constitutional rights |
| ECHR | Art. 8 (privacy), Art. 1 P1 (property) | **SUPPLEMENTARY** | Backup constitutional framing; useful in Ombudsman submissions |
| Constitutional Law | Art. 25 Syntagma | **SUPPLEMENTARY** | Proportionality principle; limits on deposit withholding |
| N. 4967/2022 | Arts. 534-561 (product warranty) | **TARGETED** | 2-year warranty for appliances; more precise than L. 2251/1994 alone |

---

## 5. Download Strategy Table

| Source | What to Download | Format | Method | One-time / Periodic | Vault Tier |
|--------|-----------------|--------|--------|--------------------|----|
| EUR-Lex | GDPR (32016R0679) — EL + EN full text | HTML | `requests.get()` with CELEX URL | One-time; check for corrigenda annually | Hot (key articles) + Cold (full text) |
| EUR-Lex | C-434/16 Nowak full judgment | HTML | `requests.get()` CELEX URL | One-time | Cold |
| EUR-Lex | C-203/22, C-487/21, C-579/21, C-154/21, C-307/22 judgments | HTML | Same | One-time | Cold |
| EUR-Lex | Consumer Rights Dir. 2011/83 (EL+EN) | HTML | Same | One-time | Cold |
| EUR-Lex | Unfair Practices Dir. 2005/29 (EL+EN) | HTML | Same | One-time | Cold |
| EUR-Lex | EU Charter (12016P/TXT) — EL+EN | HTML | Same | One-time | Cold |
| Kodiko.gr | Art. 592, 281, 288, 576, 602, 904 ΑΚ | HTML→MD | `requests` + `html2text` | One-time + verify before Phase 3 | Hot |
| Kodiko.gr | Art. 216, 237, 338-340, 442 ΚΠολΔ | HTML→MD | Same | One-time + verify | Hot |
| Kodiko.gr | N. 2251/1994 Arts. 1, 9γ, 9δ, 9ε | HTML→MD | Same | One-time + verify | Hot |
| Kodiko.gr | N. 4601/2019 Arts. 65, 70 | HTML→MD | Same | One-time + verify | Hot |
| Kodiko.gr | N. 5177/2025 Art. 16 | HTML→MD | Same | One-time + verify | Hot |
| Kodiko.gr | N. 4624/2019 Art. 38 | HTML→MD | Same | One-time | Hot |
| Kodiko.gr | Full ΑΚ (2000+ articles) | HTML→MD | Bulk scrape with rate limiting | One-time | Cold |
| Kodiko.gr | Full ΚΠολΔ (1000+ articles) | HTML→MD | Bulk scrape | One-time | Cold |
| et.gr (search.et.gr) | N. 4601/2019 original ΦΕΚ PDF | PDF | Manual download | One-time | Cold (reference) |
| et.gr | N. 5177/2025 original ΦΕΚ PDF | PDF | Manual download | One-time | Cold |
| et.gr | Any spin-off ΦΕΚ publication for defendant entity | PDF | Manual download | One-time | Cold (evidence) |
| HDPA (dpa.gr) | Decisions 36/2021, 1/2025, 31/2025, 30/2024, 27/2024 | PDF | Chrome DevTools MCP navigate + download | One-time per decision | Cold |
| Lawspot.gr | Law 2251/1994 Art. 9 (consumer) | HTML→MD | `requests` | One-time + verify | Hot backup |
| HUDOC | Art. 8 + Art. 1 P1 tenant-relevant decisions | HTML | HUDOC API search → document fetch | One-time research phase | Cold |
| Qualex (via lawyer) | ΑΠ 777/2022, 985/2020, 938/2018, 806/2023, 362/2023 | PDF | Manual retrieval via lawyer | One-time per decision | Cold |
| Qualex (via lawyer) | All ΑΠ on Arts. 592, 576, 602 (2015–2026) | PDF | Bulk retrieval via lawyer | One-time research phase | Cold |
| Isocrates (via lawyer) | Ειρηνοδικείο decisions on deposit deductions | PDF | Via lawyer access | One-time research phase | Cold |

---

## 6. Priority Matrix — Hot vs Cold Vault

### Tier 1: Hot Vault — Load Into Every AI Session

These articles appear in every analytical task. They must be instantly available, not retrieved. Target: 35–45 articles as markdown, ~50KB total context size.

**Greek Civil Code (ΑΚ) — Tenancy Core**
| Article | Topic | Source URL |
|---------|-------|-----------|
| Art. 281 ΑΚ | Abuse of rights | kodiko.gr |
| Art. 288 ΑΚ | Good faith (Treu und Glauben) | kodiko.gr |
| Art. 297 ΑΚ | Positive damage | kodiko.gr |
| Art. 298 ΑΚ | Lucrum cessans / lost profit | kodiko.gr |
| Art. 330 ΑΚ | Negligence standard | kodiko.gr |
| Art. 361 ΑΚ | Contract freedom | kodiko.gr |
| Art. 576 ΑΚ | Rent reduction for defects | kodiko.gr |
| Art. 592 ΑΚ | Normal wear and tear | kodiko.gr |
| Art. 602 ΑΚ | 6-month limitation period | kodiko.gr |
| Art. 904 ΑΚ | Unjust enrichment | kodiko.gr |
| Art. 914 ΑΚ | Tort (general) | kodiko.gr |
| Art. 932 ΑΚ | Moral damages | kodiko.gr |

**Greek Civil Procedure (ΚΠολΔ) — Procedure Core**
| Article | Topic | Source URL |
|---------|-------|-----------|
| Art. 216 ΚΠολΔ | Requirements for a valid αγωγή | kodiko.gr |
| Art. 237 ΚΠολΔ | Statement of claim, evidence rules | kodiko.gr |
| Art. 338 ΚΠολΔ | Burden of proof | kodiko.gr |
| Art. 339 ΚΠολΔ | Adverse inference from suppressed evidence | kodiko.gr |
| Art. 340 ΚΠολΔ | Evaluation of circumstantial evidence | kodiko.gr |
| Art. 442 ΚΠολΔ | Small claims procedure | kodiko.gr |
| Arts. 591-614 ΚΠολΔ | Rental dispute special procedure | kodiko.gr |

**Consumer and Corporate Law**
| Provision | Topic | Source URL |
|-----------|-------|-----------|
| N. 2251/1994 Art. 1 | Consumer definition; professional vendor | lawspot.gr |
| N. 2251/1994 Art. 9γ | Unfair commercial practices (general clause) | lawspot.gr |
| N. 2251/1994 Art. 9δ | Misleading commercial practices | lawspot.gr |
| N. 2251/1994 Art. 9ε | Aggressive commercial practices | lawspot.gr |
| N. 4601/2019 Art. 65 §4 | Joint and several liability after spin-off (5 years) | kodiko.gr |
| N. 4601/2019 Art. 70 §2 | Universal succession — automatic contract transfer | kodiko.gr |
| N. 5177/2025 Art. 16 | Stamp duty (abolished 01/12/2024) | kodiko.gr |
| N. 4624/2019 Art. 38 | DPO and corporate officer criminal liability | kodiko.gr |

**GDPR Core Articles (in Greek — EL — for HDPA submissions)**
| Article | Topic | Source |
|---------|-------|--------|
| GDPR Art. 4 | Definitions (personal data, controller, processor) | EUR-Lex EL |
| GDPR Art. 6 | Lawfulness of processing | EUR-Lex EL |
| GDPR Art. 13 | Information to be provided on collection | EUR-Lex EL |
| GDPR Art. 14 | Information where data not obtained from subject | EUR-Lex EL |
| GDPR Art. 15 | Right of access | EUR-Lex EL |
| GDPR Art. 17 | Right to erasure | EUR-Lex EL |
| GDPR Art. 82 | Right to compensation and liability | EUR-Lex EL |
| GDPR Art. 83 | General conditions for imposing penalties | EUR-Lex EL |

### Tier 2: Cold Vault — Indexed for RAG Retrieval

**Greek case law corpus (retrieve via lawyer, store as PDF → convert to text for RAG):**
- Priority 1 (retrieve immediately): ΑΠ 777/2022, 985/2020, 938/2018, 806/2023, 362/2023
- Priority 2 (research phase): All ΑΠ on Arts. 592, 576, 602, 904 ΑΚ (2015–2026) — estimated 50–200 decisions
- Priority 3 (background): Ειρηνοδικείο decisions on deposit deductions in relevant jurisdiction

**HDPA decisions corpus:**
- Priority 1: 36/2021, 1/2025, 31/2025, 30/2024, 27/2024 (cited in data protection claims)
- Priority 2: All HDPA decisions on Art. 15 GDPR (right of access refusals) — estimated 15–30 decisions
- Priority 3: All HDPA decisions on property management / real estate sector

**CJEU GDPR corpus:**
- Priority 1: C-434/16, C-203/22, C-487/21, C-579/21, C-154/21, C-307/22 (all cited in data protection claims)
- Priority 2: All CJEU GDPR Art. 15 judgments since 2018

**Full law text (bulk):**
- Full ΑΚ (2000+ articles) — reference when AI needs to check any civil law article
- Full ΚΠολΔ (1000+ articles) — reference for procedural law
- Full N. 2251/1994 (consumer protection)
- Full N. 4601/2019 (company law, spin-offs)

---

## 7. Implementation Recommendations

### 7.1 Phase 1 — Hot Vault (Build in 2 hours)

Build the hot vault manually. For each article listed in Section 6 Tier 1:

1. Open kodiko.gr or EUR-Lex at the article URL
2. Copy the Greek text of the article
3. Create a file: `law_vault/hot/{law_code}-{article}.md`
4. Include: law citation, ΦΕΚ reference, current codified text, one-line summary in English

Example structure:
```markdown
# Art. 592 ΑΚ — Normal Wear and Tear

**Source:** Αστικός Κώδικας, Νόμος 2250/1940 (ΦΕΚ Α΄ 179/1940), as codified
**Verified:** kodiko.gr, 2026-04-04
**Version:** Current (no recent amendments to this article)

## Greek Text
Ο μισθωτής υποχρεούται να επιστρέψει το μίσθιο στην κατάσταση που το παρέλαβε,
εκτός από τις φθορές που οφείλονται στη συμφωνημένη χρήση ή στον χρόνο ή στα
τυχαία γεγονότα.

## Summary (EN)
The tenant must return the property in the condition received, except for deterioration
due to agreed use, time passage, or accidental events. This is the primary defence
against damage charges — normal wear and tear is not chargeable.
```

**Time estimate:** 45–90 minutes for 35 articles.

### 7.2 Phase 2 — Cold Vault EUR-Lex Download (Automated, 1 hour)

Run the following Python script to download all CJEU cases and GDPR text:

```python
#!/usr/bin/env python3
"""Download EUR-Lex documents for Legal Authority Vault cold storage."""

import requests
import time
import os
from pathlib import Path

VAULT_DIR = Path("law_vault/cold/eurlex")
VAULT_DIR.mkdir(parents=True, exist_ok=True)

DOCUMENTS = {
    # Regulations
    "32016R0679_GDPR_EL": ("32016R0679", "EL"),
    "32016R0679_GDPR_EN": ("32016R0679", "EN"),
    # CJEU cases
    "62016CJ0434_Nowak_EN": ("62016CJ0434", "EN"),
    "62016CJ0434_Nowak_EL": ("62016CJ0434", "EL"),
    "62022CJ0203_EN": ("62022CJ0203", "EN"),
    "62021CJ0487_EN": ("62021CJ0487", "EN"),
    "62021CJ0579_PankkiS_EN": ("62021CJ0579", "EN"),
    "62021CJ0154_EN": ("62021CJ0154", "EN"),
    "62022CJ0307_EN": ("62022CJ0307", "EN"),
    # Directives
    "32011L0083_ConsumerRights_EL": ("32011L0083", "EL"),
    "32005L0029_UnfairPractices_EL": ("32005L0029", "EL"),
}

HEADERS = {"User-Agent": "Mozilla/5.0 (legal research bot; not commercial)"}

for filename, (celex, lang) in DOCUMENTS.items():
    out_path = VAULT_DIR / f"{filename}.html"
    if out_path.exists():
        print(f"Skip (exists): {filename}")
        continue
    url = f"https://eur-lex.europa.eu/legal-content/{lang}/TXT/HTML/?uri=CELEX:{celex}"
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        out_path.write_text(r.text, encoding='utf-8')
        print(f"OK ({len(r.text)//1024}KB): {filename}")
    except Exception as e:
        print(f"FAIL: {filename} — {e}")
    time.sleep(1.5)  # Polite rate limiting

print("Done.")
```

**Expected output:** ~15 files, ~12MB total.

### 7.3 Phase 3 — HDPA Decisions (Chrome DevTools MCP, 30 min)

The HDPA site is a JavaScript SPA and cannot be scraped with plain HTTP. Use Chrome DevTools MCP:

1. Navigate to `https://www.dpa.gr/el/decisions`
2. Search for each decision number (36/2021, 1/2025, etc.)
3. Click the PDF download link
4. Save to `law_vault/cold/hdpa/`

Alternatively: search Google for `site:dpa.gr "36/2021" filetype:pdf` to find direct PDF URLs.

### 7.4 Phase 4 — ΑΠ Case Law (via Lawyer, 1 week)

Send the following structured request to a lawyer with Qualex access:

> "Please retrieve full text PDFs of the following ΑΠ decisions:
> ΑΠ 777/2022, ΑΠ 985/2020, ΑΠ 938/2018, ΑΠ 806/2023, ΑΠ 362/2023.
> Also: all ΑΠ decisions on Arts. 592, 576, 602 ΑΚ in rental context, 2018–2026,
> and any Ειρηνοδικείο decisions on security deposit deductions.
> Format: PDF per decision, file name = 'AP_[year]_[number].pdf'."

Store in: `law_vault/cold/ap_decisions/`

### 7.5 RAG Indexing (Phase 4+)

Once cold vault PDFs are collected:

1. Convert PDFs to text: `pdfplumber` (Python) or `pdftotext` (poppler)
2. Chunk by article/paragraph: 500-token chunks with 50-token overlap
3. Embed with a multilingual model: `paraphrase-multilingual-mpnet-base-v2` (supports Greek)
4. Index in ChromaDB: `scripts/build_vector_index.py`
5. Query pattern: before AI responds on any legal question, query vault for relevant chunks

---

## 8. Anti-Hallucination Protocol

The vault is only useful if the AI uses it. The following protocol ensures grounded citations:

### Rule 1 — Hot Vault First

Before citing any law article in a draft, the AI must check whether the article is in the hot vault. If it is, cite the exact text from the vault file. If not in hot vault, note it as unverified.

### Rule 2 — CELEX Verification for EU Law

Every GDPR article citation must include the CELEX reference and the EUR-Lex URL. This allows one-click verification. Format:
```
GDPR Art. 15(1) (Reg. 2016/679, CELEX:32016R0679, EUR-Lex EL: https://eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:32016R0679)
```

### Rule 3 — Case Law Must Be Confirmed

No ΑΠ case number may appear in a formal document unless:
- The full text is in the cold vault, OR
- The case was retrieved via a verified source (Qualex, Sakkoulas, lawyer-confirmed), OR
- The case number is cross-referenced against at least two independent mentions in existing case files

ΑΠ 777/2022, 985/2020, 938/2018, 806/2023 are pre-verified and may be cited. Any other ΑΠ case number requires vault confirmation before formal use.

### Rule 4 — Amended Law Warning

Greek law changes frequently. Before citing any Greek law article, check:
1. Was this article amended since the relevant date? (Kodiko.gr shows amendment history)
2. Was the amendment in force at the time of the events in question?
3. If amended between events and today: cite the version operative at the event date

### Rule 5 — Never Cite Archive Files

Per standard discipline: always cite the most recent confirmed version of each fact. Do not rely on superseded research files.

---

## Quick Reference — Source Access Summary

| Source | URL | API/Scrape? | Free? | Best For |
|--------|-----|-------------|-------|----------|
| EUR-Lex | eur-lex.europa.eu/legal-content/EL/TXT/HTML/?uri=CELEX:{id} | Yes — direct GET | Yes | GDPR, CJEU cases, EU Directives |
| Kodiko.gr | kodiko.gr/nomologia/document_navigation/{id}/{slug} | Scrape (no API) | Yes | Current ΑΚ, ΚΠολΔ, Greek law text |
| Lawspot.gr | lawspot.gr/nomikes-plirofories/nomothesia/ | Scrape | Yes | Law text; legal news monitoring |
| et.gr (ΦΕΚ) | search.et.gr | Manual only | Yes | Original ΦΕΚ PDFs; company search |
| dsanet.gr / Isocrates | dsanet.gr | Login required (ΔΣΑ) | Via lawyer | All court levels incl. Ειρηνοδικείο |
| Areiospagos.gr | areiospagos.gr | ✅ ALIVE (verified 2026-04-06) | Free, official | **First-tier free source for ΑΠ decision full text** — POST form at `/nomologia/apofaseis.asp` |
| HDPA | dpa.gr/el/decisions | SPA (Chrome DevTools) | Yes | HDPA enforcement decisions |
| HUDOC | hudoc.echr.coe.int/app/query/results | REST API (free) | Yes | ECHR judgments |
| Qualex | nb.org | Subscription required | No | ΑΠ case law; doctrine; journals |
| Sakkoulas | sakkoulas-online.gr | Subscription | No | Doctrine; real estate law journal |
