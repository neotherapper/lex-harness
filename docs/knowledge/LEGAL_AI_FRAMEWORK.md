---
title: "Legal AI Framework — Architecture Design"
scope: global
source: "docs/knowledge/LEGAL_AI_FRAMEWORK.md (adapted from internal case research — this file is the canonical reference)"
last_verified: "2026-04-08"
---

# Legal AI Framework — Architecture Design

> Version: 1.0 (adapted for lex-harness)
> Purpose: Reference architecture for AI-assisted legal analysis in civil-law disputes.
> Scope: Generic framework applicable to any civil-law case; examples drawn from Greek/EU law but the architecture is jurisdiction-neutral.

---

## Executive Summary

This framework describes a layered architecture for AI-assisted legal reasoning that prioritizes verification, adversarial review, and phase-gated discipline over generative fluency.

**The single most important design decision:** verification is architecturally separated from generation. Every legal claim is decomposed into atomic statements and each is verified against primary sources by a separate phase before any document is finalized. This is the SOLAR pattern applied at framework scale.

**The second most important design decision:** the Devil's Advocate review is not optional post-hoc commentary — it is a mandatory blocking gate before any argument reaches a formal document.

| Capability | Typical commercial legal AI | This framework |
|---|---|---|
| Civil-law support (non-US) | Partial / configurable | Native |
| Adversarial DA review | No | Yes (L4M-inspired) |
| OSINT evidence layer | No | Yes |
| Multi-forum packaging | No | Yes |
| Temporal law versioning | Partial | Yes (SAT-Graph pattern) |
| Argument mining (opponent docs) | No | Yes (Toulmin pattern) |
| Claim decomposition | Partial | Yes |
| Knowledge-graph retrieval | No | Yes |
| Phase-gated pipeline | No | Yes (DISCOVER-PLAN-VERIFY-EXECUTE-EVOLVE) |
| Session-end learning | No | Yes (EVOLVE phase) |

---

## Architecture Overview

```
LAYER 0: FOUNDATION MODELS
  Model routing: standard vs. adversarial/novel reasoning
  Adversarial pair: primary agent + DA agent (independent, parallel)

LAYER 1: KNOWLEDGE ARCHITECTURE (3-TIER)
  Tier 1 (Ground Truth): case summary + verbatim statute corpus + decision log
  Tier 2 (Analysis): claim/defense files + DA reviews + knowledge graph
  Tier 3 (Output): drafts, complaints, demand letters, regulatory filings
  Cross-layer: SAT-Graph temporal versioning | LegalRuleML deontic encoding

LAYER 2: RETRIEVAL ARCHITECTURE
  Hybrid: BM25 (exact statute refs) + Dense vectors (semantic) via RRF fusion
  GraphRAG: traversal over entity-relation-argument chains
  HyDE: hypothetical document embeddings for short-query / long-document gap
  Multi-hop: multiple retrieval steps for complex statutory interpretation
  Self-RAG: selective retrieval by query complexity
  Contextual Retrieval: per-chunk context prepend

LAYER 3: VERIFICATION PIPELINE (SOLAR + Citation Chain)
  SOLAR Stage 1: rule pre-loading from verbatim statute text (no training memory)
  SOLAR Stage 2: fact application to pre-loaded TBox
  5-stage citation pipeline: extract -> exist -> holding -> currency -> status
  Claim decomposition: atomic claims, each independently verified
  HalluGraph: knowledge-graph-alignment post-generation check
  Temporal check: effective-date vs. event-date verification

LAYER 4: REASONING PIPELINE
  DISCOVER -> PLAN -> VERIFY -> EXECUTE -> EVOLVE
  Per-phase gates block progression until phase requirements are met
  Legal structures: CREAC (advocacy) | Gutachtenstil (pleadings) | Legal syllogism
  Three-dimensional quality gate: Facts + Cited Articles + Analysis

LAYER 5: OSINT AND EVIDENCE LAYER
  Digital forensics: EXIF, PDF XMP, DKIM/SPF, certificate transparency
  Corporate intelligence: business registries, beneficial-ownership sources
  Real estate: cadastre, archived listings, aerial photography
  Evidence preservation: SHA-256, RFC 3161, chain-of-custody records

LAYER 6: MULTI-AGENT ARCHITECTURE
  Primary agent: standard analysis, drafting, retrieval
  DA agent: adversarial review, parallel and independent
  Argument-mining agent: Toulmin analysis of opponent documents
  Verification agent: citation pipeline, statutory databases
  Consolidation agent: synthesis before document finalization

LAYER 7: OUTPUT AND FORUM PACKAGING
  Multiple forums: court | data-protection regulator | consumer ombudsman | tax authority | criminal
  Forum-specific argument weighting (same fact, different weight per forum)
  Filing-sequence rules
  Extraction question bank with scoring methodology
```

---

## Layer 0: Foundation Models

### Model Selection Decision Tree

```
Task involves sustained 10+ step logical chain?
  YES -> highest-capability reasoning model
  NO v

Task involves novel adversarial reasoning (DA review for court submissions)?
  YES -> highest-capability reasoning model
  NO v

Task involves multi-jurisdictional EU/national law with 10+ interdependent elements?
  YES -> highest-capability reasoning model
  NO v

Task is bulk classification/summarization of known content?
  YES -> cheapest capable model
  NO v

Default: mid-tier general-purpose model (near-top on standard legal analysis)
```

**Cost note:** At typical session volumes the per-session cost difference between tiers is small. Never use cost as a reason to use a weaker model when adversarial review or novel reasoning is warranted.

### Benchmark Context

The primary benchmark for Greek civil-law reasoning is **GreekBarBench** (EMNLP 2025, 220 questions from Greek Bar Exams 2015-2024, covering civil law and KPolD). Critical finding: even the best-performing models make citation errors on Greek statutory articles at a rate of approximately 15-20%. No mainstream model has been trained on a Greek civil-law corpus of sufficient density to eliminate this. **This is the primary driver for the 5-stage citation verification pipeline and the SOLAR pre-loading requirement.**

