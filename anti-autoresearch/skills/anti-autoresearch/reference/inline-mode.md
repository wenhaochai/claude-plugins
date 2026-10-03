# Inline mode: shared anchor gate

**Inline mode only — the shared anchor gate.** When delegation is unavailable, run each
applicable dimension's codex call yourself (envelope + verbatim sub-skill prompt above;
save the raw reply to `$PAPER_DIR/.aris/<dim>.response.md`), then convert that raw reply
into a validated `<dim>.findings.json` with this gate. It enforces invariant #3 exactly
as `tools/adjudicate_findings.py` re-binds it (`span in claim`, never `claim in span`).
`SURFACE=1` only for presentation-signals:

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; PAPER_DIR="<from Step 0>"
LEDGER="$PAPER_DIR/claims.json"; SKILL="<dimension>"; SURFACE="<0 or 1>"
mkdir -p "$PAPER_DIR/.aris"   # the fresh-thread raw reply is saved here before this gate runs
RAW="$PAPER_DIR/.aris/$SKILL.response.md"; OUT="$PAPER_DIR/$SKILL.findings.json"
python3 - "$LEDGER" "$RAW" "$OUT" "$SKILL" "$SURFACE" <<'PY'
import json, re, sys
ledger_p, raw_p, out_p, skill, surface = sys.argv[1:6]
surface = surface == "1"
nw = lambda s: " ".join((s or "").split())
SEV={"critical","major","minor","info"}; VL={"fail","warn","clean","needs_external_check"}
FPR={"low","medium","high"}; ABOVE={"critical","major","minor"}
claims = {c["claim_id"]: c for c in json.load(open(ledger_p, encoding="utf-8")).get("claims", []) if c.get("claim_id")}
raw = open(raw_p, encoding="utf-8").read(); m = re.search(r"\[.*\]", raw, re.S)
prop = json.loads(m.group(0) if m else raw)
if isinstance(prop, dict): prop = prop.get("findings", [])
kept = []; n = 0; demoted = 0; capped = 0
for f in prop:
    if not isinstance(f, dict): continue
    n += 1; f["finding_id"] = f"F{n:03d}"; f["skill"] = skill
    if f.get("severity") not in SEV: f["severity"] = "info"
    if f.get("verdict_local") not in VL: f["verdict_local"] = "warn"
    if f.get("false_positive_risk") not in FPR: f["false_positive_risk"] = "high" if surface else "medium"
    if f["verdict_local"] == "needs_external_check": f["requires_external_check"] = True
    if surface:                                   # surface signals: forced high-FP, capped at minor, L0-decidable
        f["false_positive_risk"] = "high"; f["observability_level_required"] = 0
        if f["severity"] in ("critical", "major"): f["severity"] = "minor"; capped += 1
    anchored = []
    for ev in (f.get("evidence") or []):
        cid = ev.get("claim_id"); span = nw(ev.get("span", "")); c = claims.get(cid)
        if c and span and span in nw(c.get("text_span", "")):   # span IN claim, NOT claim IN span
            ev.setdefault("location", c.get("location", {}))
            ev.setdefault("artifact_hash", c.get("evidence_anchor", ""))
            anchored.append(ev)
    f["evidence"] = anchored
    if f["severity"] in ABOVE and not anchored: f["severity"] = "info"; demoted += 1
    # observability_level_required is passed through verbatim — a missing/invalid one is
    # left as-is so the adjudicator's OBSERVABILITY gate fail-closes it to info.
    f["reviewer"] = {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False}
    kept.append(f)
json.dump(kept, open(out_p, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"{skill}: validated {len(kept)} ({demoted} ->info unanchored, {capped} surface-capped) -> {out_p}")
PY
```

For dimension-specific extras (citation must anchor to a `type:"citation"` claim;
baseline pattern-ownership + cross-row delta dedup; presentation surface allow-list),
prefer the sub-skill's own `Validate + anchor` step — it is a strict superset of this
gate. The deterministic passes have **no** LLM step — run their tools directly:
```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; PAPER_DIR="<from Step 0>"
python3 "$ROOT/tools/check_numeric_consistency.py" --ledger "$PAPER_DIR/claims.json" \
    --out "$PAPER_DIR/consistency-audit.deterministic.findings.json"
python3 "$ROOT/tools/check_presentation.py" --ledger "$PAPER_DIR/claims.json" \
    --out "$PAPER_DIR/presentation-signals.deterministic.findings.json"
```
