# Integrity Forensics Report — stat_inconsistency

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| STAT001 | consistency | major | HP-STAT-INCONSISTENCY | stat_inconsistency.tex:body | medium |

### Detail

**STAT001 — Reported p-value is inconsistent with its test statistic** (major)

- Reported z=1.1, p=0.036; recomputed two-tailed p in [0.2692,0.2735] (one-tailed [0.1346,0.1368], backend stdlib-normaldist). reported p claims significance the statistic does not support. May reflect a one-tailed test, adjusted/Welch df, or a typo.
  - evidence `C019`: “The gain over the baseline is statistically significant (z = 1.10, p = 0.036).”
  - reviewer action: Ask whether the test was one- or two-tailed, whether p was multiplicity-adjusted, and whether the df/statistic are correct.

## Counts

- critical: 0  ·  major: 1  ·  minor: 0  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