**3-dimensional scoring** (apply to every legal argument):

1. **Facts (1-10):** Is every fact tied to numbered evidence with status (PROVEN / AVAILABLE / VERBAL)?
2. **Cited Articles (1-10):** Is every citation linked to a verified source with the correct sub-article?
3. **Analysis (1-10):** Is every statutory element addressed by element-by-element subsumption (not holistic narrative)?

### LegalBench Task-Type Mapping

| LegalBench Category | Difficulty for LLMs | Best Tool |
|---|---|---|
| Issue Spotting | Medium | Mid-tier general model |
| Rule Recall | Low-Medium | SOLAR pre-load (do not trust training memory) |
| Rule Application | High | Gutachtenstil element-by-element |
| Rule Conclusion | High | Highest-capability reasoning model |
| Interpretation | Medium | Mid-tier general model |
| Rhetorical Understanding | Medium | Argument mining + DA agent |

### Multi-Model Adversarial Pattern

```
Standard session:
  Primary agent  -> argument development -> text drafting
  DA agent       -> parallel, independent -> adversarial review

DA agent receives:
  - Case facts (ground-truth summary)
  - Legal articles (verbatim from statute corpus)
  - Opponent's known positions (from correspondence)
  NOT: the primary agent's conclusions (prevents anchoring bias)

Synthesis:
  - Both outputs compared
  - Conflicts flagged for explicit resolution
  - If both reach the same conclusion independently -> confidence = HIGH
```

---

## Layer 1: Knowledge Architecture (3-Tier + Graph)

### The 3-Tier Model

The fundamental architectural principle: facts, insights, and analyses are kept in separate layers with strict propagation rules. Data flows **down**; corrections always start at Tier 1.

```
TIER 1 — GROUND TRUTH
  Rule: Never auto-refreshed. Only manually verified content with source citations.
  AI agents: READ only. Write only after human confirmation.
  Example content:
    case_summary/CASE_OVERVIEW.md        <- parties, dates, amounts (single source of truth)
    legal_research/STATUTE_CORPUS.md     <- verbatim statute text + operative dates
    strategy/DECISION_LOG.md             <- dropped/corrected arguments (institutional memory)

TIER 2 — ANALYSIS
  Rule: Derived from Tier 1. Always traceable back to a Tier 1 fact. Subject to review.
  AI agents: Generate and update; human approval before promotion.
  Example content:
    claims_and_defenses/*.md             <- per-claim and per-defense analysis
    da_reviews/*.md                      <- devil's advocate reviews
    knowledge graph                       <- entity-relation-argument triples

TIER 3 — OUTPUT
  Rule: Derived from Tier 2. Refreshed whenever Tier 2 changes. Never contradicts Tier 1.
  AI agents: Generate; human approves before any external use.
  Example content:
    drafts/emails/*.md                   <- ready-to-send communications
    drafts/regulatory_complaint.md       <- regulatory filings
    strategy/SETTLEMENT_ECONOMICS.md     <- negotiation materials
```

**The stale-data propagation problem:** "fix: stale data" commits frequently share the same root cause: Tier 2 files treated as canonical when Tier 1 changes. The discipline: when a Tier 1 fact changes, the EXECUTE phase must run a cascade update identifying all Tier 2 and Tier 3 files that reference the changed fact and correcting them before marking the session complete.

**Propagation rule (formal):** Tier 1 -> Tier 2 -> Tier 3. Never the reverse. Tier 2 files that disagree with Tier 1 are wrong by definition, not by argument.

### Tier 2: Knowledge Graph

Recommended entity types for a civil-dispute graph:

- `Person`, `Company`, `Charge`, `Counterclaim`, `Evidence`, `LegalArticle`
- `Fact`, `Precedent`, `StrategicArgument`
- `Communication`, `Contract`, `Deadline`
- `Admission`, `Contradiction`, `CrossCuttingIssue`, `ReasoningChain`

**Argument-mining nodes (from Toulmin analysis):**

```cypher
// Claim node
(:Claim {
  id: "CL-001",
  text: "[the claim text]",
  source_doc: "[source identifier]",
  sentence_idx: 14,
  confidence: 0.91,
  status: "CONTESTED"  // ADMITTED | CONTESTED | WITHDRAWN
})

// Premise node — evidence/reason supporting a claim
(:Premise {
  id: "PR-001",
  text: "[the premise text]",
  type: "FACTUAL",  // FACTUAL | LEGAL | TESTIMONIAL
  evidence_ref: "[evidence id]",
  strength: "STRONG"  // STRONG | MODERATE | WEAK
})

// ArgumentRelation — directed edges between claims and premises
(:Claim)-[:SUPPORTED_BY]->(:Premise)
(:Claim)-[:ATTACKS]->(:Claim)
(:Claim)-[:REBUTS]->(:Claim)
(:Premise)-[:GROUNDS]->(:Claim)
```

**Evidence provenance (W3C PROV-DM attributes on evidence nodes):**

```cypher
(:Evidence {
  id: "E-101",
  file_path: "[relative path to artifact]",
  sha256: "[sha256 hash at collection time]",
  rfc3161_timestamp: "[RFC 3161 TSA response time]",
  collection_method: "[tool / process]",
  chain_of_custody: ["[step 1]", "[step 2]"],
  prov_wasAttributedTo: "[collector]",
  prov_hadPrimarySource: "[original source]",
  admissibility: "PROVEN"  // PROVEN | AVAILABLE | TO_LOCATE | VERBAL
})
```

### Temporal Versioning: SAT-Graph Pattern

**Problem:** Which version of a law was operative on the date of the relevant event?

**Pattern (without building the full ML system):**

```
For every statute citation in any document:
  1. Identify the event date
  2. Load STATUTE_CORPUS.md -- check the "operative since" annotation
  3. Verify: effective_date <= event_date AND (repeal_date > event_date OR no repeal)
  4. State in document: "[Art. X] [operative on <date>] [as per <source ref>]"
  5. If event predates amendment: cite prior version explicitly
```

