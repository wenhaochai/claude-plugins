# Typical run profile

## Contents

- Typical run profile

## Typical run profile

Forensics is fast — the budget is reviewer calls, not GPU. Use this to set expectations
and to choose `— effort: max` (more fresh threads per dimension) vs the
deterministic-only fallback (zero reviewer calls).

| Stage | Reviewer calls | Reads | Writes | Notes |
|-------|----------------|-------|--------|-------|
| 0 ingest | 0 | `$ARGUMENTS` (dir/pdf/arxiv) | `paper.txt` / extracted `*.tex` | network only for arXiv |
| 1 ledger | 0–1 (enrich) | sources | `artifact_manifest.json`, `claims.json` | deterministic backbone + 1 optional additive pass |
| 2 auditors | 1+ per applicable dimension (serial; `— effort: max` → more) | `claims.json` (+ sources, +L2 code) | `<skill>.findings.json` (+ deterministic) | the bulk of the wall-clock; never parallel; `/proof-derivation-forensics` runs iff theorems/proofs are present |
| 3 memos | 1 (adversarial) + 2 per-axis fresh threads (novelty, optional) + DBLP/web retrieval | ledger + findings (+ external corpus) | `adversarial-case-builder.memo.md`, `novelty-duplication-advisory.memo.md` | non-blocking; no verdict weight; novelty is the only step that hits the network |
| 4 adjudicate | 0 | findings + ledger | `report.json`, `REPORT.md` | deterministic; the only verdict source |
| 5 present | 0 | `REPORT.md` | — | verdict + level first |

A heartbeat may **wait** on the only external steps (Stage 0 download, Stage 2 citation
web lookups, Stage 3 novelty prior-work retrieval) — it may **never** re-fire Stage 4 or
"decide the paper is fine."
