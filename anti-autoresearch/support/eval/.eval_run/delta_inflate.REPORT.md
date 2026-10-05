# Integrity Forensics Report — delta_inflate

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| NUM001 | consistency | major | HP-DELTA-ERROR | delta_inflate.tex:abstract | low |

### Detail

**NUM001 — Stated improvement contradicts its operands** (major)

- Text states a 16.7% relative change, but 73.1->78 is 6.7% relative (+4.9 absolute points).
  - evidence `C003`: “FooNet reaches 78.0\% accuracy, improving from a 73.1\% baseline to 78.0\% accuracy, a 16.7\% relative improvement.”
  - reviewer action: Ask the authors to reconcile the stated delta with the reported operands; verify relative-vs-absolute convention.

## Counts

- critical: 0  ·  major: 1  ·  minor: 0  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
