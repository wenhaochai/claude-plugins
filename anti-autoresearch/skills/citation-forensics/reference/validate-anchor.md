# Validate + anchor script (Step 4)

## Contents

- Validator script

## Validator script

```bash
LEDGER="<abs LEDGER>"; TRACE_DIR="<abs TRACE_DIR>"
OUT="<abs PAPER_DIR>/citation-forensics.findings.json"
python3 - "$LEDGER" "$TRACE_DIR" "$OUT" <<'PY'
import json, re, sys, glob, os
ledger_path, trace_dir, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

def nw(s):                                    # mirror adjudicator _norm_ws (whitespace only)
    return " ".join((s or "").split())

ALLOWED    = {"HP-CITE-HALLUC", "HP-CITE-CONTEXT", "HP-CITE-RETRACTED"}   # the ONLY patterns this skill emits
OBS        = {"HP-CITE-HALLUC": 0, "HP-CITE-CONTEXT": 0, "HP-CITE-RETRACTED": 0}   # all decidable at L0 (taxonomy 0.5 §E)
SEV        = {"critical", "major", "minor", "info"}
VL         = {"fail", "warn", "clean", "needs_external_check"}
FPR        = {"low", "medium", "high"}
ABOVE_INFO = {"critical", "major", "minor"}

L = json.load(open(ledger_path, encoding="utf-8"))
claims = {c["claim_id"]: c for c in L.get("claims", []) if c.get("claim_id")}

kept, dropped, demoted, n = [], 0, 0, 0
files = sorted(glob.glob(os.path.join(trace_dir, "*.response.md")))
for fp in files:
    raw = open(fp, encoding="utf-8", errors="replace").read()
    m = re.search(r"\[.*\]", raw, re.S)       # tolerate prose / code-fence wrapping
    if not m:
        print(f"  note: no JSON array in {os.path.basename(fp)} (treated as [])"); continue
    try:
        arr = json.loads(m.group(0))
    except Exception as e:
        print(f"  WARN: unparseable JSON in {os.path.basename(fp)}: {e} (treated as [])"); continue
    if isinstance(arr, dict):                  # tolerate {"findings": [...]}
        arr = arr.get("findings", [])
    for f in arr:
        if not isinstance(f, dict):
            dropped += 1; continue
        pid = f.get("pattern_id")
        if pid not in ALLOWED:                 # stray HP-* / surface signal -> not this skill's to emit
            dropped += 1; continue
        n += 1
        f["finding_id"] = f"F{n:03d}"          # FORCE renumber — per-key arrays each start at F001
        f["skill"] = "citation-forensics"      # force-correct the skill tag
        # enum hygiene: any illegal value -> safe default
        if f.get("severity") not in SEV: f["severity"] = "info"
        if f.get("verdict_local") not in VL: f["verdict_local"] = "warn"
        if f.get("false_positive_risk") not in FPR: f["false_positive_risk"] = "high"
        if f["verdict_local"] == "needs_external_check":
            f["requires_external_check"] = True
        # ANCHOR gate: span is a verbatim ws-normalized SUBSTRING of its cited claim,
        # AND that claim must be a type:"citation" (citing-sentence) claim.
        anchored, has_cite_anchor = [], False
        for ev in (f.get("evidence") or []):
            cid, span = ev.get("claim_id"), nw(ev.get("span", ""))
            c = claims.get(cid)
            if c and span and span in nw(c.get("text_span", "")):   # span IN claim, not claim IN span
                ev.setdefault("location", c.get("location", {}))     # enrich for human navigation
                ev.setdefault("artifact_hash", c.get("evidence_anchor", ""))
                anchored.append(ev)
                if c.get("type") == "citation":
                    has_cite_anchor = True
        f["evidence"] = anchored
        if f["severity"] in ABOVE_INFO and not (anchored and has_cite_anchor):
            f["severity"] = "info"; demoted += 1   # unanchored / non-citation anchor -> info
        # observability fallback: a real int 0-3 (JSON bool is an int subclass -> reject)
        olr = f.get("observability_level_required")
        if isinstance(olr, bool) or not isinstance(olr, int) or not (0 <= olr <= 3):
            f["observability_level_required"] = OBS.get(pid, 0)
        # cross-model provenance (reviewer-independence: a proposal, not a verdict)
        f["reviewer"] = {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False}
        kept.append(f)

json.dump(kept, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"validated {len(kept)} citation findings from {len(files)} entry response(s) "
      f"({demoted} demoted to info for unanchored/non-citation span, "
      f"{dropped} dropped: non-citation-pattern/malformed) -> {out_path}")
PY
```