**Statute corpus annotation standard** (required format for every article entry):

```
## Art. <X> <CODE> — <short title>
**Operative:** <date range or "always">
**Source:** <official gazette reference>
**Elements:** [1] ..., [2] ..., [3] ...
**Exception:** <exception> (burden: <party>)
**Overrides:** <lex specialis notes>
**Overridden by:** <lex posterior notes>
```

### LegalRuleML Integration (Practical Encoding)

Formal LegalRuleML XML is not required. The pattern is applied as structured documentation in claim/defense files. Every legal rule should be documented with deontic operators:

```
Rule: <Article reference>
  Type: <PROHIBITION | OBLIGATION | PERMISSION>
  Operator: <must / must not / may>
  Subject: <actor category>
  Object: <counterparty category>
  Condition: <triggering condition>
  Operative: <date range>
  Exception: <exception clause> (burden: <party> — <procedural rule>)
  Defeated by: <defeaters>
  Lex specialis: <if applicable>
  Lex posterior: <if applicable>
```

This encoding, stored in the statute corpus, is what SOLAR Stage 1 loads to build the TBox before any reasoning agent applies the rule to facts.

---

## Layer 2: Retrieval Architecture (Hybrid RAG)

### Why Basic Vector RAG Fails for Legal Work

GraphRAG benchmarks show vector-RAG accuracy degrades sharply on queries involving 5+ entity types. A typical civil-dispute query involves: fact -> argument -> cross-cutting issue -> strategic argument -> precedent -> DA counter-argument. The knowledge graph is the correct retrieval backbone for these queries.

### Contextual Retrieval (Anthropic 2024)

Before any chunk from the repository is indexed for semantic search, prepend a context statement generated from the full document.

**Standard context statement template for each chunk:**

```
[File: {filename} | Section: {heading} | Claim/Defense: {id or N/A} |
 Party role: <claimant|respondent|both> | Tier: 1|2|3 |
 Law domain: Civil / Consumer / Data Protection / Tax / Criminal]
```

### Hybrid Retrieval: BM25 + Dense Vectors (RRF Fusion)

**Why both are required:**

- **BM25 (sparse, keyword)** excels at: statute references, party names, exact legal terms, case-law citations, article sub-sections.
- **Dense (embedding)** excels at: semantic variants (e.g., "wear and tear" ~ "normal deterioration"), paraphrased holdings, conceptual proximity.

**Reciprocal Rank Fusion:** for each document, score = sum of 1/(60 + rank) across both ranked lists. Hybrid recall is consistently 15-30% better than either method alone.

**Query routing:**

| Query type | Primary method | Why |
|---|---|---|
| Exact statute reference | BM25 | Exact keyword match |
| Semantic paraphrase | Dense | Embedding similarity |
| Multi-entity traversal | GraphRAG | Graph traversal |
| Pattern across many facts | GraphRAG -> then dense | Graph traversal + semantic ranking |

### GraphRAG: Graph-Powered Traversal

**Standard retrieval patterns:**

```cypher
// Pattern 1: "Strongest arguments against claim X"
MATCH (c:Charge {id: "<id>"})-[:HAS_ARGUMENT]->(arg:Argument)
OPTIONAL MATCH (arg)-[:SUPPORTED_BY]->(ev:Evidence {status: "PROVEN"})
OPTIONAL MATCH (da:DA_Review)-[:RATES]->(arg)
WHERE da.threat_level <> "HIGH"
RETURN arg, count(ev) as evidence_count, da.threat_level
ORDER BY evidence_count DESC, da.threat_level ASC

// Pattern 2: "All proven facts supporting strategic argument X"
MATCH (sa:StrategicArgument {id: "<id>"})-[:ELEMENT]->(el:Element)
MATCH (el)-[:SUPPORTED_BY]->(pf:Fact {category: "PROVEN"})
RETURN el.name, collect(pf.id) as proven_facts

// Pattern 3: "Which arguments cite a given article?"
MATCH (art:LegalArticle {citation: "<citation>"})
MATCH (arg)-[:CITES]->(art)
RETURN type(arg), arg.id, arg.summary
```

### HyDE: Hypothetical Document Embeddings

Apply when standard retrieval confidence is low (top-k results below the similarity threshold).

**Process:**

1. Receive short query
2. Generate a hypothetical answer (200-400 words)
3. Embed the hypothetical and retrieve against the corpus
4. The hypothetical vector is geometrically closer to the actual document than a short query vector

**When to trigger:** Self-RAG reflection-token pattern — if retrieval similarity scores fall below a 0.75 threshold, automatically trigger HyDE for the same query.

### Multi-Hop RAG for Complex Statutory Queries

**4-hop chain example — bad-faith argument:**

```
Hop 1: Retrieve the strategic argument and its constituent elements.
Hop 2: For each element, retrieve the legal standard (statutory article + precedents).
Hop 3: For each element, retrieve proven facts that satisfy it.
Hop 4: Retrieve DA counter-arguments; adjust confidence per threat level.
```

No single vector query executes all four hops. Multi-hop RAG with a planning step does.

### Self-RAG: Selective Retrieval by Query Complexity

Not every query requires the same retrieval depth. Apply retrieval tiers based on query type:

| Query type | Retrieval tier |
|---|---|
| Known case fact (already in working memory) | None — parametric |
| Statute exact text | Mandatory single-step |
| Is claim X defensible? | Multi-hop |
| Combined exposure across all claims | Full agentic multi-hop |

---

## Layer 3: Verification Pipeline (SOLAR + Citation Chain)

### SOLAR Rule Pre-Loading — The Core Hallucination Fix

**The problem:** AI reasoning agents apply legal rules from training memory. For non-US and especially non-English civil-law corpora, training memory is incorrect 15-20% of the time. The misgrounded failure mode (correct article number, wrong content attributed to it) passes casual review and is the most dangerous error type.

**SOLAR solution (arXiv 2509.00710):**

**Stage 1 — Rule Formalization** (always runs before any legal analysis):

