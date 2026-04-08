---
title: "AI Legal Harness Framework — Requirements"
scope: global
source: "docs/knowledge/REQUIREMENTS.md (adapted from internal case research — this file is the canonical reference)"
last_verified: "2026-04-08"
---

# AI Legal Harness Framework — Requirements

> A reusable, case-agnostic harness for managing civil legal disputes with AI assistance. Designed to enforce fact integrity, legal authority sourcing, and human oversight across every phase of litigation preparation.

---

## Overview

The AI Legal Harness Framework is a structured system for managing civil legal cases using AI assistance. It is not tied to any specific case, jurisdiction, or party. Its purpose is to ensure that AI agents operating inside a legal workflow:

1. Never fabricate or conflate facts
2. Never apply legal rules from training memory alone
3. Always trace every claim to a verifiable source
4. Always respect human approval authority over formal decisions
5. Produce outputs that a retained lawyer can verify in under two minutes

The framework is composed of ten requirement categories, each covering a distinct concern. All categories are interdependent — a weakness in any one category propagates risk to the others.

---

## Design Principles

| # | Principle | Summary |
|---|-----------|---------|
| P-01 | **Facts Are Immutable** | Once a fact is human-verified, it cannot be altered by an AI agent. Only a human can modify, dispute, or supersede a proven fact. |
| P-02 | **Law Comes from Authoritative Sources, Not Memory** | No legal rule may be applied to case facts unless the verbatim statutory text has been loaded from a verifiable source in the current session. |
| P-03 | **Every Claim Must Be Traceable** | Any assertion in any output — email draft, court filing, regulatory complaint — must be traceable to a source fact code, statute citation, and evidence item within two minutes of inspection. |
| P-04 | **Dropped Arguments Stay Dropped** | Once an argument is formally abandoned (with documented reason), no AI agent may resurrect it in any form. The dropped-argument register is checked before every formal document is produced. |
| P-05 | **Human Oversight Is Non-Negotiable** | All formal documents require human approval before delivery. No AI agent may autonomously deliver any output that has external legal effect. |
| P-06 | **Forum Sequencing Is a Hard Rule** | Criminal referrals are always last. Pre-filing forums (consumer ombudsman, regulatory bodies) precede civil filings where strategically advantageous and where sequencing does not prejudice limitation periods. |
| P-07 | **Consistency Is Verified, Not Assumed** | Any value that appears in more than one file (date, amount, entity name) must be verified for consistency by a deterministic field-level check — not inferred from context. |
| P-08 | **Separation of Tiers** | Facts (T1), interpretations (T2), and strategy (T3) occupy separate tiers. T2 and T3 reference T1 by code; they never duplicate T1 content. An AI agent may operate on T2/T3 only after T1 is locked. |

---

## Requirement Categories

| # | File | Category | Req Count | CRITICAL | HIGH | MEDIUM |
|---|------|----------|-----------|----------|------|--------|
| 01 | [REQ-01-fact-integrity.md](requirements/REQ-01-fact-integrity.md) | Fact Integrity | 10 | 4 | 4 | 2 |
| 02 | [REQ-02-law-authority.md](requirements/REQ-02-law-authority.md) | Law Authority & Citation | 10 | 4 | 5 | 1 |
| 03 | [REQ-03-retrieval-strategy.md](requirements/REQ-03-retrieval-strategy.md) | Retrieval Strategy | 8 | 3 | 3 | 2 |
| 04 | [REQ-04-agent-behavior.md](requirements/REQ-04-agent-behavior.md) | Agent Behavior & Constraints | 13 | 5 | 6 | 2 |
| 05 | [REQ-05-verification-gates.md](requirements/REQ-05-verification-gates.md) | Verification Gates | 10 | 6 | 3 | 1 |
| 06 | [REQ-06-evidence-preservation.md](requirements/REQ-06-evidence-preservation.md) | Evidence Preservation | 9 | 4 | 4 | 1 |
| 07 | [REQ-07-human-oversight.md](requirements/REQ-07-human-oversight.md) | Human Oversight | 9 | 4 | 4 | 1 |
| 08 | [REQ-08-forum-sequencing.md](requirements/REQ-08-forum-sequencing.md) | Forum Sequencing | 8 | 3 | 4 | 1 |
| 09 | [REQ-09-strategy-management.md](requirements/REQ-09-strategy-management.md) | Strategy Management | 11 | 3 | 5 | 3 |
| 10 | [REQ-10-memory-management.md](requirements/REQ-10-memory-management.md) | Memory & Session Management | 9 | 3 | 3 | 3 |
| 11 | [REQ-11-strategic-combat.md](requirements/REQ-11-strategic-combat.md) | Strategic Combat & Pressure Management | 10 | 3 | 6 | 1 |
| 12 | [REQ-12-research-osint.md](requirements/REQ-12-research-osint.md) | Research & OSINT Operations | 9 | 3 | 5 | 1 |
| 13 | [REQ-13-ai-tooling-skills.md](requirements/REQ-13-ai-tooling-skills.md) | AI Tooling, Skills & Invocation Rules | 9 | 3 | 6 | 0 |
| 14 | [REQ-14-language-handling.md](requirements/REQ-14-language-handling.md) | Language Handling & Translation | 4 | 0 | 2 | 2 |
| | | **Totals** | **129** | **48** | **60** | **21** |

