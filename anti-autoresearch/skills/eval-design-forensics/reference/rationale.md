# Eval-Design Forensics — rationale and acknowledgements

## Why this exists

An optimizing pipeline (or rushed human) treats the evaluation as a number to make
go up, not a measurement to keep valid. The repeatable failure modes — distinct
from "is the number real?" (family D) — are:

- **Leakage** — the train/test boundary is broken (preprocessing fit before the
  split, no held-out set, duplicates across splits, a random split over time-ordered
  data, the same subject in both splits, an evaluated LLM that saw the benchmark in
  pretraining), so the reported score may not measure **generalization** at all.
  `HP-EVAL-LEAKAGE`
- **Judge validity** — the headline rests on an automatic **LLM judge** that is
  *conflicted* (the same model/family as a compared system, so its preference for
  that system is the "evidence") or *unvalidated* (no human-agreement correlation,
  no position/length bias control). `HP-JUDGE-VALIDITY`
- **Selective reporting** — a dataset / baseline / metric / seed-count the setup
  **explicitly declares** is dropped from the results, the metric is **switched**
  across tables to keep the method ahead, or "we report the best run/prompt/
  checkpoint" with **no held-out selection set** (selecting on the test set).
  `HP-SELECTIVE-REPORTING`

None of these is inherently misconduct — they are what an agent does when nothing
forces a *valid* evaluation. The **stated** version is decidable at **L0/L1** from
the described protocol; the **verified** version (real split/preprocessing/result
files) deepens at **L2**. What this skill will **not** do is *guess*: three leakage
subtypes are undecidable even with the repo and are handed off as
`needs_external_check`, not invented (see below).

## Acknowledgements

The taxonomy this skill operationalizes is reframed from the ML-evaluation-methodology
literature for **third-party** forensics — ledger-anchored findings, observability
tiers, and reviewer ≠ adjudicator:

- **Kapoor, S. & Narayanan, A. (2023),** "Leakage and the reproducibility crisis in
  machine-learning-based science," *Patterns* — the eight leakage types / three
  categories that `HP-EVAL-LEAKAGE` adopts and paraphrases (**priority ack**).
  Contamination methods are **named only**, never run: Oren et al. (2023) exchangeability
  test; Shi et al. (2023) Min-K% Prob; Golchin & Surdeanu (2023) Time-Travel; the
  BIG-bench (Srivastava et al. 2022) canary-string convention.
- **Zheng et al. (2023),** "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" —
  self-enhancement bias and the human-agreement bar behind `HP-JUDGE-VALIDITY`;
  **Panickssery et al. (2024),** self-preference (evaluators favor their own
  generations); **Wang et al. (2024),** position bias in LLM evaluators.
- **Dodge et al. (2019),** "Show Your Work: Improved Reporting of Experimental Results,"
  and **Pineau et al. (2021),** the ML Reproducibility Checklist (NeurIPS 2019
  Reproducibility Program report) — the under-reporting norms behind
  `HP-SELECTIVE-REPORTING`.