```
Input: Verbatim text of the relevant article from the statute corpus
Output: TBox — structured rule representation

Example TBox (generic wear-and-tear rule):
  Article: <statute reference>
  Type: PROHIBITION
  Elements:
    [E1] Normal use — definition: use that preserves the property without causing
         damage beyond ordinary deterioration
    [E2] Agreed use — definition: use explicitly or implicitly permitted by the lease
    [E3] Resulting wear is EXEMPT from the counterparty's liability
  Exception: abnormal use [burden: landlord must prove]
  Operative: <date range>
  Lex specialis: <if applicable>
  Cross-reference: <controlling precedents>
```

**Stage 2 — Rule Application** (the answering agent works ONLY from Stage 1 TBox):

```
TBox: [loaded above]
Case facts: [from proven facts register]
Task: For each TBox element, state the relevant facts and whether the element is satisfied.
```

**The answering agent cannot hallucinate a statutory rule because the TBox was formalized from the verbatim statute text.** The only failure mode is Stage 1 error, and Stage 1 works from the literal article text in the statute corpus, not from training memory.

**Implementation gate:** If the statute corpus does not contain the article -> HALT -> query the canonical statutory database before proceeding. No analysis runs without a verified TBox.

### The 5-Stage Citation Verification Pipeline

Every legal citation must pass all 5 stages before inclusion in any formal document.

**Stage 1 — Extraction (structured parsing):**

```python
citation = {
    "article": "<article ref>",
    "law": "<law ref>",
    "sub_article": "<sub-letter if any>",  # Critical — sub-letter errors are common
    "purpose": "<what the citation is being used for>",
    "event_date": "<event date>"
}
```

**Stage 2 — Existence check (DETERMINISTIC — no LLM):**

- Domestic law: lookup in the statute corpus by article ID anchor — if found, PASS; if not, flag as `[UNVERIFIED]`
- EU law: EUR-Lex retrieval by CELEX number
- Domestic case law: lookup in the case-law index and verify against the official court database

**This is a binary deterministic check. No LLM opinion can override a lookup failure.**

**Stage 3 — Holding validation (LLM permitted):**

- Load the actual verbatim text of the article
- Compare what the article text says against what the argument claims it says
- This is where the misgrounded failure mode is caught

**Stage 4 — Currency check (temporal versioning):**

- Apply the SAT-Graph pattern: effective_date <= event_date AND (repeal_date > event_date OR no repeal)
- Check the decision log for any known wrong-version errors
- BLOCKED if the decision log contains a version-specific error for this citation

**Stage 5 — Status annotation:**

Every citation in every document must carry one of these status tags:

```
[VERIFIED — statute corpus #<anchor> — operative <date range>]
[VERIFIED via <canonical DB> — <source reference>]
[VERIFIED via EUR-Lex — CELEX <number>]
[UNVERIFIED — lookup required before sending]
[DROPPED — see DECISION_LOG <id>]
[WRONG_VERSION — use <correct version>]
```

**Formal documents (court, regulatory, demand letter) must contain ZERO `[UNVERIFIED]` citations.**

### Claim Decomposition

Decompose compound legal statements into atomic claims and verify each independently.

**Decomposition protocol:**

Given a compound statement, extract atomic claims into a table:

| ID | Atomic Claim | Type | Verification source |
|---|---|---|---|
| AC-1 | <fact 1> | FACTUAL | <document> |
| AC-2 | <legal classification> | LEGAL | <statute corpus anchor> |
| AC-3 | <legal consequence> | LEGAL | <statute corpus anchor> |
| AC-4 | <fact 2> | FACTUAL | <document> |

Each claim is verified independently. No argument is finalized until all atomic claims pass their respective verification stage.

### HalluGraph: Post-Generation Structural Check

After generating any legal argument, validate it against the knowledge graph:

```cypher
// Does the argument assert facts not in the graph?
MATCH (f:Fact) WHERE f.text CONTAINS "<key phrase>"
RETURN f.id, f.status

// Does the argument assert relations the graph contradicts?
MATCH (ch:Charge {id:"<id>"})-[:GOVERNED_BY]->(art:LegalArticle)
RETURN art.citation
```

- If the argument asserts a fact not in the graph -> flag as `[NEW — verify before use]`.
- If the argument asserts a relation the graph contradicts -> flag as `[CONFLICT — check]`.

Graph alignment catches entity substitutions that semantic similarity misses.

### Temporal Verification Gateway

Before any session generates legal arguments, the DISCOVER phase pre-loads temporal anchors: key event dates, statutory effective dates, limitation-period deadlines, and the operative version of every article to be cited.

---

## Layer 4: Reasoning Pipeline

### DISCOVER -> PLAN -> VERIFY -> EXECUTE -> EVOLVE

The pipeline is phase-gated: each phase has entry conditions that must be met before the next phase begins. Skipping phases is the primary cause of repeated errors.

```
DISCOVER
  Entry: Session start, or before any new task
  Must load: CURRENT_STATUS + DECISION_LOG + CASE_OVERVIEW (key facts fingerprint)
  Must output: ONE recommended next action (ranked by deadline proximity ->
               strategic impact -> effort)
  Terminal state: "Verified situation. Next action: [X]. Relevant articles loaded."
  -> PLAN

PLAN
  Entry: DISCOVER output with verified situation + identified task
  Must produce: CREAC scaffold (all 5 elements non-empty before EXECUTE)
  Must apply: Claim decomposition on every compound statement
  Must pre-load: SOLAR TBox for all relevant articles from the statute corpus
  Must check: DECISION_LOG — no dropped arguments
  Must run: DA dispatch (parallel, independent)
  Terminal state: "CREAC plan verified. [N] claims VERIFIED, [M] UNVERIFIED (listed)."
  Blocks on: any unresolved HIGH-threat DA counter-argument
  -> VERIFY (for UNVERIFIED items) or -> EXECUTE (if all clear)

VERIFY
  Entry: PLAN output with specific [UNVERIFIED] claims to check
  Must run: 5-stage citation pipeline for each unverified claim
  Must check: temporal versioning for all cited statutes
  Must maintain: architectural independence (load primary sources fresh; do not
                 trust PLAN output)
  Terminal state: "Claim [X] VERIFIED via [source]. Claim [Y] DROPPED — DL-XX."
  -> PLAN (update plan) or -> EXECUTE (if all resolved)

EXECUTE
  Entry: verified CREAC structure + all claims VERIFIED + no unresolved HIGH DA threats
  Must run: consolidation gate (check existing files before creating new)
  Must output: CREAC-structured document with all citations status-annotated
  Must run: cascade update checklist (what Tier 2/3 files reference changed Tier 1 facts?)
  Must run: human review gate for formal documents (summary table + explicit
            approval request)
  Terminal state: "Document complete. Cascade checklist done. Graph updated."
  -> EVOLVE

EVOLVE
  Entry: EXECUTE complete; session ending
  Must update: DECISION_LOG (any new dropped/corrected arguments)
  Must update: CURRENT_STATUS (next session's starting orientation)
  Must update: PROVEN_FACTS_REGISTER (new proven facts from session)
  Must update: knowledge graph (new entities, relations, observations)
  Must run: memory compression (extract events, detect conflicts, merge)
  Terminal state: "Session complete. [N] new rules. [M] facts added. CURRENT_STATUS updated."
```

