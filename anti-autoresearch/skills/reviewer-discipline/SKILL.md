---
name: reviewer-discipline
description: "Venue norms for writing a paper critique: the six CVPR reviewer errors, nine phrasings a review must never contain, the ARR vague-to-specific rewrite table, the COLM single-dimension and compute-fairness guards, and the TMLR no-SOTA guard. Run every drafted weakness through it before writing the report. Use when drafting reviewer comments, a self-review of your own draft, a meta-review, or a rebuttal reply. Triggers: \"review this paper\", \"reviewer comments\", \"weakness list\", \"是不是审稿意见写太虚\", \"审稿\"."
---

# Reviewer Discipline

A filter, not a generator. Take a drafted weakness list and rewrite or drop every item that fails a
check below. Apply it whether the paper is someone else's or your own.

## The six CVPR reviewer errors

| Error | The check |
|---|---|
| Ignorance / inaccuracy | Every technical critique points at a specific line, equation, or table cell. |
| Pure opinion | "I dislike X" becomes "X violates principle Y because Z". |
| Novelty fallacy | Never reject for "lack of novelty" without citing the specific prior work; never accept for "novelty" without saying what is new against what. |
| Blank assertion | "This has been done before" carries a citation or it goes. |
| Policy entrepreneurism | Never invent a venue requirement. NeurIPS, ICML, ICLR, and TMLR do not require SOTA, a 70B run, or every baseline. |
| Intellectual laziness | Never reduce an evaluation to one metric. Non-SOTA accuracy with better efficiency, robustness, or interpretability still counts. |

## Nine phrasings to refuse

Each one marks a lazy review. Never write:

1. "The paper is good overall."
2. "The work is okay but not outstanding."
3. "Some experiments are missing", without naming which.
4. "The writing could be improved", without naming where.
5. "Related work is incomplete", without naming which papers.
6. Any verdict that contradicts your own findings, such as "technically sound, but I recommend reject".
7. "I have no further comments", after a substantial finding. A rebuttal update needs an explanation.
8. "The contribution is limited", without naming which contribution and against what baseline.
9. "The novelty is incremental", without saying what would qualify as non-incremental.

## ARR specificity rewrite

Any drafted weakness matching the left column gets rewritten to the right form.

| Vague | Specific |
|---|---|
| "Missing relevant references" | "Missing references to [Smith et al. 2023] and [Jones 2024]" |
| "X is not clear" | "Y and Z are missing from the description of X" |
| "Formulation of X is wrong" | "Formulation of X misses the factor Y" |
| "Not novel" | "Highly similar work [citation], published at least three months prior" |
| "Missing recent baselines" | "Should compare against [Method X, Y, Z] from [citations]" |
| "Algorithm-dataset interaction is problematic" | "Using [decoding method] on [dataset] may lack the training data the n-best list needs" |

## Three venue guards

**COLM dimensional tradeoff.** A weakness in one dimension does not carry a reject on its own: a
reject resting only on "writing is poor" demotes to borderline reject. Strength in one dimension does
not carry an accept either: an accept resting only on "results are great", with method or related work
missing, demotes the same way.

**COLM compute fairness.** Any weakness that reduces to "did not use enough GPUs" or "did not scale to
model size X" gets dropped or weakened. Most authors lack big-lab compute, and penalizing that stifles
the field.

**TMLR no-SOTA.** "Did not achieve SOTA" is not a critique. TMLR states that authors need not obtain
SOTA results.

## Output

Report what the filter changed: how many weaknesses were rewritten, how many dropped, and the reason
for each drop. A weakness list that survives unchanged is a fine outcome; say so rather than inventing
edits.
