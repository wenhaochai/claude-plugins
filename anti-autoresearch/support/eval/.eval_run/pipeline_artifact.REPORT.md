# Integrity Forensics Report — pipeline_artifact

**Verdict:** 🟡 SOFT_FLAGS  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| PRES001 | presentation | minor | HP-PIPELINE-ARTIFACT | pipeline_artifact.tex:table:1 | low |

### Detail

**PRES001 — Leftover pipeline/assistant string in finished text** (minor)

- The exact phrase "As an AI language model" appears in table:1 (claim C010). This is a verbatim pipeline/template leftover that should not survive into a finished paper. The check flags the CHECKABLE STRING only — it does NOT infer who or what produced the text (exact substring match, not stylometry, not an AI-text classifier). If this string instead FEEDS a reported number/figure, it is HP-PLACEHOLDER-DATA (family D, critical), not this surface signal.
  - evidence `C010`: “racy, \%, mean of 5 seeds). As an AI language model, I cannot independently ver”
  - reviewer action: Confirm the string is a genuine leftover and not a deliberate quotation/discussion of such text (e.g. a paper studying LLM outputs / refusal messages); if it is a leftover, the text should be cleaned. This is a surface signal, not an authorship or misconduct finding.

## Counts

- critical: 0  ·  major: 0  ·  minor: 1  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 0

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