### DISCOVER Phase Detail

**Mandatory first step — DECISION_LOG check:** Before any argument is proposed or researched, load the decision log and verify the argument is not already dropped or downgraded. Dropped arguments are institutional memory. Resurfacing them wastes session time and risks document errors.

**Memory search:** prefer targeted semantic searches over loading the full graph.

**OSINT evidence collection** (during DISCOVER for new sessions with open evidence gaps): see Layer 5.

**Legal research:** use the canonical statutory database for domestic law and EUR-Lex for EU law via structured queries.

**Argument mining of opponent documents** (during DISCOVER when processing new opposing responses): apply a Toulmin extraction template to identify claims, premises, and relations. Flag:

- Claims without supporting premises (logical gaps -> extraction questions)
- Premises that are demonstrably false (contradictions -> graph nodes)
- New arguments not previously addressed (-> new DA review task)

### PLAN Phase Detail

**Three-column test — mandatory for every extraction question:**

| Column | Required outcome |
|---|---|
| If YES | Must provide a usable admission |
| If NO | Must create a useful contradiction or adverse inference |
| If SILENT | Must allow an adverse inference under the applicable procedural rule |

Questions that fail any column are redesigned or dropped.

**CREAC vs. Gutachtenstil selection:**

| Document type | Framework | Opening |
|---|---|---|
| Formal demand letter | CREAC | Conclusion first |
| Court pleading | Gutachtenstil | Article -> elements -> subsumption -> conclusion |
| Consumer Ombudsman complaint | CREAC + pattern narrative | Pattern theme -> legal basis |
| Data-protection regulator complaint | Article-first | Article number, then what the controller did |
| Extraction correspondence | None (conversational) | Three-column test drives question design |
| Internal claim/defense analysis | Gutachtenstil per element | One subsumption block per statutory element |

**Multi-forum packaging:** the same fact can have different weight across forums. PLAN must specify forum assignments per fact.

**Filing-sequence rules:**

1. Consumer Ombudsman procedures typically exclude pending judicial proceedings -> file **before** the civil action.
2. Data-protection investigations generate official responses -> use as evidence in court.
3. Criminal referrals risk procedural stays -> file **last**.
4. Tax-authority referrals should ideally precede the civil action so that the audit is on record at filing.

### VERIFY Phase Detail

**Walton Critical Questions Checklist** — for every legal argument, the DA agent must answer all 5:

| Question |
|---|
| 1. Is the rule applicable to these facts? |
| 2. Is the rule defeasible in this case? |
| 3. Does lex specialis override? |
| 4. Is the authority credible? |
| 5. Is the rule current (operative on the relevant event date)? |

Any uncertain answer -> argument tagged `[PARTIAL]` -> human review required before formal document.

**MAD-Judges pattern** (for highest-stakes arguments only): multiple AI agents argue and vote on argument quality. Warranted when:

- Novel legal theory with no directly on-point precedent
- DA rates counter-argument as MEDIUM and the DROP/KEEP decision is borderline
- Multi-jurisdictional combination (domestic + EU law)

**Architecture independence:** the VERIFY phase must load the statute corpus and decision log independently. It must not use PLAN output as a source of legal truth.

### EXECUTE Phase Detail

**Consolidation gate (before creating any new file):**

```
Before creating <new_file.md>:
  1. Does a file already exist for this purpose?
  2. Can this be added as a section to an existing file?
  3. Should this point to an existing file instead?

If existing file covers topic -> ADD SECTION, do not create new file.
If new file genuinely needed -> log reason.
```

**Evidence provenance recording** (for every new piece of evidence):

```
1. SHA-256 hash (record in EVIDENCE_INDEX)
2. RFC 3161 timestamp (legal-grade, independent authority)
3. W3C PROV-DM attributes on the graph Evidence node
4. Collection method
5. Chain of custody
```

**Human review gate for formal documents** — required checklist before marking any formal document ready-to-send:

| Check item | Status |
|---|---|
| Citations verified | N / N total |
| Atomic claims verified | N / N total |
| Decision log checked | Yes/No |
| DA review exists | Yes/No |
| Financial figures match ground truth | Yes/No |
| Forum-specific version correct | Yes/No |
| Filing sequence checked | Yes/No |

### EVOLVE Phase Detail

**Memory consolidation pattern (Mem0, arXiv 2504.19413):**

At session end, do not just append to status files. Apply the extraction-update pipeline:

1. **Extraction:** identify semantically complete events worth long-term storage (most session content is not).
2. **Update:** for each extracted fact, check against existing memory. Conflicts -> flag for human resolution; duplicates -> update existing; genuinely new -> add to the appropriate topic file.
3. **Index:** the top-level memory index stays short and points to topic files.

**MemGPT three-tier mapping:**

