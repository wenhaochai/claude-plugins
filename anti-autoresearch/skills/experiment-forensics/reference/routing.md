# Experiment Forensics — routing to other auditors

## Contents

- How this differs from the other auditors (route correctly)
- When NOT to use this skill

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Level |
|---------|---------------------|------|
| **`experiment-forensics`** (this) | **Are the reported numbers what the eval code actually computes?** (fake/derived GT, self-norm, phantom result, dead metric, verified scope, method drift, placeholder/fake data, code↔paper mismatch, missing repro artifacts) | **L2** (L0/L1 → info-only; missing-repro absence is L0-stated, surfaced info here) |
| `consistency-audit` | Does the paper contradict ITSELF / does described method = evaluated method? | L0 |
| `baseline-comparison-audit` | Are the right baselines present, tuned, and is "SOTA" earned? | L0 stated / L2 verified |
| `citation-forensics` | Do the cited papers exist and support the claim made? | L0 |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary, capped at minor) | L0 |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

**Do NOT raise here** (hand off instead): pure text-vs-text contradiction or
scope-vs-evidence-in-text → `consistency-audit`; "first / SOTA / beats prior work"
external truth → `baseline-comparison-audit` + `citation-forensics` (emit
`needs_external_check`); citation existence/context → `citation-forensics`;
surface/AI-flavor → `presentation-signals`; **evaluation-design validity** (train/test
leakage, a conflicted/unvalidated LLM judge, declared-but-unreported conditions) →
`eval-design-forensics` (family H, L0/L1 stated-tells — distinct from this skill's L2
code/result-integrity); the rejection memo → `adversarial-case-builder`. (Note:
an LLM that produces the GROUND-TRUTH labels stays here as `HP-FAKE-GT`, L2 — only the
LLM-as-*judge* validity question hands off to `eval-design-forensics`.)

## When NOT to use this skill

- **As the verdict.** It proposes findings; `tools/adjudicate_findings.py` renders
  `CLEAN_GIVEN_EVIDENCE` / `SOFT_FLAGS` / `HARD_FLAGS`. Do not read this skill's
  output as a ruling.
- **At L0/L1 to assert fraud.** With no repo you get info-level "could-not-verify"
  signals, full stop — never a fraud claim from a PDF.
- **Without `claims.json`.** No ledger ⇒ nothing can be anchored ⇒ everything fails
  closed to `info`. Run `/evidence-ledger` first; this skill never invents structure
  from the raw PDF.
- **For text-only contradictions / scope-in-text** → `/consistency-audit`; for
  baseline integrity or "SOTA / first" → `/baseline-comparison-audit` (+
  `/citation-forensics`), handed off via `needs_external_check`.
- **For authorship / "is this AI-written".** Out of scope — surface "AI-flavor" lives
  in `/presentation-signals` (auxiliary, capped at minor); this repo is **not** an
  AI-text classifier.
- **On a timer.** Re-firing adds no signal — only a higher observability level does;
  schedule the *wait for artifacts*, then run once at the new level (see the cadence
  fence at the top).
