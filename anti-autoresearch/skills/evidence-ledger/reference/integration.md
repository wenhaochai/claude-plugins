# Evidence Ledger — what consumes the ledger downstream

## What consumes the ledger downstream (integration)

You normally reach these via `/anti-autoresearch`; the exact contracts are:

```bash
# consistency-audit's deterministic arithmetic layer (HP-DELTA-ERROR, HP-NUM-INFLATE):
python3 "$ROOT/tools/check_numeric_consistency.py" --ledger "$PAPER_DIR/claims.json" \
    --out consistency-audit.deterministic.findings.json

# presentation-signals' surface checks (HP-DUP-TABLE via table_cell claims, etc.) —
# AUXILIARY, capped at minor by the adjudicator, default false_positive_risk:high,
# NOT an AI-text classifier, never a standalone verdict:
python3 "$ROOT/tools/check_presentation.py" --ledger "$PAPER_DIR/claims.json" \
    --out presentation-signals.deterministic.findings.json

# the deterministic adjudicator — --ledger is REQUIRED:
python3 "$ROOT/tools/adjudicate_findings.py" --findings *.findings.json \
    --ledger "$PAPER_DIR/claims.json" --paper-id "$PAPER_ID" \
    --observability-level "$L" --taxonomy-version 0.5 --out report.json --md REPORT.md
```

`adjudicate_findings.py` **requires** `--ledger`: it re-verifies that each
above-`info` finding quotes a verbatim ledger span; without it every such finding
**fails closed to `info`** — a missing or wrong ledger silently neuters the whole
audit. The ledger you build here is load-bearing for every verdict. **This skill does
not run any of these** — stop at a validated ledger.
