# Baseline Comparison Audit — routing to other auditors

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Level |
|---------|---------------------|------|
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? (owns text-only `HP-SCOPE-INFLATE` + single-sentence `HP-DELTA-ERROR`) | L0 |
| `experiment-forensics` | Are the reported numbers what the code actually computes? (fake GT, self-norm, phantom) | L2 |
| **`baseline-comparison-audit`** (this) | **Are the right baselines present (completeness), fairly tuned/configured (fairness), and is "outperforms/SOTA" statistically earned (significance)?** | **L0 stated / L2 verified** |
| `citation-forensics` | Do the cited baseline papers exist and support the claim? | L0 |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary, capped at minor) | L0 |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

**Do NOT raise here** (hand off instead): generic in-text scope inflation
("comprehensive / extensive / robust" decoupled from a SOTA/comparison claim) →
`consistency-audit` owns `HP-SCOPE-INFLATE`; a single-sentence "from A to B, X%"
delta whose operands and stated value sit in **one** sentence → already caught
deterministically by `consistency-audit` (do **not** re-emit — Step 5 dedups);
whether a baseline *number* matches the repo/code → `experiment-forensics` (L2);
whether a *cited* baseline paper exists / is used in-context → `citation-forensics`;
surface / AI-flavor → `presentation-signals`. This skill **never** emits an
F-pattern.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **The paper makes no comparison / SOTA / baseline claim** (`APPLICABLE = no` in
  Step 1) → write `[]` and stop; there is nothing to audit.
- **Generic in-text scope inflation with no comparison** ("a *comprehensive* study")
  → `/consistency-audit` (`HP-SCOPE-INFLATE`).
- **A single-sentence "from A to B, X%" delta** → already caught deterministically by
  `/consistency-audit`; do not re-emit.
- **Whether a baseline NUMBER matches the repo / code** (fake GT, self-norm, phantom)
  → `/experiment-forensics` at **L2**.
- **Whether a *cited* baseline paper EXISTS / is used in-context** →
  `/citation-forensics`.
- **An AI-text / "looks machine-written" verdict** → out of scope; surface hints live
  in `/presentation-signals` (auxiliary, capped at minor). This repo is **not** an
  AI-text classifier.
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the paper, ledger, or live leaderboard changes (see the fence at the top).
