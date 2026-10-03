# Consistency Audit — auditor routing

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Level |
|---------|---------------------|------|
| **`consistency-audit`** (this) | **Does the paper contradict ITSELF / does described method = evaluated method?** | **L0 — intra-paper, no external lookup** |
| `experiment-forensics` | Are the reported numbers what the code actually computes? (fake GT, self-norm, phantom) | L2 |
| `baseline-comparison-audit` | Are the right baselines present, tuned, and is "SOTA" earned? | L0 stated / L2 verified |
| `citation-forensics` | Do the cited papers exist and support the claim made? | L0 |
| `proof-derivation-forensics` | Does the WRITTEN proof/derivation actually establish its theorem? (gap / circularity / invalid step / symbol drift / smuggled assumption) | L1 |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary, capped at minor) | L0 |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

**Do NOT raise here** (hand off instead): code/result-level fraud → `experiment-forensics`
(needs L2); "first / SOTA / beats prior work" external truth → `baseline-comparison-audit`
+ `citation-forensics` (emit `needs_external_check`); citation existence/context →
`citation-forensics`; proof / derivation validity (a theoretical relation that must be
*derived*, not measured — gap / circularity / invalid step / symbol drift / smuggled
assumption) → `proof-derivation-forensics` (family G); surface/AI-flavor →
`presentation-signals`; the rejection memo → `adversarial-case-builder`. This skill
never reaches outside the paper.
