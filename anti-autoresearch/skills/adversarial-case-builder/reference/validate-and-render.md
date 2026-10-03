# Adversarial Case Builder — Step 3 validate-and-render command

## Contents

- Validate + render command (run verbatim)

## Validate + render command (run verbatim)

```bash
LEDGER="<abs path to claims.json from Step 0>"
ATTACK="<abs path to $TRACE/001-attack.response.md>"
DEFENSE="<abs path to $TRACE/002-defense.response.md>"
python3 - "$LEDGER" "$ATTACK" "$DEFENSE" "<ATTACK_THREAD_ID>" "<DEFENSE_THREAD_ID>" <<'PY'
import json, re, sys, os, glob
ledger_path, attack_path, defense_path = sys.argv[1], sys.argv[2], sys.argv[3]
attack_tid = sys.argv[4] if len(sys.argv) > 4 else ""
defense_tid = sys.argv[5] if len(sys.argv) > 5 else ""

def nw(s): return " ".join((s or "").split())

# ---- evidence universe: ledger claims + sibling findings (never our own output) ----
led = json.load(open(ledger_path, encoding="utf-8"))
D = os.path.dirname(os.path.abspath(ledger_path)) or "."
L = int(led.get("observability_level", 0))
PID = led.get("paper_id", "?")
claims = {c["claim_id"]: c for c in led.get("claims", []) if c.get("claim_id")}

findings, n_findings, bad_findings = {}, 0, []
for fp in sorted(glob.glob(os.path.join(D, "*.findings.json"))):
    if os.path.basename(fp).startswith("adversarial-case-builder"):
        continue                                   # never let the memo cite itself
    try:
        arr = json.load(open(fp, encoding="utf-8"))
    except Exception as e:                          # forensic: never SILENTLY drop input
        print("WARN: unreadable findings file skipped: %s (%s) — evidence universe "
              "reduced; fix it and re-run" % (os.path.basename(fp), e), file=sys.stderr)
        bad_findings.append(os.path.basename(fp))
        continue
    if isinstance(arr, dict): arr = arr.get("findings", [])
    for it in (arr or []):
        if not isinstance(it, dict) or not it.get("finding_id"):
            continue
        fid, sk = it["finding_id"], it.get("skill", "")
        olr = it.get("observability_level_required")
        meta = {"skill": sk, "severity": it.get("severity", "info"),
                "fpr": it.get("false_positive_risk", "high"),
                "olr": olr if (type(olr) is int and 0 <= olr <= 3) else None}
        findings[fid] = meta                        # bare id (last wins on collision)
        if sk: findings["%s:%s" % (sk, fid)] = meta # skill-qualified (globally unique)
        n_findings += 1

# ---- attack prose: strip a stray code fence; flag dangling inline citations ----
attack = re.sub(r"^```[a-zA-Z]*\n|\n```$", "", open(attack_path, encoding="utf-8").read().strip()).strip()
cited = {t.strip() for t in re.findall(r"\[([A-Za-z][\w:.\-]*\d[\w:.\-]*)\]", attack)}
dangling = sorted(t for t in cited if t not in claims and t not in findings)

# ---- defense JSON points ----
draw = open(defense_path, encoding="utf-8").read()
m = re.search(r"\[.*\]", draw, re.S)               # tolerate prose / code-fence wrapping
try:
    points = json.loads(m.group(0) if m else draw)
except Exception:
    sys.exit("DEFENSE_PARSE_FAILED: re-run Step 2 with 'Output ONLY the JSON array, nothing else.'")
if isinstance(points, dict): points = points.get("points", [])

CLS = {"already_addressed", "partially_addressed", "unresolved"}
SEV = {"critical", "major", "minor"}

def valid_anchor(a):
    if not isinstance(a, dict): return None
    ref = a.get("ref") or a.get("id") or ""
    span = nw(a.get("span", ""))
    if ref in claims:                              # claim anchor REQUIRES a verbatim span
        if span and span in nw(claims[ref].get("text_span", "")):
            return {"ref": ref, "kind": "claim", "span": span}
        return None
    if ref in findings:                            # finding id alone is a valid anchor
        f = findings[ref]
        return {"ref": ref, "kind": "finding", "severity": f["severity"],
                "fpr": f["fpr"], "olr": f["olr"]}
    return None

kept, dropped = [], []
for i, p in enumerate(points, 1):
    if not isinstance(p, dict): continue
    good = [v for v in (valid_anchor(a) for a in (p.get("anchors") or [])) if v]
    cls = p.get("classification"); cls = cls if cls in CLS else "already_addressed"  # unknown -> not load-bearing
    rs = p.get("residual_severity"); rs = rs if rs in SEV else "minor"
    olr = p.get("observability_level_required")
    olr = olr if (type(olr) is int and 0 <= olr <= 3) else 0
    rec = {"id": p.get("id") or ("P%d" % i), "label": p.get("label", ""),
           "attack_claim": nw(p.get("attack_claim", "")), "classification": cls,
           "residual_severity": rs, "observability_level_required": olr,
           "defense_evidence": nw(p.get("defense_evidence", "")),
           "reviewer_action": nw(p.get("reviewer_action", "")), "anchors": good}
    (kept if good else dropped).append(rec)
for j, p in enumerate(kept, 1): p["id"] = "P%d" % j   # stable renumber

def decidable_crit(p):
    # INFORMATIONAL heuristic (NOT a verdict): flag a "constructed" kill only if an
    # UNRESOLVED point rests on a finding the upstream auditor DECLARED critical, FP
    # low, and decidable at the run level L. The adjudicator independently re-applies
    # the full gate stack (incl. span-anchor + surface cap) and owns the real verdict;
    # a minor / high-FP / observability-demoted finding can never reach this.
    return p["classification"] == "unresolved" and any(
        a["kind"] == "finding" and a.get("severity") == "critical"
        and a.get("fpr") == "low" and type(a.get("olr")) is int and a["olr"] <= L
        for a in p["anchors"])

if any(decidable_crit(p) for p in kept):
    disp = "kill_constructed"
elif any(p["classification"] in ("unresolved", "partially_addressed") for p in kept):
    disp = "partial_case"
else:
    disp = "honest_null"
unresolved = [p for p in kept if p["classification"] == "unresolved"]
counts = {c: sum(1 for p in kept if p["classification"] == c) for c in CLS}

# ---- render the memo (markdown; embedded verbatim under the adjudicator's memo H2) ----
def anchstr(a):
    if a["kind"] == "claim":
        loc = claims[a["ref"]].get("location", {}) or {}
        where = loc.get("section") or os.path.basename(str(loc.get("file", ""))) or ""
        return ("claim `%s`" % a["ref"]) + ((" (%s)" % where) if where else "") + \
               ((": “%s”" % a["span"]) if a.get("span") else "")
    f = findings.get(a["ref"], {})
    return "finding `%s`" % a["ref"] + ((" (%s, %s)" % (f.get("skill", ""), f.get("severity", ""))) if f else "")

BADGE = {"already_addressed": "✅ already_addressed",
         "partially_addressed": "\U0001f7e1 partially_addressed",
         "unresolved": "\U0001f534 unresolved"}
out = []
out.append("**Adversarial Case — %s** (evidence-bound, MEMO-ONLY — no verdict weight)." % PID)
out.append("Reviewer: gpt-5.5 xhigh, two fresh threads (no codex-reply)  ·  Run level: L%d  "
           "·  Attack thread: %s  ·  Defense thread: %s" % (L, attack_tid or "—", defense_tid or "—"))
out.append("Disposition (informational, NOT the report verdict): **%s**  ·  Evidence universe: "
           "%d ledger claims · %d confirmed findings" % (disp, len(claims), n_findings))
if dangling:
    out.append("⚠ Dangling attack citations dropped (not in the ledger/findings): %s" % ", ".join(dangling))
if bad_findings:
    out.append("⚠ Unreadable findings file(s) SKIPPED (evidence universe reduced): %s" % ", ".join(bad_findings))
out += ["", "### Strongest case to reject (attack, verbatim)", ""]
out += [("> " + ln) if ln.strip() else ">" for ln in (attack or "_(empty attack)_").splitlines()]
out += ["", "### Point-by-point adjudication (evidence-bound)", ""]
order = (unresolved + [p for p in kept if p["classification"] == "partially_addressed"]
         + [p for p in kept if p["classification"] == "already_addressed"])
if not order:
    out += ["_No anchored objection survived validation._", ""]
for p in order:
    out.append("#### %s — %s  ·  %s" % (p["id"], p["label"] or "(unlabeled)",
                                                  BADGE.get(p["classification"], p["classification"])))
    if p["attack_claim"]: out.append("- **Attack:** %s" % p["attack_claim"])
    if p["anchors"]:      out.append("- **Anchors:** " + " ; ".join(anchstr(a) for a in p["anchors"]))
    if p["defense_evidence"]: out.append("- **Defense / evidence:** %s" % p["defense_evidence"])
    if p["classification"] == "unresolved":
        out.append("- **Residual severity (descriptive, not a verdict):** %s · decidable at L%d"
                   % (p["residual_severity"], p["observability_level_required"]))
    if p["reviewer_action"]: out.append("- **Reviewer action:** %s" % p["reviewer_action"])
    out.append("")
out += ["### Unresolved questions for the human reviewer", ""]
out += ([ "- (%s) %s" % (p["id"], p["reviewer_action"] or p["attack_claim"]) for p in unresolved]
        or ["- _None — no objection went unresolved on the anchored evidence._"])
out.append("")
if disp == "honest_null":
    out += ["### Honest null", "",
            "On the anchored evidence at L%d, the strongest evidence-bound case does **not** sustain a "
            "rejection: every anchored objection is `already_addressed` or only `partially_addressed` "
            "(minor / high-FP / observability-demoted signals, or claims already accounted for). The "
            "paper **survives** this adversarial pass at this level. No kill was manufactured — this "
            "is a valid, expected result." % L, ""]
if dropped:
    out += ["### Dropped (uncited rhetoric — no valid anchor, excluded from the case)", ""]
    out += ["- %s: %s" % (p["label"] or "(no label)", p["attack_claim"]) for p in dropped]
    out.append("")
out += ["### Anchoring audit", "",
        "- points kept: %d  ·  dropped (uncited): %d  ·  dangling attack citations: %d"
        % (len(kept), len(dropped), len(dangling)),
        "- classification: already_addressed %d · partially_addressed %d · unresolved %d"
        % (counts["already_addressed"], counts["partially_addressed"], counts["unresolved"]), ""]
out += ["---",
        "_Informational only. `tools/adjudicate_findings.py` lists `adversarial-case-builder` in "
        "`MEMO_ONLY_SKILLS` and caps every finding it could emit at `info`, so this memo contributes "
        "**no verdict weight**. The deterministic adjudicator owns the verdict._"]
memo_path = os.path.join(D, "adversarial-case-builder.memo.md")
open(memo_path, "w", encoding="utf-8").write("\n".join(out) + "\n")

# ---- info-only findings mirror: one per unresolved point; MEMO gate caps at info anyway ----
acb = []
for k, p in enumerate(unresolved, 1):
    ev = [{"claim_id": a["ref"], "span": a["span"],
           "location": claims[a["ref"]].get("location", {}),
           "artifact_hash": claims[a["ref"]].get("evidence_anchor", "")}
          for a in p["anchors"] if a["kind"] == "claim" and a.get("span")]
    acb.append({
        "finding_id": "ACB%03d" % k, "skill": "adversarial-case-builder",
        "title": (p["label"] or "adversarial objection")[:120],
        "description": (p["attack_claim"] + ((" — " + p["defense_evidence"]) if p["defense_evidence"] else "")).strip(),
        "severity": "info",                        # memo-only: never verdict-bearing
        "observability_level_required": p["observability_level_required"],
        "evidence": ev,                            # may be [] (schema permits empty evidence for info)
        "verdict_local": "warn", "requires_external_check": False, "false_positive_risk": "high",
        "recommended_reviewer_action": p["reviewer_action"] or ("Press the authors on: " + p["attack_claim"]),
        "reviewer": {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False, "thread_id": defense_tid},
    })
find_path = os.path.join(D, "adversarial-case-builder.findings.json")
json.dump(acb, open(find_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print("disposition=%s (informational, NOT a verdict) | kept=%d (unresolved=%d, partially_addressed=%d, "
      "already_addressed=%d) | dropped_uncited=%d | dangling=%d | bad_findings=%d"
      % (disp, len(kept), counts["unresolved"], counts["partially_addressed"],
         counts["already_addressed"], len(dropped), len(dangling), len(bad_findings)))
print("memo     ->", memo_path)
print("findings ->", find_path, "(%d info-only)" % len(acb))
PY
```
