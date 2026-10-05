# Integrity Forensics Report — defensive_hedge

**Verdict:** 🟢 CLEAN_GIVEN_EVIDENCE  ·  **Observability:** L1  ·  **Taxonomy:** v0.5  ·  **Adjudicator:** deterministic-rules-v0

> This is decision SUPPORT for a human reviewer. It flags discrepancies to investigate — it does **not** judge misconduct. `CLEAN_GIVEN_EVIDENCE` means "nothing checkable at L1 is broken", not "the paper is honest".

## Findings (evidence first)

| ID | Dimension | Severity | Pattern | Where | FP-risk |
|----|-----------|----------|---------|-------|---------|
| — | — | none above info | — | — | — |

### Detail

## AI Writing-Style Impressions — NOT integrity findings · ZERO verdict weight

> Transparent, itemized impressions of AI-generated **writing style**. These are **not** factual/integrity inconsistencies and carry **zero** weight on the verdict above — a paper can be `CLEAN_GIVEN_EVIDENCE` and still list many. No authorship probability is implied; this is reviewer-impression context, not a judgment.

| ID | Signal | Where |
|----|--------|-------|
| AIS001 | AIS-DEFENSIVE-HEDGE | defensive_hedge.tex:introduction |

### Impression detail

**AIS001 — Pervasive defensive-hedge writing across multiple sections** (`AIS-DEFENSIVE-HEDGE` · impression, no verdict weight)

- 5 distinct defensive-hedge constructions (e.g. "we do not claim …", "not X but rather Y") across 3 non-excluded sections (body, introduction, method). The text repeatedly defends against anticipated objections instead of directly stating what was done — a common AI writing-style tell that lowers information density. This is a STYLE IMPRESSION with ZERO verdict weight, not a factual inconsistency and not an authorship verdict. If a specific hedge instead reveals a real scope/evaluation limitation, that is a separate integrity finding (HP-SCOPE-INFLATE / eval-design-forensics).
  - where `C009`: “We do not claim that this routing module is optimal.”
  - where `C010`: “This does not mean that simpler designs cannot work.”
  - where `C012`: “We are not proposing a fundamentally new architecture.”
  - not-necessarily-AI: Some venues / AI reviewers penalize the ABSENCE of caveats, so measured hedging is a legitimate strategic choice; a single scoping sentence is not the pattern.
  - reviewer note: Skim the cited sentences: if the paper over-hedges in its contribution/body, that lowers readability. Impression only — not misconduct, not an authorship judgment.

## Counts

- critical: 0  ·  major: 0  ·  minor: 0  ·  info: 0
- demoted for observability: 0  ·  demoted unanchored: 0
- AI writing-style impressions (zero verdict weight): 1

## Limitations

- L1 run: code/result-level patterns (fake GT, self-normalization, phantom results, dead metrics) were NOT verifiable and appear only as info-level 'could-not-check' signals.

_Human review required: always. This report does not issue a verdict on misconduct._