---

## Design Documents

| Document | Purpose |
|----------|---------|
| [../architecture/skill-ecosystem.md](../architecture/skill-ecosystem.md) | Canonical skill ecosystem document — 4 skills, file contracts, composition, portability, best practices. Consolidated 2026-04-06 from the earlier `SKILL-ECOSYSTEM-DESIGN.md` spec. |

---

## Glossary

The following terms are used consistently across all requirement files.

| Term | Definition |
|------|-----------|
| **Claimant / Client** | The party on whose behalf the legal case is being managed. Never refers to a specific individual in framework documents. |
| **Opposing party / Defendant** | The party against whom claims are made. Never refers to a specific entity in framework documents. |
| **Fact record** | A single, atomically stated factual assertion stored in the proven fact register. Identified by a unique code (e.g., `PF-CATEGORY-NNN`). |
| **Strategic argument** | An entry in the strategy catalogue representing a legal or factual argument deployable in one or more forums. |
| **Dropped argument** | A strategic argument that has been formally abandoned, with documented reason, and placed in the dropped-argument register. |
| **Forum** | Any venue where a legal dispute may be heard or raised: civil court, consumer ombudsman, data protection authority, tax authority, mediation body, criminal court. |
| **Tier 1 (T1)** | The fact tier: human-verified factual assertions. Immutable by AI. |
| **Tier 2 (T2)** | The interpretation tier: legal analysis connecting facts to legal rules. AI-assisted, human-reviewed. |
| **Tier 3 (T3)** | The strategy tier: deployable arguments, forum-specific framings, sequencing decisions. AI-assisted, human-approved. |
| **SOLAR** | Statute-first, Ordered, Literal, Authoritative, Retrievable — the rule requiring verbatim statutory text to be loaded before law is applied to facts. |
| **Hot vault** | The set of statutes and articles currently cited in case documents, stored as markdown for fast retrieval. |
| **Cold vault** | The full-text archive of statutory instruments, judgment PDFs, and official gazettes used for RAG retrieval. |
| **LRS** | Litigation Readiness Score — a 0–100 composite metric measuring the case's readiness to proceed to formal action. |
| **MAD-Judges** | Multi-Agent Debate pattern: three independent AI agents debate a claim before a high-stakes document is released. |
| **GraphRAG** | Graph-based retrieval augmented generation: uses a property graph (e.g., Neo4j) to traverse entity relationships for multi-hop retrieval. |
| **RRF** | Reciprocal Rank Fusion — the algorithm used to merge BM25 (keyword) and dense (vector) retrieval scores into a single ranked list. |
| **RFC 3161** | The IETF standard for trusted timestamps, used to prove a document existed at a given point in time. |
| **ISO/IEC 27037:2012** | The international standard for digital evidence identification, collection, acquisition, and preservation. |
| **Dropped-argument register** | A permanent, append-only log of all abandoned arguments with the reason for abandonment. Never purged. |
| **Devil's advocate review** | An independent critical review of a strategic argument, conducted by a separate AI agent receiving raw facts rather than conclusions. |
| **Limitation period** | The statutory deadline by which a civil claim must be filed. Interruption methods vary by jurisdiction (e.g., formal notice via bailiff). |
| **Res judicata** | The principle that a matter already adjudicated cannot be re-litigated between the same parties. Administrative decisions from regulatory bodies do not typically create res judicata for civil claims. |
| **Session brief** | A short document generated at session start summarising pending reviews, approaching deadlines, and flagged items requiring human decision. |
| **Provenance record** | Metadata attached to every fact record: source document, collection date, SHA-256 hash, RFC 3161 timestamp, approver identity. |
| **Circuit breaker** | A fallback rule that activates when an external dependency (database, timestamp server, retrieval service) is unavailable, preventing silent failure. |

---

## Versioning and Maintenance

- All requirement files share version `1.0` at initial publication.
- Any change to a requirement that affects acceptance criteria or priority requires a version increment and entry in the decision log.
- Deprecated requirements are marked `[SUPERSEDED]` and point to the replacement requirement ID.
- No requirement is ever deleted — superseded entries are retained for audit continuity.
