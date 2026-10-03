# Routing

## Contents

- How this differs from the other auditors (route correctly)

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Level |
|---------|---------------------|------|
| **`proof-derivation-forensics`** (this) | **Does the WRITTEN proof/derivation actually establish its theorem? (gap / circularity / invalid step / symbol drift / smuggled assumption)** | **L1 — from the written math (LaTeX source), no external lookup** |
| `consistency-audit` | Does the paper contradict ITSELF (numbers, scope, method)? incl. abstract-general-vs-theorem-narrow (`HP-THEOREM-SCOPE-DRIFT`) | L0 |
| `citation-forensics` | Does a cited theorem EXIST and is it cited in a context it supports? | L0 |
| `experiment-forensics` | Are reported numbers what the code actually computes? (fake GT, self-norm, phantom) | L2 |
| `baseline-comparison-audit` | Are the right baselines present, tuned, and is "SOTA" earned? | L0 stated / L2 verified |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

**Do NOT raise here** (hand off instead):
- abstract/title advertises generality the *theorem statement* doesn't have →
  `consistency-audit` owns `HP-THEOREM-SCOPE-DRIFT`; the headline framing goes to
  `adversarial-case-builder`. *This skill owns the proof-internal twin:* the proof
  uses an assumption the **theorem statement** never lists (`HP-ASSUMPTION-SMUGGLE`).
- whether a cited result **exists** or is **cited in the right context** →
  `citation-forensics`. *This skill owns the proof-internal twin:* a cited theorem is
  **applied without verifying its hypotheses** at the point of use
  (`HP-PROOF-OBLIGATION-GAP`).
- results-table arithmetic / delta / aggregation / number coherence →
  `consistency-audit`. This skill audits the **derivation**, not results tables.
- code/result-level fraud (fake GT, self-normalization, phantom numbers) →
  `experiment-forensics` at **L2**. Family G never reaches for code; if you think a
  flaw needs the code to decide, it is not a proof-validity finding.
- "first / SOTA / novel" external truth → emit `needs_external_check` and hand to
  `baseline-comparison-audit` + `citation-forensics`, never a guess.
