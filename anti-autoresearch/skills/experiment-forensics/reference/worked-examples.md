# Experiment Forensics — worked L2 finding

**Worked L2 finding** (the full, copyable shape):

```json
{
  "finding_id": "EF002",
  "skill": "experiment-forensics",
  "pattern_id": "HP-SELF-NORM",
  "title": "Headline score is normalized by the model's own output maximum",
  "description": "The abstract headline metric (claim C014) is reported as 0.98. In the pipeline, results/main.json stores score_norm=0.98 computed at src/eval.py:88 (sha256 a1b2c3…) as raw_score / max(model_outputs) — the divisor is the model's OWN output max, not a fixed scale or a cross-method min–max. The raw score at the same key is 0.41, and no raw column appears in the paper. Discrepancy to verify: a metric approaching 1.0 via self-referential normalization is not comparable to baselines.",
  "severity": "critical",
  "observability_level_required": 2,
  "evidence": [
    {"claim_id": "C014", "span": "achieves a score of 0.98",
     "location": {"file": "main.tex", "section": "abstract"},
     "artifact_hash": "<sha256 of main.tex from the ledger's evidence_anchor>"}
  ],
  "verdict_local": "fail",
  "reviewer": {"model": "gpt-5.5", "reasoning": "xhigh", "thread_id": "<codex thread>", "deterministic": false},
  "false_positive_risk": "low",
  "requires_external_check": false,
  "recommended_reviewer_action": "Ask the authors for the raw (un-normalized) score and the exact normalization denominator; confirm the same normalization is applied identically to all baselines. If the divisor is the model's own output statistics, the 0.98 headline is not a valid cross-method comparison."
}
```
