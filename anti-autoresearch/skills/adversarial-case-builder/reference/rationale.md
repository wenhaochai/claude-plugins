# Adversarial Case Builder — rationale

## Why this exists

The standard auditors (`consistency-audit`, `citation-forensics`, …) fan out and
each flags discrepancies in *its own dimension*. They produce a **balanced** list —
each discrepancy at its own severity, none committing to "this is the one that sinks
the paper." That misses a specific failure mode: the **single most damaging
paragraph** a senior area chair would write in a rejection. A balanced reviewer lists
"scope-overclaim" as one `major` among several and never commits; an adversarial
reviewer **must** commit — their whole job is to convince the AC to reject in ~200
words.

This skill runs that adversarial pass deliberately, then forces a second fresh
reviewer to decompose the attack and rule each point against the evidence. The
forensics twist over ARIS `kill-argument`: the attack is **fenced to anchored
evidence**. A reviewer who can cite anything tends to manufacture a confident kill
out of nothing — the exact dynamic that makes "AI reviews AI" feel like noise. By
forcing every accusation to cite an existing ledger `claim_id` or `finding_id`, the
memo can only be as strong as the evidence the deterministic layers already graded.
If that evidence is weak, the correct output is an **honest null**: the paper
survives. Manufacturing a kill from thin evidence is a failure, not a success.
