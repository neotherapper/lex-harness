---
module: tenancy
pack: greece
version: 0.1.0
loaded_when: task-signal-or-default
trigger_signals:
  - "deposit"
  - "rental damage"
  - "wear and tear"
  - "φυσιολογική φθορά"
  - "balcony rent reduction"
  - "Art. 576"
  - "defect"
  - "rent abatement"
  - "CH1"
  - "CH2"
  - "CH3"
  - "CH4"
  - "CH5"
  - "CC2"
  - "CC3"
articles:
  - AK_574
  - AK_575
  - AK_576
  - AK_577
  - AK_578
  - AK_592
  - AK_599
  - AK_624
case_law_inline_file: case_law_inline.md
adverse_decisions:
  - id: "ΑΠ 399/2023"
    flag: ADVERSE
    instruction: "DO NOT CITE — flag in DECISION_LOG"
last_verified: 2026-04-07
---

# Tenancy module — Greek pack

> Lease relationship under the Greek Civil Code (Αστικός Κώδικας Books III & IV).
> Loaded by every CH1–CH5 case, every CC2 (rent reduction) and CC3 (defect remedy)
> case, and any task whose prompt matches the trigger signals above.

## Articles in this module

- **AK_574** — Concept of lease
- **AK_575** — Lessor's duty to deliver and maintain
- **AK_576** — Lessee's right to rent reduction for defects
- **AK_577** — Lessee's right to terminate for defects
- **AK_578** — Lessor's good-faith warranty
- **AK_592** — Normal wear-and-tear exemption (the operative defence article)
- **AK_599** — Lessee's duty to return the property
- **AK_624** — Lessee's right to repair-deduct

## Inline case law

See `case_law_inline.md` for ≤500-character summaries of:
- ΑΠ 985/2020 (primary 3-element burden test)
- ΑΠ 777/2022 (most recent betterment + depreciation framework)
- ΑΠ 938/2018 (family use = agreed use)
- ΟλΑΠ 705/1979 (repair preferred — full bench)
- ΑΠ 1597/1995 (itemisation requirement)

## Adverse decisions (DO NOT CITE)

- **ΑΠ 399/2023** — flagged ADVERSE per LEGAL_CORPUS_MAP §3.
  This decision narrows tenant defences in a way that hurts our position.
  The skill MUST refuse to cite it and MUST flag any user request that
  proposes citing it as `[ADVERSE-PRECEDENT-BLOCKED]`.
