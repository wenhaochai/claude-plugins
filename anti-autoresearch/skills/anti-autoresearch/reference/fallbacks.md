# Fallbacks

## Contents

- Step 1 without /evidence-ledger
- Deterministic-only fallback (no model in the loop)

## Step 1 without /evidence-ledger

**Failure handling.** If `/evidence-ledger` is unavailable, build the ledger directly
with the real tools (exact flags — confirm via `--help`):
```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; PAPER_DIR="<from Step 0>"
SLUG=$(basename "$PAPER_DIR" | tr -cs 'A-Za-z0-9.' '-')
TXT=(); [ -f "$PAPER_DIR/paper.txt" ] && TXT=(--pdf-text "$PAPER_DIR/paper.txt")
python3 "$ROOT/tools/build_manifest.py" --paper-id "$SLUG" --dir "$PAPER_DIR" "${TXT[@]}" --out "$PAPER_DIR/artifact_manifest.json"
L=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["observability_level"])' "$PAPER_DIR/artifact_manifest.json")
TEX=(); while IFS= read -r f; do [ -n "$f" ] && TEX+=("$f"); done \
  < <(find "$PAPER_DIR" -type f -name '*.tex' -not -path '*/.aris/*' -not -path '*/build/*' -not -path '*/_build/*' -not -path '*/.git/*' | LC_ALL=C sort)   # nested tex/*.tex too
if [ ${#TEX[@]} -gt 0 ]; then
  python3 "$ROOT/tools/build_claim_ledger.py" --paper-id "$SLUG" --latex "${TEX[@]}" --observability-level "$L" --out "$PAPER_DIR/claims.json"
else
  python3 "$ROOT/tools/build_claim_ledger.py" --paper-id "$SLUG" --pdf-text "$PAPER_DIR/paper.txt" --observability-level "$L" --out "$PAPER_DIR/claims.json"
fi
```

## Deterministic-only fallback (no model in the loop)

When no cross-model reviewer is available (offline / no codex), you can still produce a
real, reproducible report from the deterministic core alone — the load-bearing,
eval-gated part of the repo (**100% recall on the three deterministic patterns
`HP-DELTA-ERROR` / `HP-NUM-INFLATE` / `HP-DUP-TABLE`, zero clean false-positives**;
`README.md` Status). All real tools, exact flags:

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; PAPER_DIR="<from Step 0>"
TXT=(); [ -f "$PAPER_DIR/paper.txt" ] && TXT=(--pdf-text "$PAPER_DIR/paper.txt")
python3 "$ROOT/tools/build_manifest.py"      --paper-id mypaper --dir "$PAPER_DIR" "${TXT[@]}" --out "$PAPER_DIR/artifact_manifest.json"
L=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["observability_level"])' "$PAPER_DIR/artifact_manifest.json")
TEX=(); while IFS= read -r f; do [ -n "$f" ] && TEX+=("$f"); done \
  < <(find "$PAPER_DIR" -type f -name '*.tex' -not -path '*/.aris/*' -not -path '*/build/*' -not -path '*/_build/*' -not -path '*/.git/*' | LC_ALL=C sort)   # nested tex/*.tex too
if [ ${#TEX[@]} -gt 0 ]; then                              # L1/L2 source path
  python3 "$ROOT/tools/build_claim_ledger.py"  --paper-id mypaper --latex "${TEX[@]}" \
      --observability-level "$L" --out "$PAPER_DIR/claims.json"
else                                                       # L0 text path (no *.tex)
  python3 "$ROOT/tools/build_claim_ledger.py"  --paper-id mypaper --pdf-text "$PAPER_DIR/paper.txt" \
      --observability-level "$L" --out "$PAPER_DIR/claims.json"
fi
python3 "$ROOT/tools/check_numeric_consistency.py" --ledger "$PAPER_DIR/claims.json" \
    --out "$PAPER_DIR/consistency-audit.deterministic.findings.json"
python3 "$ROOT/tools/check_presentation.py"        --ledger "$PAPER_DIR/claims.json" \
    --out "$PAPER_DIR/presentation-signals.deterministic.findings.json"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$PAPER_DIR"/*.deterministic.findings.json \
    --ledger "$PAPER_DIR/claims.json" --paper-id mypaper --observability-level "$L" \
    --taxonomy-version 0.5 \
    --limitation "Deterministic-only run (no cross-model reviewer): semantic + code-level dimensions were NOT run." \
    --out "$PAPER_DIR/report.json" --md "$PAPER_DIR/REPORT.md"
```

The verdict reflects only the deterministic patterns; the report's limitations must say
the semantic / code-level dimensions were not run. Run `python3 "$ROOT/eval/run_eval.py"`
any time to prove this core still catches the bundled injected defects and stays clean
on the clean fixture (the CI gate).
