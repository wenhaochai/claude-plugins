# Integrity Forensics Report — headline_inflate

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| HL001 | consistency | minor | HP-NUM-INFLATE | headline_inflate.tex:abstract | high |

### Detail

**HL001 — Headline number not found in any results table** (minor)

- The abstract cites 85.3% accuracy but no extracted table cell reports that value; may be a different setting, a rounding artifact, or an inflated headline.
  - evidence `C003`: “FooNet reaches 85.3\% accuracy, improving from a 73.1\% baseline to 78.0\% accuracy, a 6.7\% relative improvement.”
  - reviewer action: Locate the headline number's source table/row; confirm the setting it refers to.

## Counts

- critical: 0  ·  major: 0  ·  minor: 1  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
