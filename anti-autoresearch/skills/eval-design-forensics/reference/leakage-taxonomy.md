# Eval-Design Forensics — Kapoor & Narayanan leakage taxonomy

## The Kapoor & Narayanan leakage taxonomy (adopted — paraphrased)

`HP-EVAL-LEAKAGE` adopts the **eight leakage types in three categories** of Kapoor &
Narayanan (2023), paraphrased. The reviewer maps each finding to one type and records
it in the `description`.

| K&N category (the leakage **TYPE**) | The tell (subtypes) | This repo's **observability** | Common false positive |
|---|---|---|---|
| **L1 — no clean train/test separation** | (a) no held-out test set at all; (b) preprocessing (scaling / imputation / resampling) **fit on all data before the split**; (c) feature selection fit before the split; (d) duplicate / near-duplicate records across splits | **L0** stated / **L2** verified | a transductive / semi-supervised design where overlap is **intended and declared**; preprocessing fit on **train only**, then applied to test (the *correct* pattern) |
| **L2 — illegitimate (proxy) feature** | a feature that stands in for the target, or would be unavailable at prediction time | **needs_external_check** (domain judgment) | a "proxy-looking" feature that is **genuinely available** at prediction time |
| **L3 — test set not from the distribution of interest** | (a) **temporal** leakage (random split over time-ordered data / training on the future); (b) **non-independence** (same subject / patient / group in both splits); (c) **sampling bias** in the test set | (a),(b) **L0** stated / **L2** verified; (c) **needs_external_check** | a correctly time-respecting split; a standard fixed benchmark split the field uses |
| **(LLM-specific) pretraining / benchmark contamination** | the evaluated model may have seen the public benchmark during pretraining | **needs_external_check** (black-box) — name Oren 2023 (exchangeability), Shi 2023 (Min-K%), Golchin 2023 (Time-Travel), BIG-bench canary; **never run them** | a benchmark released **after** the model's training cutoff, or a corpus **documented to exclude** it |

> ⚠️ **Two scales — do not conflate them.** K&N's **L1 / L2 / L3** are leakage-*type*
> labels (severity-ordered *categories of leak*). This repo's **L0 / L1 / L2** are
> *observability* levels (what you can *see*: PDF / +source / +repo). They are
> orthogonal. A K&N-**L1** preprocessing leak that is *stated* in the protocol is
> decidable at observability-**L0**. Every finding carries **both**: the K&N type in
> `description`, the observability in `observability_level_required`.
