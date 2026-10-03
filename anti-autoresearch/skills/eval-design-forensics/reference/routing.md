# Eval-Design Forensics — auditor routing

## How this differs from the other auditors (route correctly)

This skill is the **L0/L1-stated / L2-verified** sibling of
`baseline-comparison-audit` and `proof-derivation-forensics` (both verdict-bearing
**without a repo**) — *not* the L2-only `experiment-forensics`.

| Auditor | Question it answers | Level |
|---------|---------------------|------|
| **`eval-design-forensics`** (this) | **Is the evaluation a VALID measurement of the claim, and is the reporting complete?** (train/test leakage, conflicted/unvalidated LLM judge, declared-but-unreported / metric-switch / best-without-held-out) | **L0/L1 stated · L2 verified** |
| `experiment-forensics` | Are the reported numbers what the **code** computes? (fake/derived GT, self-norm, phantom, dead metric) | L2 |
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? (owns `HP-AGG-DRIFT`, `HP-APPENDIX-CONTRA`, text-only `HP-SCOPE-INFLATE`) | L0 |
| `baseline-comparison-audit` | Are the right baselines present, fairly tuned, and is "SOTA" earned? (owns `HP-MISSING-BASELINE`, `HP-SIG-OVERLAP`) | L0 stated / L2 verified |
| `citation-forensics` | Do the cited papers exist and support the claim? | L0 |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary, capped at minor) | L0 |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

**Do NOT raise here** (hand off instead):

- **An LLM generating the GROUND-TRUTH labels/targets** (not judging outputs) →
  `experiment-forensics` `HP-FAKE-GT` (L2). The clean split: a judge whose
  **preference IS the reported metric** is `HP-JUDGE-VALIDITY` (here, L0/L1 stated);
  a model that **fabricates the reference** the metric is computed against is
  `HP-FAKE-GT` (there, needs the code, L2). When unsure which, prefer the L2 route
  and set `needs_external_check`.
- **best-reported-as-mean** (the aggregation lies) → `consistency-audit`
  `HP-AGG-DRIFT`; **thin overall scope** with no comparison → `consistency-audit`
  `HP-SCOPE-INFLATE`; **appendix-vs-main disagreement on the same quantity** →
  `consistency-audit` `HP-APPENDIX-CONTRA`.
- **A never-mentioned expected SOTA baseline** (completeness) →
  `baseline-comparison-audit` `HP-MISSING-BASELINE`; a "consistently/across-the-board"
  comparison resting on **one dataset** → `baseline-comparison-audit`'s single-dataset
  `HP-SIG-OVERLAP`.
- **Whether a reported number matches the code** (fake GT, self-norm, phantom) →
  `experiment-forensics` (L2); **whether a cited paper exists / is used in context**
  → `citation-forensics`; **surface / AI-flavor** → `presentation-signals`.

`HP-SELECTIVE-REPORTING` is **scoped to declared-but-unreported / cherry-picked-
among-shown** — the gap between what the setup *promised* and what the tables
*deliver*. It never re-emits the four patterns above.
