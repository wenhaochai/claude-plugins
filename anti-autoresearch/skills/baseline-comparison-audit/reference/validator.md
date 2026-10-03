# Baseline Comparison Audit — Step 5 validator

## Contents

- Step 5 validator script

## Step 5 validator script

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"
OUT="$(dirname "$LEDGER")/baseline-comparison-audit.findings.json"
# args: LEDGER OUT then each saved raw reviewer response file from Steps 3–4:
python3 - "$LEDGER" "$OUT" "<resp_completeness.md>" "<resp_fairness.md>" <<'PY'
import json, re, sys, os
ledger_path, out_path = sys.argv[1], sys.argv[2]
resp_paths = [p for p in sys.argv[3:] if p and os.path.isfile(p)]

def nw(s):                                   # mirror adjudicator _norm_ws (whitespace only)
    return " ".join((s or "").split())

OWNED = {"HP-MISSING-BASELINE", "HP-WEAK-BASELINE", "HP-SIG-OVERLAP", "HP-DELTA-ERROR",
         "HP-RESOURCE-IDENTITY-MISMATCH"}
ABOVE = {"critical", "major", "minor"}

ledger = json.load(open(ledger_path, encoding="utf-8"))
base = {c["claim_id"]: nw(c.get("text_span", "")) for c in ledger.get("claims", [])
        if c.get("claim_id")}

# best-effort dedup target: claim_ids the DETERMINISTIC consistency delta pass already
# flagged (consistency-audit.deterministic.findings.json, if it exists in this dir).
det_path = os.path.join(os.path.dirname(os.path.abspath(ledger_path)),
                        "consistency-audit.deterministic.findings.json")
det_delta = set()
if os.path.isfile(det_path):
    try:
        for f in json.load(open(det_path, encoding="utf-8")):
            if f.get("pattern_id") == "HP-DELTA-ERROR":
                for ev in f.get("evidence") or []:
                    if ev.get("claim_id"): det_delta.add(ev["claim_id"])
    except Exception:
        pass

proposed = []
for p in resp_paths:
    raw = open(p, encoding="utf-8").read()
    m = re.search(r"\[.*\]", raw, re.S)      # tolerate prose / code-fence wrapping
    try:
        chunk = json.loads(m.group(0) if m else raw)
        proposed += chunk.get("findings", []) if isinstance(chunk, dict) else chunk
    except Exception as e:
        print(f"WARN: could not parse {p}: {e}", file=sys.stderr)

kept, demoted, deduped, not_owned = [], 0, 0, 0
for f in proposed:
    if not isinstance(f, dict):
        continue
    f["skill"] = "baseline-comparison-audit"
    # ANCHOR: keep only evidence whose span is a verbatim ws-normalized substring of its claim
    anchored = [ev for ev in (f.get("evidence") or [])
                if ev.get("claim_id") in base and nw(ev.get("span", "")) and
                nw(ev["span"]) in base[ev["claim_id"]]]                 # span IN claim, not claim IN span
    f["evidence"] = anchored
    # owned-pattern gate: a non-owned pattern cannot rise above info here
    if f.get("pattern_id") and f["pattern_id"] not in OWNED and f.get("severity") in ABOVE:
        f["severity"] = "info"; f.setdefault("_demotions", []).append("pattern-not-owned"); not_owned += 1
    # best-effort delta dedup vs the deterministic single-sentence pass
    if f.get("pattern_id") == "HP-DELTA-ERROR" and f.get("severity") in ABOVE \
       and any(ev.get("claim_id") in det_delta for ev in anchored):
        f["severity"] = "info"; f.setdefault("_demotions", []).append("dup-of-deterministic-delta"); deduped += 1
    # ANCHOR gate: above-info needs >=1 anchored span
    if f.get("severity") in ABOVE and not anchored:
        f["severity"] = "info"; f.setdefault("_demotions", []).append("unanchored"); demoted += 1
    # OBSERVABILITY hygiene — MIRROR the adjudicator, fail-closed: an above-info finding whose
    # observability_level_required is missing/invalid demotes to info. NEVER silently default to 0
    # (that would let a forgotten level-2 config-only asymmetry survive an L0 run). type() not
    # isinstance() so JSON booleans (True==1) are rejected, exactly as adjudicate_findings.py does.
    olr = f.get("observability_level_required")
    if f.get("severity") in ABOVE and (type(olr) is not int or not (0 <= olr <= 3)):
        f["severity"] = "info"; f.setdefault("_demotions", []).append("undeclared-observability"); demoted += 1
    # FP-RISK hygiene — false_positive_risk is the REVIEWER's self-assessment (it drives the
    # adjudicator's cap); the executor never guesses it. Missing/invalid demotes to info, never a default.
    if f.get("severity") in ABOVE and f.get("false_positive_risk") not in ("low", "medium", "high"):
        f["severity"] = "info"; f.setdefault("_demotions", []).append("undeclared-fp-risk"); demoted += 1
    f.setdefault("reviewer", {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False})
    # honest hand-off: needs_external_check carries no severity weight (adjudicate_findings.py has
    # no such gate, so the validator makes the claim true) — pin it to info, never drop it.
    if f.get("verdict_local") == "needs_external_check":
        f["requires_external_check"] = True
        if f.get("severity") in ABOVE:
            f["severity"] = "info"; f.setdefault("_demotions", []).append("needs-external-check-no-weight")
    kept.append(f)

for k, f in enumerate(kept, 1):                                        # one namespace, sequential
    f["finding_id"] = f"BC{k:03d}"

json.dump(kept, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
above = sum(1 for x in kept if x.get("severity") in ABOVE)
print(f"validated {len(kept)} baseline findings (above_info={above}; {demoted} demoted->info "
      f"(unanchored/undeclared); {not_owned} not-owned->info; {deduped} delta deduped) -> {out_path}")
PY
```
