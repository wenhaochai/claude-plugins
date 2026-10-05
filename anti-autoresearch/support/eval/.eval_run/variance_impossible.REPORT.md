# Integrity Forensics Report — variance_impossible

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| VAR001 | consistency | major | HP-VARIANCE-IMPOSSIBLE | variance_impossible.tex:body | low |

### Detail

**VAR001 — Reported SD exceeds the maximum possible for a bounded metric** (major)

- SD 18 is reported at mean 98 for a metric bounded in [0,100] (%); the largest attainable SD there is 15.8 (Bhatia-Davis, sample n=5). The SD, the mean, the metric range, or an SD-vs-SEM label may be misreported.
  - evidence `C016`: “Averaged over 5 seeds, FooNet's accuracy is 98.0\% with a standard deviation of 18.0\%.”
  - reviewer action: Confirm the dispersion is a standard deviation (not SEM/CI), that mean and SD share a scale, the metric's true range, and the sample size used for the variance.

## Counts

- critical: 0  ·  major: 1  ·  minor: 0  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
