# Validate + anchor script (Step 3)

## Contents

- Validator script

## Validator script

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"
PROPOSED="<abs path to the saved raw reviewer response from Step 2>"
OUT="$(dirname "$LEDGER")/proof-derivation-forensics.findings.json"
python3 - "$LEDGER" "$PROPOSED" "$OUT" <<'PY'
import json, re, sys
ledger_path, proposed_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

def nw(s):                                    # mirror adjudicator _norm_ws (whitespace only)
    return " ".join((s or "").split())

GFAMILY = {"HP-PROOF-OBLIGATION-GAP", "HP-PROOF-CIRCULARITY", "HP-DERIVATION-INVALID",
           "HP-SYMBOL-SEMANTIC-DRIFT", "HP-ASSUMPTION-SMUGGLE", "HP-UNDEFINED-NOTATION"}
# fallback observability tier per pattern (taxonomy 0.5 lowest-decidable level) — used
# ONLY when the reviewer omitted/garbled the field. ALL family-G patterns default to L1:
# a verdict-bearing proof/derivation flaw is decided from the LaTeX SOURCE, because
# PDF-extracted math is unreliable (mangled symbols, subscripts, equation structure) — an
# L0 (PDF-only) "this step is invalid" risks flagging an extraction artifact. An unknown/
# missing pattern fails closed to L2 (auto-demotes at L0/L1).
OBS = {"HP-PROOF-OBLIGATION-GAP": 1, "HP-PROOF-CIRCULARITY": 1, "HP-DERIVATION-INVALID": 1,
       "HP-SYMBOL-SEMANTIC-DRIFT": 1, "HP-ASSUMPTION-SMUGGLE": 1, "HP-UNDEFINED-NOTATION": 1}
SEV = {"critical", "major", "minor", "info"}
VL  = {"fail", "warn", "clean", "needs_external_check"}
FPR = {"low", "medium", "high"}
ABOVE_INFO = {"critical", "major", "minor"}

ledger = json.load(open(ledger_path, encoding="utf-8"))
claims = {c["claim_id"]: c for c in ledger.get("claims", []) if c.get("claim_id")}

raw = open(proposed_path, encoding="utf-8").read()
m = re.search(r"\[.*\]", raw, re.S)           # tolerate prose / code-fence wrapping
proposed = json.loads(m.group(0) if m else raw)
if isinstance(proposed, dict):                # tolerate {"findings": [...]}
    proposed = proposed.get("findings", [])

kept, dropped_nonG, demoted = [], 0, 0
n = 0
for f in proposed:
    if not isinstance(f, dict):
        dropped_nonG += 1; continue
    pid = f.get("pattern_id")
    # SCOPE: this skill emits ONLY family-G. A set pattern_id outside G is routed
    # elsewhere (consistency/citation/experiment/presentation) -> drop, logged. A
    # missing pattern_id is kept (forensic record) but fail-closes its observability.
    if pid is not None and pid not in GFAMILY:
        dropped_nonG += 1; continue
    n += 1
    f["finding_id"] = f"F{n:03d}"
    f["skill"] = "proof-derivation-forensics"
    # enum hygiene: any illegal value -> safe default
    if f.get("severity") not in SEV: f["severity"] = "info"
    if f.get("verdict_local") not in VL: f["verdict_local"] = "warn"
    if f.get("false_positive_risk") not in FPR: f["false_positive_risk"] = "high"
    if f["verdict_local"] == "needs_external_check":
        f["requires_external_check"] = True
    # ANCHOR gate: span must be a verbatim, ws-normalized SUBSTRING of its cited claim
    anchored = []
    for ev in (f.get("evidence") or []):
        if not isinstance(ev, dict):              # tolerate a stray string/None evidence item
            continue
        cid, span = ev.get("claim_id"), nw(ev.get("span", ""))
        c = claims.get(cid)
        if c and span and span in nw(c.get("text_span", "")):   # span IN claim, not claim IN span
            ev.setdefault("location", c.get("location", {}))     # enrich for human navigation
            ev.setdefault("artifact_hash", c.get("evidence_anchor", ""))
            anchored.append(ev)
    f["evidence"] = anchored
    if f["severity"] in ABOVE_INFO and not anchored:
        f["severity"] = "info"; demoted += 1                     # unanchored -> info (adjudicator would too)
    # a family-G finding above info MUST name one of the 6 G patterns; non-G ids were
    # already dropped, so a MISSING pattern_id here cannot carry weight -> info.
    if pid not in GFAMILY and f["severity"] in ABOVE_INFO:
        f["severity"] = "info"; demoted += 1
    # observability:
    olr = f.get("observability_level_required")
    olr_explicit = (not isinstance(olr, bool)) and isinstance(olr, int) and (0 <= olr <= 3)
    if not olr_explicit:
        # missing/garbled -> a written-proof flaw is decided from the LaTeX source (L1);
        # unknown pattern fail-closes to L2.
        olr = 1 if pid in GFAMILY else 2
    elif pid in GFAMILY and olr > 1 and f["severity"] in ABOVE_INFO:
        # reviewer EXPLICITLY marked an owned G finding as needing code/results (>=L2).
        # family-G validity is decided from the WRITTEN proof, so >=L2 means this finding is
        # mis-routed / over-claimed -> demote to info (do NOT silently clamp it down to L1).
        f["severity"] = "info"; demoted += 1
    # family-G floor: a verdict-bearing proof/derivation finding needs the LaTeX source (L1) —
    # PDF-extracted math is unreliable, so an L0 G finding must not raise the verdict. Clamp UP
    # to L1 (conservative: RAISES the observability bar -> auto-demotes at an L0 run; unlike the
    # >L2 case above, clamping up never launders an over-claim into a pass).
    if pid in GFAMILY and isinstance(olr, int) and olr < 1:
        olr = 1
    f["observability_level_required"] = olr
    # cross-model provenance (reviewer-independence: this is a proposal, not a verdict)
    f["reviewer"] = {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False}
    kept.append(f)

json.dump(kept, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"validated {len(kept)} family-G findings "
      f"({demoted} demoted to info for unanchored span, "
      f"{dropped_nonG} dropped: non-G pattern routed elsewhere / malformed) -> {out_path}")
PY
```
