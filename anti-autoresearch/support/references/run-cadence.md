# Run cadence: once per input change, never on a timer

Do not wrap any Anti-Autoresearch skill in `/loop`, `/schedule` or `CronCreate`.

Every skill here is a function of its inputs: the paper, the evidence ledger, the
artifacts at the run's observability level, and (for a few) an external record such
as a bibliography or a leaderboard. Its output changes only when one of those inputs
changes, never with the wall clock. Re-firing on a timer adds no signal and spends
real cross-model, DBLP and web budget on every tick.

This holds for memo-only skills too (`adversarial-case-builder`,
`novelty-duplication-advisory`): the adjudicator caps them at `info`, so they add no
verdict weight, and a timer still buys nothing.

Schedule the external wait that precedes a run instead: ledger built, bibliography
finalized, or artifacts released (raising the level to L2). Then run the skill once.
Each skill's SKILL.md names the input change that justifies a re-run.

(Mirrors ARIS's external-cadence doctrine: `/loop` and `/schedule` are fire-control,
not a judge.)
