# Integrity Forensics Report — dup_table

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| PRES001 | presentation | minor | HP-DUP-TABLE | dup_table.tex:table:1 | high |

### Detail

**PRES001 — Two tables have identical numeric content** (minor)

- table:1 and table:2 contain the same ordered cell values ([73.1, 78.0]); may be padding or an un-updated copy-paste.
  - evidence `C001`: “Baseline \cite{smith2024bar} & 73.1 \\”
  - evidence `C003`: “Baseline \cite{smith2024bar} & 73.1 \\”
  - reviewer action: Check whether the two tables are meant to differ; if identical, ask why both are present.

## Counts

- critical: 0  ·  major: 0  ·  minor: 1  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
