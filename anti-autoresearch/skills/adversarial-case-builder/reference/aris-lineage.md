# Adversarial Case Builder — lineage from ARIS kill-argument

## How this differs from ARIS `kill-argument` (the parent)

| | ARIS `kill-argument` | `adversarial-case-builder` (forensics) |
|---|---|---|
| Reviewer may cite | any `file:line` / equation in the paper | ONLY existing `claim_id` / `finding_id` (evidence-bound) |
| Output | `KILL_ARGUMENT.{md,json}` with a 6-state PASS/WARN/FAIL **verdict** | `adversarial-case-builder.memo.md` — **no verdict** |
| Who decides | the skill maps per-point counts → verdict | the deterministic adjudicator, which caps this skill at `info` |
| Weak evidence | still writes the sharpest attack it can | returns an **honest null** (paper survives) |
| Position in flow | run once before submission | run **LAST** in the pipeline (needs ledger + upstream findings) |

The attack-then-defense, two-fresh-threads, ~200-word-commit structure is kept
*exactly*, because asking one model to "write the rejection memo" produces
qualitatively sharper feedback than "review and grade" — the former forces
commitment, the latter encourages hedging.
