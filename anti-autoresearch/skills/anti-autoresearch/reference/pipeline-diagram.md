# Pipeline diagram

## Contents

- Stage diagram

## Stage diagram

```
[0] ingest          arxiv-id | pdf | dir  →  working dir (+ pdftotext text for L0)
        │
        ▼
[1] /evidence-ledger   tools/build_manifest.py + tools/build_claim_ledger.py
        │              → artifact_manifest.json (derives observability level L)
        │              → claims.json   (span-anchored, hashed; the ONLY structure auditors read)
        ▼
[2] fan out auditors (each reads the ledger, emits <skill>.findings.json):
        consistency-audit          (always · flagship · deterministic arithmetic + semantic)
        citation-forensics         (if ≥1 citation claim)
        baseline-comparison-audit  (if ≥1 comparison / SOTA scope claim)
        experiment-forensics       (always · L0/L1 = info "could-not-verify" · L2 = full code audit)
        presentation-signals       (always · AUXILIARY · capped at minor)
        ai-style-impressions       (always · AIS track · NOT integrity · zero verdict weight)
        proof-derivation-forensics (if ≥1 theorem/proof/derivation claim · verdict-bearing · dim=proof · L1 source, CAN reach HARD_FLAGS; L0 PDF-only → info)
        eval-design-forensics      (if ≥1 comparison/eval claim · family H · dim=evaluation · L0/L1 stated-tells: leakage / judge-validity / selective-reporting)
        │
        ▼
[3] advisory memos (each reads the ledger + merged findings · NO verdict weight):
        /adversarial-case-builder      → adversarial-case-builder.memo.md       (strongest evidence-bound objection)
        /novelty-duplication-advisory  → novelty-duplication-advisory.memo.md   (if ≥1 contribution claim · MEMO-ONLY · prior-work overlap · capped at info)
        │
        ▼
[4] tools/adjudicate_findings.py  --ledger REQUIRED  → report.json + REPORT.md
        │   gates (in order): ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE
        │   overall_verdict ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS, HARD_FLAGS}  (rules, no model)
        ▼
[5] present REPORT.md to the human (verdict + level first; state what could NOT be checked)
```
