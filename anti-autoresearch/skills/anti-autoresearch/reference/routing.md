# Routing to standalone skills

## Contents

- When NOT to use (and routing to standalone skills)

## When NOT to use (and routing to standalone skills)

- **You only want one dimension** → call the auditor directly (`/consistency-audit`,
  `/citation-forensics`, `/baseline-comparison-audit`, `/experiment-forensics`,
  `/presentation-signals`, `/proof-derivation-forensics`); each can adjudicate itself with
  `--ledger` when run alone.
- **You only want the prior-work overlap** (trivial-combination / duplicate-publication
  signals) → `/novelty-duplication-advisory` (memo-only; it surfaces overlap but never rules
  novelty, and the absence of a match is not evidence of originality).
- **You only need the ledger** (extract claims, no verdict) → `/evidence-ledger`.
- **You want an AI-text / "looks machine-written" verdict** → out of scope by design;
  this tool audits *integrity under limited evidence*, not authorship (`DESIGN.md` §1).
- **You want the paper auto-fixed** → out of scope; this is a third-party forensics tool,
  not a co-author. (ARIS `citation-audit` etc. are the co-author-mode tools.)
- **You want reproduction (re-run the code, L3)** → out of scope in v0; we never claim
  reproduction. L2 verifies paper-number ↔ result-file match, not a re-run.
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` the verdict; re-run only
  when the paper / repo / ledger changes (see the cadence fence at the top).
