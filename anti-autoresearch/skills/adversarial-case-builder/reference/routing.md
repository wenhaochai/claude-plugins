# Adversarial Case Builder — auditor routing

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Level | Verdict weight |
|---------|---------------------|------|----------------|
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? | L0 | yes (via adjudicator) |
| `experiment-forensics` | Are reported numbers what the code computes? (fake GT, self-norm, phantom) | L2 | yes |
| `baseline-comparison-audit` | Right baselines present, tuned, "SOTA" earned? | L0 stated / L2 verified | yes |
| `citation-forensics` | Do cited papers exist and support the claim made? | L0 | yes |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary) | L0 | capped at minor |
| **`adversarial-case-builder`** (this) | **Strongest *anchored* rejection memo + defense** | **any (inherits anchors' level)** | **none (memo-only, capped at info)** |

**This skill detects nothing new.** It does not re-read the paper to invent
objections, does not assign severities the upstream auditors didn't already license,
and does not originate a substantive flag. It *narrates* the worst case the existing
evidence supports and stress-tests it. A *new* discrepancy belongs to the auditor that
owns it (code/result fraud → `experiment-forensics` at L2; existence/context →
`citation-forensics`; "SOTA/first" → `baseline-comparison-audit`), not here.
