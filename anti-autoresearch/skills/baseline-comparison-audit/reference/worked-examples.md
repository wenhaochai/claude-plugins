# Baseline Comparison Audit — worked findings

**Worked HP-MISSING-BASELINE (headline SOTA, critical):**

```json
{
  "finding_id": "BC001",
  "skill": "baseline-comparison-audit",
  "pattern_id": "HP-MISSING-BASELINE",
  "title": "Headline SOTA claim omits an expected, pre-dating same-benchmark baseline",
  "description": "Claim C007 asserts 'state-of-the-art on GSM8K'. The expected-set facts list Self-Consistency CoT (2023; same benchmark; predates this submission per paperswithcode <url>, accessed <date>) as a standard strong baseline, but it appears in no comparison/baseline claim in the ledger. Discrepancy to verify: a 'state-of-the-art' headline that omits an obvious pre-dating baseline — confirm the claim survives once it is included, or whether the omission is justified.",
  "severity": "critical",
  "observability_level_required": 0,
  "evidence": [
    {"claim_id": "C007", "span": "achieves state-of-the-art accuracy on GSM8K",
     "location": {"file": "main.tex", "section": "abstract"}}
  ],
  "verdict_local": "fail",
  "requires_external_check": false,
  "false_positive_risk": "low",
  "recommended_reviewer_action": "Ask the authors to add Self-Consistency CoT (and any other pre-dating leaderboard baseline) or to justify its omission as concurrent/unavailable; confirm the SOTA claim survives the comparison."
}
```

**Worked needs_external_check (off-profile — hand off, do NOT guess):**

```json
{
  "finding_id": "BC002",
  "skill": "baseline-comparison-audit",
  "pattern_id": "HP-MISSING-BASELINE",
  "title": "Baseline completeness not settleable internally (off-profile benchmark)",
  "description": "Claim C011 claims to 'outperform all prior methods' on a niche benchmark not covered by the baseline profile, and the leaderboard search was inconclusive. Completeness cannot be decided from the available inputs — NOT an allegation of an omission, only a hand-off for a domain expert to confirm the expected baseline set.",
  "severity": "info",
  "observability_level_required": 0,
  "evidence": [
    {"claim_id": "C011", "span": "outperform all prior methods",
     "location": {"file": "main.tex", "section": "experiments"}}
  ],
  "verdict_local": "needs_external_check",
  "requires_external_check": true,
  "false_positive_risk": "high",
  "recommended_reviewer_action": "Have a domain expert enumerate the expected baseline set for this benchmark and check it against the paper's comparison table."
}
```

**Worked HP-WEAK-BASELINE (L2, config-confirmed budget gap):**

```json
{
  "finding_id": "BC003",
  "skill": "baseline-comparison-audit",
  "pattern_id": "HP-WEAK-BASELINE",
  "title": "Compared rows use an unequal training budget",
  "description": "Claim C019 reports the proposed method (78.0) 'outperforms the baseline' (73.1) in Table 2. configs/ours.yaml sets epochs=100, n_seeds=5 (sha256 a1b2c3…) while configs/baseline.yaml sets epochs=10, n_seeds=1 — a 10x budget asymmetry in the compared rows, with no matched-budget / equal-budget ablation-as-baseline run reported. Discrepancy to verify: the 4.9-point gap may reflect compute, not method.",
  "severity": "major",
  "observability_level_required": 2,
  "evidence": [
    {"claim_id": "C019", "span": "our method (78.0) outperforms the baseline (73.1)",
     "location": {"file": "main.tex", "section": "table:2"}}
  ],
  "verdict_local": "warn",
  "reviewer": {"model": "gpt-5.5", "reasoning": "xhigh", "thread_id": "<codex thread>", "deterministic": false},
  "requires_external_check": false,
  "false_positive_risk": "low",
  "recommended_reviewer_action": "Ask the authors for the baseline under the same epochs/seeds/backbone budget as the proposed method (the config delta is at configs/{ours,baseline}.yaml), or to document why the budgets differ."
}
```
