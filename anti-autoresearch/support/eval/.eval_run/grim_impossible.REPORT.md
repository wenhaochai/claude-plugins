# Integrity Forensics Report — grim_impossible

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| GRIM001 | consistency | minor | HP-GRANULARITY-IMPOSSIBLE | grim_impossible.tex:body | low |

### Detail

**GRIM001 — Reported proportion is not achievable for the stated N** (minor)

- 84.7% over N=500 integer items is not round(k/500) at 1 decimal place(s) for any integer k (nearest achievable 84.8%). The value, its precision, or N may be misreported, or trials may have been excluded.
  - evidence `C014`: “On a held-out test set of 500 examples, FooNet's accuracy is 84.7\%.”
  - reviewer action: Ask the authors to reconcile the value, its precision, and the exact denominator N (e.g. excluded/invalid items, or a macro/weighted average rather than a simple proportion).

## Counts

- critical: 0  ·  major: 0  ·  minor: 1  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
