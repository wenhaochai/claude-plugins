# Presentation Signals — routing and when not to use

## How this differs from the other auditors (route correctly)


| Auditor | Question it answers | Level |
|---------|---------------------|------|
| **`presentation-signals`** (this) | **Surface tells a reviewer notices first (dup tables, pipeline artifacts, thin/LLM figures, padding) — AUXILIARY, capped at `minor`** | **L0** |
| `ai-style-impressions` | Pure AI writing-style impressions (AI-flavor, defensive hedging, broken narrative arc, jargon-stuffing, invented codenames) — zero verdict weight (AIS track) | L0 |
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? | L0 |
| `experiment-forensics` | Are the reported numbers what the code actually computes? (fake GT, self-norm, phantom) | L2 |
| `baseline-comparison-audit` | Are the right baselines present, tuned, and is "SOTA" earned? | L0 stated / L2 verified |
| `citation-forensics` | Do the cited papers exist and support the claim they are used for? | L0 |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo (no verdict weight) | any |

The pure AI writing-style impressions — AI-flavor, defensive hedging, broken narrative
arc, jargon-stuffing, and invented codenames — **moved out of this skill** in v0.5 to
the zero-verdict-weight **AIS track** owned by `skills/ai-style-impressions`; route any
AI-writing-style question there, not here.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **You want an AI-text / "looks machine-written" verdict** → out of scope by design.
  This skill is auxiliary and capped at `minor`; for authorship detection use a
  dedicated tool (Pangram / GPTZero / Binoculars).
- **You need numeric self-contradiction / method drift** → `/consistency-audit`.
- **You need citation existence / wrong-context** → `/citation-forensics`.
- **You need "SOTA / first" or baseline integrity** → `/baseline-comparison-audit`.
- **You need code/result-level fraud** (fake GT, self-normalization, phantom numbers)
  → `/experiment-forensics` at **L2**.
- **As the basis for a reject / accusation** → never. The strongest thing a surface
  signal can do is say "combine with the substantive findings and look closer."
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the paper or ledger changes (see the fence at the top).
