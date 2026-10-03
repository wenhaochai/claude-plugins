# Eval-Design Forensics — Step 5 validator

## Validator (run verbatim)

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"
OUT="$(dirname "$LEDGER")/eval-design-forensics.findings.json"
# args: LEDGER OUT then each saved raw reviewer response file from Steps 3–4:
python3 - "$LEDGER" "$OUT" "<resp_leakage.md>" "<resp_judge_reporting.md>" <<'PY'
import json, re, sys, os
ledger_path, out_path = sys.argv[1], sys.argv[2]
resp_paths = [p for p in sys.argv[3:] if p and os.path.isfile(p)]

def nw(s):                                   # mirror adjudicator _norm_ws (whitespace only)
    return " ".join((s or "").split())

OWNED = {"HP-EVAL-LEAKAGE", "HP-JUDGE-VALIDITY", "HP-SELECTIVE-REPORTING"}   # ALLOWED set
ABOVE = {"critical", "major", "minor"}
# OBS map — the canonical observability each owned pattern is decidable at (documentation;
# the REVIEWER sets observability_level_required per finding, and the adjudicator does the
# real req>run_level downgrade). stated-tell = 0; repo confirm = 2; the 3 leakage external
# subtypes carry no level (needs_external_check -> info).
OBS = {"HP-EVAL-LEAKAGE": "0 stated / 2 verified (proxy|sampling|contamination -> needs_external_check)",
       "HP-JUDGE-VALIDITY": "0/1 stated (2 may corroborate)",
       "HP-SELECTIVE-REPORTING": "0 stated / 2 verified"}

ledger = json.load(open(ledger_path, encoding="utf-8"))
base = {c["claim_id"]: nw(c.get("text_span", "")) for c in ledger.get("claims", [])
        if c.get("claim_id")}

proposed = []
for p in resp_paths:
    raw = open(p, encoding="utf-8").read()
    m = re.search(r"\[.*\]", raw, re.S)      # tolerate prose / code-fence wrapping
    try:
        chunk = json.loads(m.group(0) if m else raw)
        proposed += chunk.get("findings", []) if isinstance(chunk, dict) else chunk
    except Exception as e:
        print(f"WARN: could not parse {p}: {e}", file=sys.stderr)

kept, demoted, not_owned, ext = [], 0, 0, 0
for f in proposed:
    if not isinstance(f, dict):
        continue
    # OWNED gate: this skill emits ONLY family-H patterns — a missing/non-owned pattern_id is
    # DROPPED (not demoted), so nothing foreign can ride the `evaluation` dimension or survive
    # above-info on a malformed/absent id.
    if f.get("pattern_id") not in OWNED:
        not_owned += 1
        continue
    f["skill"] = "eval-design-forensics"
    # ANCHOR: keep only evidence whose span is a verbatim ws-normalized substring of its claim.
    # Guard malformed evidence (non-list / non-dict items can't anchor).
    anchored = [ev for ev in (f.get("evidence") if isinstance(f.get("evidence"), list) else [])
                if isinstance(ev, dict) and ev.get("claim_id") in base and nw(ev.get("span", "")) and
                nw(ev["span"]) in base[ev["claim_id"]]]               # span IN claim, never claim IN span
    f["evidence"] = anchored
    # ANCHOR gate: above-info needs >=1 anchored span
    if f.get("severity") in ABOVE and not anchored:
        f["severity"] = "info"; f.setdefault("_demotions", []).append("unanchored"); demoted += 1
    # OBS hygiene — MIRROR the adjudicator, fail-closed: an above-info finding whose
    # observability_level_required is missing/invalid demotes to info. NEVER default to 0
    # (that would let a forgotten level-2 code-confirm survive an L0 run). type() not
    # isinstance() so JSON booleans (True==1) are rejected, exactly as adjudicate_findings.py.
    olr = f.get("observability_level_required")
    if f.get("severity") in ABOVE and (type(olr) is not int or not (0 <= olr <= 3)):
        f["severity"] = "info"; f.setdefault("_demotions", []).append("undeclared-observability"); demoted += 1
    # FP-RISK hygiene — false_positive_risk is the REVIEWER's self-assessment (it drives the
    # adjudicator's cap); the executor never guesses it. Missing/invalid demotes to info.
    if f.get("severity") in ABOVE and f.get("false_positive_risk") not in ("low", "medium", "high"):
        f["severity"] = "info"; f.setdefault("_demotions", []).append("undeclared-fp-risk"); demoted += 1
    f.setdefault("reviewer", {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False})
    # honest hand-off: needs_external_check carries no severity weight (the 3 leakage external
    # subtypes land here) — pin it to info, never drop it. Mirrors the adjudicator's gate 6.
    if f.get("verdict_local") == "needs_external_check" or f.get("requires_external_check") is True:
        f["requires_external_check"] = True
        if f.get("severity") in ABOVE:
            f["severity"] = "info"; f.setdefault("_demotions", []).append("needs-external-check-no-weight"); ext += 1
    kept.append(f)

for k, f in enumerate(kept, 1):                                       # one namespace, sequential
    f["finding_id"] = f"ED{k:03d}"

json.dump(kept, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
above = sum(1 for x in kept if x.get("severity") in ABOVE)
seen = sorted({f.get("pattern_id") for f in kept if f.get("pattern_id") in OWNED})
print(f"validated {len(kept)} eval-design findings (above_info={above}; {demoted} demoted->info "
      f"(unanchored/undeclared); {not_owned} not-owned dropped; {ext} needs-external-check->info) -> {out_path}")
print("OBS map for patterns seen:", {p: OBS[p] for p in seen})
PY
```
