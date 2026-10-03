# Routing

## Contents

- How this differs from the other auditors (route correctly)
- When NOT to use this skill

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Level |
|---------|---------------------|------|
| **`citation-forensics`** (this) | **Do the cited papers exist, with correct metadata, and support the claim they are used for?** | **L0** |
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? | L0 |
| `baseline-comparison-audit` | Are the right baselines present, tuned, and is "SOTA" earned? | L0 stated / L2 verified |
| `experiment-forensics` | Are the reported numbers what the code actually computes? (fake GT, self-norm, phantom) | L2 |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary, capped at minor) | L0 |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

**Do NOT raise here** (hand off instead): numeric self-contradiction / method drift →
`consistency-audit`; "first / SOTA / beats prior work" as an *empirical* claim →
`baseline-comparison-audit` (emit `needs_external_check`); code/result-level fraud →
`experiment-forensics` (needs L2); surface / AI-flavor of the prose →
`presentation-signals`; the rejection memo → `adversarial-case-builder`. **Stay in
lane:** this skill judges only whether *the cited work* exists, is described
correctly, and supports the citing sentence — not whether the citing paper's own
claim is true.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **No citation claims in the ledger** (e.g. an L0 PDF-text-only run, where the
  extractor does not pull citations) → there is nothing to anchor to. Re-run
  `/evidence-ledger` with the LaTeX source so `citation` claims enter the ledger;
  otherwise emit `[]` and say why.
- **You need numeric self-contradiction or method drift** → `/consistency-audit`.
- **You need to verify an empirical "SOTA / first / beats prior work" claim** →
  `/baseline-comparison-audit` (+ hand off via `needs_external_check`); this skill
  judges only whether *the cited work* supports the sentence, not whether the citing
  paper's own result is true.
- **You need code/result-level fraud** (fake GT, self-normalization, phantom numbers)
  → `/experiment-forensics` at **L2**.
- **You want an AI-text / "looks machine-written" verdict** → out of scope. Surface
  hints live in `/presentation-signals` (auxiliary, capped at minor); this repo is
  **not** an AI-text classifier.
- **You want the `.bib`/`.tex` auto-fixed** → that is ARIS `citation-audit`
  (co-author mode). This skill is detect-only.
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the paper / ledger / bibliography changes (see the fence at the top).
