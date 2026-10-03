# Evidence Ledger — rationale and role in the pipeline

## Why this exists

Five language-model auditors each independently parsing a PDF = five different
hallucinated tables and five different number lists, none reproducible — and the
obvious dismissal, *"an LLM grading another LLM's paper is just slop."* The
structural answer is **one deterministic pass** that turns the paper into:

- `artifact_manifest.json` — what was observable; this fixes the **observability
  level L**, the ceiling on every downstream finding's severity, and
- `claims.json` — a list of **span-anchored, hashed, checkable** claims
  (`schemas/claims.schema.json`).

Every downstream finding must cite a `claim_id` from this ledger and quote a verbatim
span of it. **No ledger claim → no finding** (the single most important integrity
rule of the repo, enforced again by `tools/adjudicate_findings.py`). That is what
makes the difference between "a model said so" and "here is the exact sentence, its
file, and its content hash" (`DESIGN.md` §2).

## Role in the pipeline (what this skill does and does NOT do)

| Stage | Skill / tool | Emits | Judges? |
|-------|--------------|-------|:-------:|
| **[1]–[2] ledger** | **evidence-ledger (this skill)** + `tools/build_manifest.py`, `tools/build_claim_ledger.py` | `artifact_manifest.json` + `claims.json` | **No.** States *what the paper says*. |
| [3] auditors | `consistency-audit`, `citation-forensics`, `baseline-comparison-audit`, `experiment-forensics` | `<skill>.findings.json` (read the ledger; quote its spans) | Propose findings — not the verdict. |
| [3] surface | `presentation-signals` | capped-at-`minor` surface findings (auxiliary) | Never a standalone verdict. |
| [3] memo | `adversarial-case-builder` | an evidence-bound memo | No verdict weight. |
| [4] **verdict** | `tools/adjudicate_findings.py` | `report.json` + `REPORT.md` | **Yes** — the ONLY verdict, by fixed rules, no model in the loop. |

This skill is stage [1]–[2] only. It states **what the paper says**, never **whether
it is right**. The `finding.schema.json` `skill` enum technically lists
`evidence-ledger` for completeness, but this skill never writes a finding object. If
you came here for a PASS/FAIL, you want `/anti-autoresearch` (the orchestrator), not
this skill.
