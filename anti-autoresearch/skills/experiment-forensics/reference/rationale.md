# Experiment Forensics — rationale, ARIS lineage, acknowledgements

## Contents

- ARIS lineage
- Why this exists
- Core principle (two independence axes)
- Acknowledgements

## ARIS lineage

> Adapted from ARIS `experiment-audit` (#57/#131), reframed for the reviewer side.
> The original audits *your own* experiment before you claim results; this audits a
> *third party's* submission. The crucial reframe: at **L0/L1 (no code)** these
> patterns are **not decidable** — they appear only as info-level "could-not-verify"
> signals. **Code-level fraud requires L2.** A PDF can never produce a fraud verdict.

## Why this exists

LLM-driven research pipelines (and rushed human work) produce results that *look*
computed but are not what the paper claims. The repeatable failure modes — ported
from ARIS's experiment-integrity audit — are:

1. **Fake ground truth** — the eval "reference/target" is *derived from model
   outputs* and reported as performance, not as a labeled proxy. `HP-FAKE-GT`
2. **Score self-normalization** — a metric divided by the model's **own** max/min/
   mean to approach 1.0; no raw score shown. `HP-SELF-NORM`
3. **Phantom results** — a paper number maps to a result file or metric key that
   does not exist (or a function never called). `HP-PHANTOM-RESULT`
4. **Dead metric code** — a metric defined in eval code, discussed in the paper,
   but never called / never present in any result file. `HP-DEAD-METRIC`
5. **Scope inflation (verified)** — "comprehensive/robust/SOTA" while the repo
   actually ran 1–2 datasets/seeds/configs. `HP-SCOPE-INFLATE`
6. **Method drift (confirmed)** — the method *described* differs from the method
   *evaluated* (A-lite, A+oracle, extra data, different backbone, test-time labels
   the method claims not to use). `HP-METHOD-DRIFT`
7. **Synthesized-looking results** — numbers across configs related by a too-clean
   arithmetic pattern ("不像跑出来的"). `HP-SUSPICIOUS-REGULARITY`
8. **Placeholder / fake data in released code** — the released code still ships
   placeholder/dummy/fake data (e.g. a `# fake data for plotting` annotation, a
   `TODO: replace with real data`, a hard-coded `np.random.*` array) and a *reported*
   figure/number is drawn from it rather than from a real run. `HP-PLACEHOLDER-DATA`
   (flag the checkable code marker; do not infer who wrote it)
9. **Result ≠ artifact** — the code / result artifacts, read or run as released, produce
   numbers *different* from the paper's reported values for the same experiment.
   `HP-RESULT-ARTIFACT-MISMATCH` (an implementation that computes a different
   loss/normalization/architecture than the equations state is `HP-METHOD-DRIFT`, not this)
10. **Missing reproducibility artifacts** — an empirical / agent / LLM paper ships
    neither code nor the prompts/configs/hyperparameters its results depend on, so the
    claim cannot be reproduced even in principle (the *absence* is L0-stated; *what its
    results specifically need* is L2-verified). `HP-MISSING-REPRO-ARTIFACT`

These are NOT inherently misconduct — they are failure modes of optimizing agents
that lack an integrity constraint. This skill is that constraint, pointed outward,
and it stays honest about what it can and cannot see.

## Core principle (two independence axes)

**The executor (Claude) collects paths + the ledger and passes them through; a
fresh, different-family reviewer (codex) reads the code and proposes findings; a
deterministic tool decides the verdict.** Both axes from
`references/reviewer-independence.md` hold:

- **Layer 1 — cross-model (executor ≠ reviewer).** The executor never summarizes,
  pre-judges, or leaks a hunch into the prompt — it ships only paths + `claims.json`
  + the checklist + the observability level. The reviewer is a different model family.
- **Layer 2 — reviewer ≠ adjudicator.** The reviewer is demoted from *judge* to
  *evidence-extractor*: it emits span-anchored findings; `tools/adjudicate_findings.py`
  computes `overall_verdict` by fixed rules. Same ledger + same findings → same
  verdict, with no model in the final decision.

## Acknowledgements

Ports the A–F integrity checks from ARIS `experiment-audit`, motivated by
community-reported issues (#57, #131) where executor agents fabricated ground truth
and self-normalized scores. Reframed for third-party forensics: ledger-anchored
findings, observability tiers, and reviewer ≠ adjudicator.