| MemGPT Tier | Implementation | Update cadence |
|---|---|---|
| Core Memory (always visible) | CASE_OVERVIEW + CURRENT_STATUS | Every session |
| Archival Storage | Knowledge graph + topic files | When facts change |
| Recall Storage | Git log + DECISION_LOG | Per commit |
| Working Memory | Active context window | Session only |

**Decision-log update (mandatory at EVOLVE if any argument was corrected):**

Every dropped or corrected argument must be logged with:

- DL-XX number
- The wrong argument (one sentence)
- Why it was wrong (one sentence, legal basis)
- What replaces it (one sentence)
- Date and session number

---

## Layer 5: OSINT and Evidence Layer

### Digital Forensics

**Photo / EXIF verification:**

```bash
# macOS fallback (no exiftool required):
sips -g creation <file>        # creation date from EXIF
sips -g pixelWidth <file>      # resolution check

# General:
exiftool <file>
```

**PDF document forensics:**

```bash
pdfinfo <invoice.pdf>          # creation date, producer, XMP metadata
exiftool <invoice.pdf>         # XMP:CreateDate, XMP:ModifyDate
# If creation date > document date -> possible backdating evidence
```

### Digital Evidence Preservation

**SHA-256 chain of custody:**

```bash
openssl dgst -sha256 <file>
# Record: file_path | sha256_hash | timestamp | collection_method | collector
```

**RFC 3161 timestamp** (legal-grade; admissible in most civil-law courts):

```bash
openssl ts -query -data <file> -no_nonce -sha256 -cert -out <file>.tsq
curl -H "Content-Type: application/timestamp-query" --data-binary @<file>.tsq \
     https://freetsa.org/tsr > <file>.tsr
```

**Evidence status taxonomy:**

| Status | Meaning |
|---|---|
| PROVEN | Documentary evidence confirmed, hash recorded |
| AVAILABLE | Exists and retrievable; not yet formally collected |
| TO_LOCATE | Known to exist; location/access pending |
| VERBAL | Statement or phone call; no documentary record |

### Corporate Intelligence

- **Business registry / beneficial ownership:** the domestic commercial registry is the canonical source for corporate structure, directors, and beneficial ownership.
- **Cross-border verification:** OpenOwnership, OCCRP Aleph, OpenCorporates.
- **Corporate-structure graphs:** visual tools (e.g., Maltego community edition) for presenting ownership chains as court annexes.

### Real Estate OSINT

- **Historical listings:** Wayback Machine CDX API for archived property-listing snapshots.
- **Registered ownership:** cadastre / land registry.
- **Building permits:** municipal permit archives (FOIA-style requests where available).
- **Aerial imagery:** national aerial-photo archives for before/after comparisons.

### Email and Domain Forensics

- **Certificate transparency** (crt.sh): SSL-certificate history reveals domain age and predates-or-postdates questions.
- **DNS auth records** (dig txt _dmarc.<domain>): absence of DMARC = technical-measures gap, potentially relevant to data-protection Art. 32 arguments.
- **Email enumeration** (theHarvester, Amass): discovers contactable addresses for regulatory complaints requiring specific-recipient naming.

### Social Media and Open Web

- **Review archives:** collect and preserve public reviews using archive.ph or equivalent before sending a demand letter (prevents post-hoc deletion).
- **Employee reviews:** platforms like Glassdoor can corroborate business-practice patterns where admissible.

---

## Layer 6: Multi-Agent Architecture

### Agent Roles and Responsibilities

**Primary Reasoning Agent:**

- Standard analysis: clause-by-clause review, argument drafting, extraction-question generation
- Text drafting for correspondence and formal documents
- DISCOVER, PLAN, and EXECUTE phases (primary)
- Evidence indexing and categorization

**Devil's Advocate Agent:**

- Parallel and independent — must NOT see the primary agent's conclusions before forming its own position (anchoring bias)
- Argues from the opponent's perspective: "what would their lawyer say?"
- Rates each counter-argument: HIGH / MEDIUM / LOW threat
- Flags arguments that should be dropped (DA override rule)
- Walton 5-question checklist applied to every argument
- Outputs to a standard DA review format with required sections

**DA agent receives:**

- Case facts (ground-truth summary)
- Verbatim statute texts (statute corpus)
- Opponent's known correspondence
- NOT: primary agent's argument conclusions (independence requirement)

**DA agent DROP rule:**

An argument must be dropped to the decision log if:

- DA rates the counter as HIGH and no rebuttal reduces it to MEDIUM
- The underlying legal citation is wrong (confirmed by decision-log check)
- The argument backfires — raising it creates more exposure than not raising it

**OSINT Collection Agent:** digital forensics, certificate transparency, registry intelligence, archive preservation.

**Legal Verification Agent:** executes citation pipeline Stages 2-4; uses EUR-Lex for EU law and canonical statutory databases for domestic law.

**Argument Mining Agent:** applies Toulmin analysis to the opponent's documents; extracts Claims, Premises, and ArgumentRelations; stores them in the knowledge graph.

**Consolidation Agent:** synthesizes primary + DA + verification outputs; applies the human review gate; ensures CREAC structure is complete; runs the cascade update checklist.

### L4M-Inspired Formal Adversarial Protocol (highest-stakes arguments)

From arXiv 2511.21033:

```
Phase 1 — Statute Formalization:
  Primary agent formalizes each relevant article as a TBox (SOLAR Stage 1)
  DA agent independently formalizes the same articles from the opponent's perspective
  Conflict in formalization -> immediately surfaced (legal uncertainty)

Phase 2 — Dual Position Development:
  Primary agent: maps case facts to statutory elements supporting the claimant's position
  DA agent: maps the SAME facts to statutory elements supporting the opponent's position
  Both work INDEPENDENTLY before seeing each other's output

Phase 3 — Adjudication:
  Consolidation agent compares the two position papers
  For each contested element: strongest argument on each side
  Confidence assigned: HIGH / MEDIUM / LOW
  LOW-confidence elements -> Walton critical-question analysis -> potential DROP
```

