# Novelty & Duplication Advisory — routing and when not to use

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | External lookup? | Verdict weight |
|---------|---------------------|:---:|:---:|
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? | no | yes (via adjudicator) |
| `experiment-forensics` | Are reported numbers what the code computes? (fake GT, self-norm, phantom) | no | yes (L2) |
| `baseline-comparison-audit` | Right baselines present, tuned, "SOTA" earned? | profile only | yes |
| `citation-forensics` | Do the *cited* papers EXIST and support the claim they are used for? | yes (existence/context of *cited* works) | yes |
| `proof-derivation-forensics` | Does the written proof / derivation hold? | no | yes |
| `presentation-signals` | Surface "AI-flavor" hints (auxiliary) | no | capped at minor |
| `adversarial-case-builder` | Strongest *anchored* rejection memo + defense | no | none (memo-only) |
| **`novelty-duplication-advisory`** (this) | **What prior-work OVERLAP should a reviewer weigh for trivial-combination / duplicate?** | **YES — retrieves *uncited* prior work** | **none (memo-only, capped at info)** |

**Route, do not overreach.** `citation-forensics` checks the works the paper *already cites*;
this skill goes looking for prior work the paper *omits or overlaps*. A **wrong-context or
fabricated citation** belongs to `citation-forensics`. A **"SOTA / first / beats prior work"**
claim that needs a baseline comparison belongs to `baseline-comparison-audit` (this skill can
emit `needs_external_check` and hand it off). An **internal** scope-overclaim ("comprehensive"
on thin scope) belongs to `consistency-audit` (`HP-SCOPE-INFLATE`). This skill owns *only* the
two advisory overlap signals — and even those it only *surfaces*.

## How this differs from ARIS `novelty-check` (the parent)

| | ARIS `novelty-check` | `novelty-duplication-advisory` (forensics) |
|---|---|---|
| Frame | "is MY idea novel — PROCEED / ABANDON?" | "here is the overlap a REVIEWER should weigh" |
| Subject | the author's own prospective idea | a third party's submitted paper |
| Paper side | a free-text method description | **ledger claims** (`claim_id` + verbatim span) |
| Output | a `Score: X/10` + recommendation + "suggested positioning" | a side-by-side overlap memo — **no score, no recommendation** |
| Verdict | "Novelty: HIGH/MEDIUM/LOW" | **none** — never rules trivial/duplicate; capped at `info` |
| Empty retrieval | "looks novel, proceed" | "no candidate overlap found — this says **nothing** about novelty" |
| Prior-work anchoring | `verify_papers.py` (anti-hallucination) | every candidate a resolved record in `candidates.json`; unresolved → dropped |

The multi-source retrieval and the cross-model verification are kept *exactly* (they are the
load-bearing parts). What changes is the refusal to grade: a forensics tool that scored
novelty from an incomplete corpus would be precisely the over-claim this repo refuses.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents structure
  from the raw PDF, and it needs the contribution spans to build its query (the title is read
  from the source only as a search seed).
- **You want a novelty SCORE / a PROCEED-vs-ABANDON recommendation** → that is the
  *author-facing* ARIS `/novelty-check`, not this forensics advisory. This skill never scores or
  recommends; it only surfaces overlap for a human to weigh.
- **You want a "this paper is trivial / a duplicate" verdict** → impossible by design; novelty
  is a reviewer judgment and this skill is capped at `info`. Read the memo and decide yourself.
- **You need to verify a *cited* reference exists / is used in the right context** →
  `/citation-forensics` (this skill is about overlap with work the paper need not cite).
- **You need to verify an empirical "first / SOTA / beats prior work" claim** →
  `/baseline-comparison-audit` (a baseline-integrity verdict, not an overlap memo).
- **You need intra-paper contradiction or method drift** → `/consistency-audit`
  (`HP-SCOPE-INFLATE` for an internal scope-overclaim).
- **You need code/result-level fraud** (fake GT, self-normalization, phantom numbers) →
  `/experiment-forensics` at **L2**.
- **You want an AI-text / "looks machine-written" verdict** → out of scope. Surface hints live
  in `/presentation-signals` (auxiliary, capped at minor); this repo is **not** an AI-text
  classifier and **not** a plagiarism detector — it surfaces candidates to weigh.
- **No corpus access** → the retrieval cannot run; the honest output is `retrieval_incomplete`
  (concludes nothing), not a guessed "no duplication".
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only when the
  paper / ledger / literature change (see the fence at the top). Re-running burns external-search
  budget for an identical memo.
