# Eval-Design Forensics — worked findings

## Worked findings

**Worked HP-EVAL-LEAKAGE (stated preprocessing-before-split, headline, critical, L0):**

```json
{
  "finding_id": "ED001",
  "skill": "eval-design-forensics",
  "pattern_id": "HP-EVAL-LEAKAGE",
  "title": "Preprocessing fit before the split may leak the test set into the reported accuracy",
  "description": "Claim C006 describes the protocol as 'we standardize all features, then split 80/20'. Standardizing before the split fits the scaler on the test rows (Kapoor & Narayanan leakage type L1 — no clean train/test separation), so the headline accuracy may not measure generalization. Discrepancy to verify: confirm whether the scaler was in fact fit on the training partition only and applied to test.",
  "severity": "critical",
  "observability_level_required": 0,
  "evidence": [
    {"claim_id": "C006", "span": "we standardize all features, then split 80/20",
     "location": {"file": "main.tex", "section": "method"}}
  ],
  "verdict_local": "fail",
  "requires_external_check": false,
  "false_positive_risk": "low",
  "recommended_reviewer_action": "Ask the authors whether the scaler/imputer was fit on TRAIN ONLY and then applied to test; if it was fit on all data before the split, the reported accuracy should be re-measured with a leak-free pipeline."
}
```

**Worked needs_external_check (pretraining contamination — hand off, do NOT guess):**

```json
{
  "finding_id": "ED002",
  "skill": "eval-design-forensics",
  "pattern_id": "HP-EVAL-LEAKAGE",
  "title": "Benchmark may be contaminated in the evaluated model's pretraining (not decidable here)",
  "description": "Claim C012 reports a headline score on a widely-published benchmark using a frontier LLM. Whether the model saw this benchmark during pretraining is a black-box question undecidable from the PDF or the repo — NOT an allegation. A domain check would use an exchangeability test (Oren 2023), Min-K% Prob (Shi 2023), Time-Travel (Golchin 2023), or BIG-bench canary strings; this tool does not run them.",
  "severity": "info",
  "observability_level_required": 0,
  "evidence": [
    {"claim_id": "C012", "span": "achieves 91.2 on the public benchmark",
     "location": {"file": "main.tex", "section": "experiments"}}
  ],
  "verdict_local": "needs_external_check",
  "requires_external_check": true,
  "false_positive_risk": "high",
  "recommended_reviewer_action": "Have a domain expert run a contamination probe (Min-K% / exchangeability / Time-Travel) or confirm the benchmark post-dates the model's training cutoff."
}
```

**Worked HP-JUDGE-VALIDITY (conflicted judge, major, L0):**

```json
{
  "finding_id": "ED003",
  "skill": "eval-design-forensics",
  "pattern_id": "HP-JUDGE-VALIDITY",
  "title": "Headline win-rate rests on a judge that shares a family with the proposed system",
  "description": "Claim C021 reports 'our GPT-4-based agent wins 78% of pairwise comparisons, judged by GPT-4'. The judge shares a model family with the proposed system (self-enhancement / self-preference: an evaluator favors its own family's generations), and no human-agreement number is reported. Discrepancy to verify: the 78% is the load-bearing evidence yet the judge is conflicted and unvalidated.",
  "severity": "major",
  "observability_level_required": 0,
  "evidence": [
    {"claim_id": "C021", "span": "wins 78% of pairwise comparisons, judged by GPT-4",
     "location": {"file": "main.tex", "section": "experiments"}}
  ],
  "verdict_local": "warn",
  "requires_external_check": false,
  "false_positive_risk": "medium",
  "recommended_reviewer_action": "Ask for a human-agreement validation of the judge (correlation/kappa) and a family-disjoint or position-swapped judge; report the win-rate under a judge that does not share a family with the proposed system."
}
```

**Worked HP-SELECTIVE-REPORTING (declared-but-unreported datasets, L0):**

```json
{
  "finding_id": "ED004",
  "skill": "eval-design-forensics",
  "pattern_id": "HP-SELECTIVE-REPORTING",
  "title": "Two declared evaluation datasets are not reported and not in the appendix",
  "description": "Claim C008 declares 'we evaluate on five datasets {A,B,C,D,E}', but every results table reports only {A,B,C} and no appendix reports D or E. Discrepancy to verify: ask for the D/E results, or an explicit reason for the omission. (De-dup: this is declared-but-unreported, not best-as-mean (HP-AGG-DRIFT) or a missing expected baseline (HP-MISSING-BASELINE).)",
  "severity": "major",
  "observability_level_required": 0,
  "evidence": [
    {"claim_id": "C008", "span": "we evaluate on five datasets",
     "location": {"file": "main.tex", "section": "experiments"}}
  ],
  "verdict_local": "warn",
  "requires_external_check": false,
  "false_positive_risk": "low",
  "recommended_reviewer_action": "Ask the authors for the results on datasets D and E (or an explicit justification for omitting them); confirm the headline survives once the declared conditions are all reported."
}
```