Apply the L4M protocol for: formal demand letters, court pleadings, data-protection regulatory complaints. Not required for extraction emails or internal notes.

---

## Layer 7: Output and Forum Packaging

### Forum-Specific Templates

**Court pleading (Gutachtenstil structure):**

```
[1. Parties and jurisdiction]
[2. Factual foundation — numbered facts, each tied to evidence]
[3. Per-element legal analysis (Gutachtenstil)]
    Article X:
      Obersatz:    <legal conclusion if element A is satisfied>
      Definition:  <statutory text for element A>
      Subsumption: <facts>. Therefore element A [is/is not] satisfied because ...
      Ergebnis:    element A satisfied / not satisfied
    [repeat for every element]
    Final Ergebnis: claim succeeds / fails
[4. Calculation — itemized amounts with legal basis for each]
[5. Prayer for relief]
```

**Data-protection regulator complaint:**

```
[1. Controller identification]
[2. Per-violation format:]
    Violation #N:
      GDPR Article: Art. X
      What the controller did/failed to do: <factual statement>
      Evidence: <reference>
      Regulator precedent: <decision number if available>
      Relief sought: <remediation / fine / data deletion>
[3. Filing deadline]
[4. Criminal referral (if applicable)]
```

**Consumer Ombudsman (CREAC + pattern narrative):**

```
[1. Pattern introduction]
[2. CREAC per charge:]
    Conclusion, Rule, Explanation, Application, Conclusion
[3. Combined financial harm]
[4. Pattern-of-conduct documentation]
[5. Relief]
```

**Tax authority referral:**

```
[1. Taxpayer identification]
[2. Per-invoice violations]
[3. Stamp-duty or filing violations
[4. Note: file before the civil action where possible]
```

**Criminal complaint (file last — risk of procedural stay):**

```
[1. Named individuals and criminal provisions]
[2. Pattern documentation]
[3. NEVER use criminal terminology in civil correspondence
[4. File AFTER: consumer ombudsman + data-protection regulator + tax authority are on record]
```

### Extraction Question Bank

**Combined Pressure Score (CPS) methodology:**

```
CPS = LTW x RDW
  LTW (Legal Truth Weight): 1-3 — how important is this answer to the legal case?
  RDW (Response Direction Weight): 1-3 — how favorable is any possible answer?

CPS 9 (max) = question where ALL three response directions help
CPS 1 (min) = question where responses rarely help (redesign or drop)
```

**Three-column test integration:** every extraction question must pass the YES / NO / SILENT test described in the PLAN phase.

**Questions that FAIL the test (do not send):**

