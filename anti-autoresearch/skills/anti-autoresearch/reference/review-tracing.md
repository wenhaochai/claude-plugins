# Review tracing

## Contents

- Review tracing

## Review tracing

Each auditor saves its own raw reviewer calls under `.aris/traces/<skill>/<date>_run<NN>/`
(forensic policy — never silently dropped: `run.meta.json` + per-call `request.json` /
`response.md` / `meta.json`, where `request.json` shows the executor sent only paths + the
ledger + the checklist — the reviewer-independence audit trail). The orchestrator
additionally writes a top-level run trace so the whole sweep is reproducible:

```bash
PAPER_DIR="<from Step 0>"; ARG="<original input arg, from Step 0>"; DATE=$(date +%Y-%m-%d); N=1
while [ -d "$PAPER_DIR/.aris/traces/anti-autoresearch/${DATE}_run$(printf %02d $N)" ]; do N=$((N+1)); done
RUNDIR="$PAPER_DIR/.aris/traces/anti-autoresearch/${DATE}_run$(printf %02d $N)"; mkdir -p "$RUNDIR"
python3 - "$PAPER_DIR" "$RUNDIR" "$ARG" <<'PY'
import json, glob, os, sys, hashlib, datetime
D, RUN, ARG = sys.argv[1], sys.argv[2], sys.argv[3]
def sha(p):
    try: return hashlib.sha256(open(p, "rb").read()).hexdigest()
    except Exception: return None
rep = json.load(open(f"{D}/report.json", encoding="utf-8")) if os.path.exists(f"{D}/report.json") else {}
meta = {
    "skill": "anti-autoresearch", "input_arg": ARG, "paper_dir": D,
    "paper_id": rep.get("paper_id"), "observability_level": rep.get("observability_level"),
    "ledger_sha256": sha(f"{D}/claims.json"),
    "findings_files": [os.path.basename(p) for p in sorted(glob.glob(f"{D}/*.findings.json"))
                       if not p.endswith(".proposed.findings.json")],
    "overall_verdict": rep.get("overall_verdict"), "counts": rep.get("counts"),
    "adjudicator": rep.get("adjudicator"), "taxonomy_version": rep.get("taxonomy_version"),
    "generated_at": datetime.datetime.utcnow().isoformat() + "Z",
}
json.dump(meta, open(f"{RUN}/run.meta.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("wrote", f"{RUN}/run.meta.json", "->", meta["overall_verdict"])
PY
```

Traces are the reproducibility + independence audit trail: they prove the executor sent
the reviewer only structured inputs and that the verdict came from the deterministic
adjudicator, not a model.
