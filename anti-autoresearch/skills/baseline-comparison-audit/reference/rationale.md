# Baseline Comparison Audit — rationale and ARIS lineage

## ARIS lineage

> Adapted from ARIS `paper-claim-audit` — its **scope-overclaim** and
> **delta-arithmetic** checks, reframed from "paper vs result files" to **"is the
> SOTA claim earned, and is the comparison a fair fight?"** — plus a per-domain
> baseline profile and a completeness / fairness / significance split. A favourite
> autoresearch shortcut is to claim SOTA while omitting the obvious recent baseline,
> to beat an undertuned one, or to write "outperforms" over error bars that overlap.
> This skill is the constraint that asks for the fair fight, pointed at a third
> party's submission, and it stays honest about what it cannot settle from a PDF.

## Why this exists

An autoresearch pipeline (or rushed human) optimises for the *headline* and treats
the comparison table as scaffolding to fill, not a fair experiment to run. The
repeatable failure modes:

- **Completeness** — "achieves state-of-the-art on GSM8K" while the obvious recent
  baseline a 2024–2026 reviewer expects is simply absent from the table, or the
  strong classical **floor** (BM25 for retrieval, GBDT for tabular, a linear/naive
  forecaster for time-series) is skipped while only weak neural baselines are beaten.
  `HP-MISSING-BASELINE`
- **Fairness** — the proposed method is tuned for 100 epochs / 5 seeds / extra data,
  the baseline is run at default settings for 10; or the compared rows use different
  backbones, splits, or eval protocols; or the single most informative baseline —
  the method's **own backbone with the new component removed, at an identical
  budget** — is missing. `HP-WEAK-BASELINE`
- **Significance** — "consistently outperforms" on a 0.3-point gap with overlapping
  error bars, with no variance / no seed count reported at all, or resting on a single
  dataset too thin for the "consistent / across-the-board" wording. `HP-SIG-OVERLAP`
- **Delta arithmetic** — "improves over the strongest baseline by 16%" when the
  baseline row is 73.1 and the proposed row is 78.0 (+6.7% relative / +4.9 points),
  the two operands sitting in *different* cells so the single-sentence deterministic
  pass cannot pair them. `HP-DELTA-ERROR` (cross-row form)

None of these is inherently misconduct — they are what an optimizing agent does when
nothing forces a fair comparison. The *stated* version is decidable at **L0** from
the manuscript; the *verified* version (real configs, real seeds) deepens at **L2**.
What this skill will **not** do is *guess*: where no domain profile exists and the
leaderboard search is inconclusive, the completeness question is handed off as
`needs_external_check`, not invented.