- "Do you agree your charges were excessive?" — YES: useless (won't agree); NO: expected; SILENT: no inference
- "Will you return the disputed amount?" — YES: great but won't happen; NO/SILENT: no new legal position

### Settlement Packaging

**ZOPA (Zone of Possible Agreement) analysis:**

```
Claimant's BATNA: litigation for full recovery + counterclaims
Respondent's BATNA: defend all charges; risk regulatory + consumer-protection exposure

ZOPA:
  Claimant's minimum acceptable: <figure>
  Respondent's maximum concession: <figure>
  Sweet spot: somewhere between, saving both litigation cost

Settlement framing triggers:
  Ombudsman filing creates "investigation pending" pressure
  Data-protection complaint creates independent fine exposure
  Tax referral creates audit exposure — motivates resolution before the civil action
```

Maintain a short menu of scenario settlements (baseline / improved / aspirational) to consult before any settlement discussion.

---

## Tool Map (Master Reference)

| Tool category | Layer | Purpose | Examples |
|---|---|---|---|
| Foundation models | L0 | Primary analysis, drafting, DA review | Tier-based routing: cheapest capable -> mid-tier general -> highest-capability reasoning |
| Graph memory | L1/L2 | Retrieve case facts by semantic query | Neo4j + semantic search MCPs |
| Legal reasoning MCPs | L4 | Structured legal reasoning | Domain-specific reasoning tools |
| EU law search | L3/L4 | EU law + CJEU case retrieval | EUR-Lex MCP |
| Statute verification | L3 | Domestic law verification | Canonical statutory database(s) |
| Case-law verification | L3 | Supreme/appellate court precedent | Official court databases |
| Browser automation | L3/L5 | Citation verification, OSINT, evidence | chrome-devtools MCP |
| URL fetch | L3/L5 | Fetch specific URLs | mcp__fetch |
| Business registry | L5 | Corporate intelligence, beneficial ownership | Domestic commercial registry + OpenOwnership |
| Web archive | L5 | Historical listing / web archive | Wayback Machine CDX API, archive.ph |
| Domain forensics | L5 | SSL cert history, DNS auth | crt.sh, dig, theHarvester |
| Photo forensics | L5 | EXIF, XMP metadata | exiftool (macOS fallback: sips) |
| Hash + timestamp | L5 | Chain of custody | openssl dgst, RFC 3161 TSA (e.g., freeTSA) |
| Argument mining | L6 | Claim/premise extraction | Toulmin prompt templates, IBM Debater patterns, TARGER |
| RAG evaluation | L2 | Faithfulness + context checks | RAGAS, TruLens |

---

## Integration Connections

```
DISCOVER Phase:
  CURRENT_STATUS (read)                -> Session brief
  DECISION_LOG (read)                  -> Blocked arguments list
  CASE_OVERVIEW (read)                 -> Key facts fingerprint
  graph semantic search                -> Relevant graph facts
  browser [open web]                   -> OSINT sweep
  browser [prior litigation search]    -> Prior litigation check
  browser [business registry]          -> Corporate facts

PLAN Phase:
  STATUTE_CORPUS (read)                -> SOLAR TBox pre-load
  CASE_LAW (read)                      -> Precedent synthesis (CREAC Explanation)
  DECISION_LOG (read)                  -> Dropped-argument check
  legal-reasoning MCP                  -> Structured legal analysis
  primary model                        -> CREAC scaffold
  DA model (parallel)                  -> Adversarial review (independent)

VERIFY Phase:
  STATUTE_CORPUS (independent load)    -> Stage 2 existence check
  canonical statutory DB (browser)     -> Stage 2 fallback / Stage 3-4
  EUR-Lex MCP                          -> EU law Stages 2-4
  official court DB (browser)          -> Case-law holding validation
  graph HalluGraph check               -> Post-generation KG alignment

EXECUTE Phase:
  primary model                        -> CREAC document generation
  graph (add observations/relations)   -> Knowledge enrichment
  EVIDENCE_INDEX (edit)                -> Evidence provenance recording
  PROVEN_FACTS_REGISTER (edit)         -> New proven facts
  openssl dgst -sha256 (bash)          -> Evidence hash
  RFC 3161 timestamp                    -> Legal-grade timestamping

EVOLVE Phase:
  DECISION_LOG (edit)                  -> New dropped/corrected arguments
  CURRENT_STATUS (edit)                -> Next session orientation
  topic memory files (edit)            -> Semantized long-term memory
  graph enrichment                     -> Entities, relations, observations
  STATUTE_CORPUS (edit, if confirmed)  -> Verified statute update
```

### Critical "Never Do" Constraints

| Constraint | Why | Alternative |
|---|---|---|
| NEVER load the entire knowledge graph eagerly | Token blowout; returns everything | Targeted semantic search or Cypher |
| NEVER reason from training memory about non-US/non-English statute text | High hallucination rate | SOLAR pre-load from statute corpus |
| NEVER allow LLM opinion in Stage 2 (existence check) | Deterministic check must not be overridden | Binary lookup: found or not found |
| NEVER let the DA agent see primary-agent conclusions first | Anchoring bias | Parallel independent dispatch |
| NEVER skip temporal-versioning check | Statute text may post- or pre-date event | SAT-Graph pattern |
| NEVER read archived or superseded case files without flagging | Known wrong values may propagate | Current files in the canonical tree |
| NEVER file consumer ombudsman after civil action | Ombudsman excludes pending litigation | File ombudsman first |
| NEVER use criminal terminology in civil correspondence | Risks a separate actionable claim | Reserve criminal language for the criminal complaint, filed last |

---

## Implementation Priority

### Phase 1 — Must-Have Before Any Formal Document

1. **SOLAR pre-loading gate:** the statute corpus must contain anchor-ID entries for every article to be cited. No article cited without verbatim text pre-loaded.
2. **5-stage citation pipeline:** all citations must pass all 5 stages; every citation must carry a `[VERIFIED]` tag before the document is sent.
3. **DECISION_LOG gate:** DISCOVER checks the decision log before any PLAN phase. No dropped argument resurfaces.
4. **Claim decomposition:** every compound argument is decomposed into atomic claims, each `[VERIFIED]` or `[UNVERIFIED]` tagged.
5. **Human review gate:** summary table + explicit approval before any formal document is marked ready-to-send.
6. **DA dispatch for new arguments:** any argument not previously DA-reviewed must have a DA review before inclusion.
7. **OSINT pre-filing sweep:** free/immediate actions (certificate transparency, public review archive, business registry screenshot, web archive) should be done before filing.
8. **Temporal anchors loaded:** all key dates verified at session start.

### Phase 2 — Should-Have Before Court Filing

1. **Three-dimensional quality gate:** self-score every claim/defense on Facts + Cited Articles + Analysis.
2. **Walton critical questions:** every argument checked against the 5 Walton questions.
3. **DA independence:** primary and DA agents producing independent positions before comparison.
4. **GraphRAG retrieval:** use the knowledge graph as the primary retrieval layer for complex multi-entity queries, not just as storage.
5. **Full OSINT sweep:** cadastre extract, municipal permits, aerial imagery where relevant, domain enumeration.
6. **MCP tool sequencing gate:** EU law citations must use EUR-Lex by CELEX number; domestic citations must use the fallback chain.
7. **L4M adversarial protocol:** full formal dual-position development for the highest-stakes document.

### Phase 3 — Could-Have for Long-Term Framework Improvement

1. **HyDE fallback retrieval** when standard retrieval is low-confidence.
2. **Custom contextual chunking** (Anthropic Contextual Retrieval): prepend context statements to all chunks.
3. **RAGAS evaluation** for automated faithfulness checks.
4. **MAD-Judges formal implementation** for contested arguments.
5. **Hybrid BM25 + dense retrieval infrastructure** as an addition to graph and direct-file reads.
6. **RFC 3161 timestamp automation** via a TSA API.

### Won't Build (Out of Scope for a Single-Case Framework)

1. **Full LegalRuleML XML encoding** — the pattern is implemented as structured documentation; full XML is not required.
2. **SAT-Graph RAG ML system** — the temporal-versioning problem is solved by manual annotation in the statute corpus with operative dates.
3. **Custom legal embeddings** — would require large-scale domain-training data.
4. **Self-hosted legal LLMs** — API models are preferable for per-case work.

---

## Research Basis

This framework draws on research into AI legal-reasoning architectures and civil-law-specific failure modes. Academic sources underpinning the design:

- arXiv 2509.00710 — SOLAR (rule formalization / answering separation)
- arXiv 2511.21033 — L4M (formal adversarial protocol)
- arXiv 2501.09136 — Agentic RAG
- arXiv 2212.10496 — HyDE
- arXiv 2309.15217 — RAGAS
- arXiv 2504.19413 — Mem0
- arXiv 2310.08560 — MemGPT
- arXiv 2310.11511 — Self-RAG
- arXiv 2505.00039 — SAT-Graph RAG
- arXiv 2512.01659 — HalluGraph
- arXiv 2505.17267 — GreekBarBench
- arXiv 2308.11462 — LegalBench
- arXiv 2509.01324 — KoBLEX (multi-hop statutory retrieval)
- arXiv 2510.12697 — MAD-Judges

Standards: OASIS LegalRuleML v1.0, W3C PROV-DM, Akoma Ntoso, FRBR/LRMoo, ELI (EUR-Lex), RFC 3161 (timestamp authority).

---

*End of Legal AI Framework — reference architecture for civil-law dispute assistance.*
