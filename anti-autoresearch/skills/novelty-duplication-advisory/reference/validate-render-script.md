# Step 4 — validate, anchor, render memo + findings mirror script

## Contents

- Script
- Scope of this gate

## Script

```bash
PAPER_DIR="<abs PAPER_DIR from Step 0>"
LEDGER="$PAPER_DIR/claims.json"
CAND="$PAPER_DIR/novelty-duplication-advisory.candidates.json"
TRACE="<abs TRACE dir from Step 0>"
RUNMETA="$TRACE/run.meta.json"
python3 - "$LEDGER" "$CAND" "$TRACE" "$PAPER_DIR" "$RUNMETA" <<'PY'
import json, re, sys, os, glob
ledger_path, cand_path, trace_dir, paper_dir, runmeta = sys.argv[1:6]
def nw(s): return " ".join((s or "").split())

led = json.load(open(ledger_path, encoding="utf-8"))
L = int(led.get("observability_level", 0)); PID = led.get("paper_id", "?")
CONTRIB_TYPES = {"scope", "method", "comparison"}
CONTRIB_SECT  = {"abstract", "intro", "introduction"}
# a contribution CUE — so an abstract/intro claim only anchors if it actually states a
# contribution, not background/citation/problem-statement text (avoids over-anchoring).
CONTRIB_CUE = re.compile(r"\b(we\s+(propose|present|introduce|develop|design|show|"
                         r"contribute)|our\s+(method|approach|model|framework|contribution)|"
                         r"novel|first\s+to|state[- ]of[- ]the[- ]art|key\s+(idea|contribution))\b", re.I)
def sect(c): return ((c.get("location") or {}).get("section") or "").lower()
def is_contrib(c):
    if c.get("type") in CONTRIB_TYPES: return True            # deterministic contribution types
    return sect(c) in CONTRIB_SECT and bool(CONTRIB_CUE.search(c.get("text_span", "")))
claims = {c["claim_id"]: c for c in led.get("claims", [])
          if c.get("claim_id") and is_contrib(c)}

cands = {}
if os.path.isfile(cand_path):
    for c in json.load(open(cand_path, encoding="utf-8")):
        if isinstance(c, dict) and c.get("candidate_id"):
            cands[c["candidate_id"]] = c

# retrieval_incomplete is honestly recorded by Step 2 in run.meta.json
retrieval_incomplete = False
try:
    rm = json.load(open(runmeta, encoding="utf-8"))
    rv = rm.get("retrieval", {})
    retrieval_incomplete = isinstance(rv, dict) and any(v == "unavailable" for v in rv.values())
except Exception:
    pass

AXES = {"duplicate": "ADV-DUPLICATE-PUBLICATION", "combination": "ADV-TRIVIAL-COMBINATION"}
# neutralize leaked VERDICT phrasings. The bare descriptive word "duplicate" stays intact
# (it is this skill's axis term — e.g. "duplicate axis", "duplicate candidate"), but RULING
# phrasings that assert a verdict ("is a duplicate", "duplicate of", "duplicated publication")
# ARE scrubbed — surfacing candidate overlap must never read as a ruling that it IS a duplicate.
RULE_WORDS = re.compile(
    r"\b(not\s+novel|lacks?\s+novelty|trivial\w*|incremental|mere\s+stapl\w*|"
    r"reject\w*|plagiar\w*|derivative|duplicate[sd]?\s+publication|repackag\w*)\b"
    r"|\b(?:is|are|appears?|seems?|clearly|essentially|simply)\s+(?:a\s+|an\s+)?duplicate\b"
    r"|\bduplicate\s+of\b|缝合", re.I)
n_scrubbed = 0
def scrub(s):
    global n_scrubbed
    out, n = RULE_WORDS.subn("[reviewer-judgment]", s or "")
    n_scrubbed += n; return out

def claim_anchor(a):
    if not isinstance(a, dict): return None
    cid, span = a.get("claim_id"), nw(a.get("span", ""))
    c = claims.get(cid)
    if c and span and span in nw(c.get("text_span", "")):   # span IN claim, never claim IN span
        return {"claim_id": cid, "span": span,
                "location": c.get("location", {}), "artifact_hash": c.get("evidence_anchor", "")}
    return None

items, dropped, n_halluc = [], [], 0
for fp in sorted(glob.glob(os.path.join(trace_dir, "*.response.md"))):
    raw = open(fp, encoding="utf-8", errors="replace").read()
    m = re.search(r"\[.*\]", raw, re.S)            # tolerate prose / code-fence wrapping
    if not m:
        print(f"  note: no JSON array in {os.path.basename(fp)} (treated as [])"); continue
    try:
        arr = json.loads(m.group(0))
    except Exception as e:
        print(f"  WARN: unparseable JSON in {os.path.basename(fp)}: {e} (treated as [])"); continue
    if isinstance(arr, dict): arr = arr.get("findings", arr.get("items", []))
    for it in (arr or []):
        if not isinstance(it, dict): dropped.append({"why": "malformed"}); continue
        axis = it.get("axis")
        if axis not in AXES:                       # infer from pattern_id if missing
            axis = next((a for a, p in AXES.items() if p == it.get("pattern_id")), None)
        if axis not in AXES:
            dropped.append({"label": it.get("label", ""), "why": "unknown-axis"}); continue
        anch = [v for v in (claim_anchor(a) for a in (it.get("anchors") or [])) if v]
        good_ids, bad_ids, self_ids = [], [], []
        for cid in (it.get("candidate_ids") or []):
            c = cands.get(cid)
            if not c:
                bad_ids.append(cid)                                  # not in candidates.json -> hallucinated ref
            elif axis == "duplicate" and c.get("self_record_suspected"):
                self_ids.append(cid)                                 # confirmed own record -> excluded (NOT hallucinated)
            else:
                good_ids.append(cid)                                 # real candidate (incl. self_record_unconfirmed -> surfaced w/ flag)
        n_halluc += len(bad_ids)
        rec = {"axis": axis, "pattern_id": AXES[axis], "label": scrub(nw(it.get("label", ""))),
               "overlap_statement": scrub(nw(it.get("overlap_statement", ""))), "anchors": anch,
               "candidate_ids": good_ids, "overlap_kind": nw(it.get("overlap_kind", "")),
               "residual_delta_note": scrub(nw(it.get("residual_delta_note", ""))),
               "reviewer_action": scrub(nw(it.get("reviewer_action", "")))}
        # LOAD-BEARING only if it anchors to a real contribution span AND cites a real candidate
        if anch and good_ids:
            items.append(rec)
        else:
            dropped.append({**rec, "why": ("no-anchor" if not anch else "no-resolved-candidate")})
for i, p in enumerate(items, 1): p["id"] = "O%d" % i

n_dup  = sum(1 for p in items if p["axis"] == "duplicate")
n_comb = sum(1 for p in items if p["axis"] == "combination")
if retrieval_incomplete: disp = "retrieval_incomplete"
elif items:              disp = "candidate_overlap_surfaced"
else:                    disp = "no_candidate_overlap_found"

# ---------- render memo ----------
def cstr(cid):
    c = cands.get(cid, {}); idv = c.get("identifier", {}) or {}
    ref = idv.get("arxiv") or idv.get("doi") or idv.get("dblp_url") or idv.get("url") or ""
    flag = (" ⚠️ near-identical title, authorship unverified — confirm self-record vs real duplicate"
            if c.get("self_record_unconfirmed") else "")
    return f"**{c.get('title','?')}** ({c.get('venue','?')} {c.get('year','?')}) — `{ref}` [{cid}]{flag}"
def astr(a):
    sec = (a.get("location") or {}).get("section", "")
    return f"claim `{a['claim_id']}`{f' ({sec})' if sec else ''}: “{a['span']}”"

out = []
out.append(f"**Novelty / Duplication Advisory — {PID}** (retrieval-grounded, MEMO-ONLY — no verdict weight).")
out.append(f"Reviewer: gpt-5.5 xhigh, two fresh per-axis threads (no codex-reply)  ·  Run level: L{L}  "
           f"·  Disposition (informational, NOT a verdict): **{disp}**")
out.append(f"Overlap items surfaced: {n_dup} duplicate · {n_comb} combination  ·  Candidates retrieved: {len(cands)}  "
           f"·  Hallucinated candidate refs dropped: {n_halluc}  ·  Ruling words neutralized: {n_scrubbed}")
out += ["", "> ⚠️ **This is not a novelty verdict.** It lays out prior work the contribution OVERLAPS with so a "
        "human reviewer can weigh `ADV-TRIVIAL-COMBINATION` and `ADV-DUPLICATE-PUBLICATION` themselves. **It never "
        "rules \"trivial\" or \"duplicate\", and the absence of a candidate match below is NOT evidence of "
        "originality** — the search corpus is incomplete by construction (recent / non-indexed / paywalled / "
        "differently-titled work is missed). A same-authors match is legitimate self-overlap (arXiv→venue, "
        "workshop→conference, extended journal), not misconduct. `tools/adjudicate_findings.py` lists this skill in "
        "`MEMO_ONLY_SKILLS` and caps it at `info`; it carries no verdict weight.", ""]

for axis, head in [("duplicate", "ADV-DUPLICATE-PUBLICATION — candidate near-duplicates (verify; never a verdict)"),
                   ("combination", "ADV-TRIVIAL-COMBINATION — is the contribution a standard A+B+C? (reviewer judgment)")]:
    rows = [p for p in items if p["axis"] == axis]
    out += [f"### {head}", ""]
    if not rows:
        out += ["_No resolved candidate overlap surfaced on this axis. **Not** an originality finding — see the caveat above._", ""]
        continue
    for p in rows:
        out.append(f"#### {p['id']} — {p['label'] or '(unlabeled)'}  ·  _{p['overlap_kind'] or 'overlap'}_")
        if p["overlap_statement"]:   out.append(f"- **Overlap:** {p['overlap_statement']}")
        if p["anchors"]:             out.append("- **Submission contribution (anchor):** " + " ; ".join(astr(a) for a in p["anchors"]))
        if p["candidate_ids"]:       out.append("- **Candidate prior work:** " + " ; ".join(cstr(c) for c in p["candidate_ids"]))
        if p["residual_delta_note"]: out.append(f"- **Residual delta the paper still claims (descriptive):** {p['residual_delta_note']}")
        if p["reviewer_action"]:     out.append(f"- **For the human reviewer to weigh:** {p['reviewer_action']}")
        out.append("")

if disp == "no_candidate_overlap_found":
    out += ["### No candidate overlap found (NOT an originality verdict)", "",
            "The retrieval ran but surfaced no resolved prior-work overlap with the submission's title / "
            "contribution at this search depth. This is **not** evidence the work is original: the corpus search is "
            "necessarily incomplete, and the queries are bounded by the ledger's contribution spans. A human reviewer "
            "should still judge novelty against their own knowledge of the field. No verdict is rendered.", ""]
elif disp == "retrieval_incomplete":
    out += ["### Retrieval incomplete (inconclusive)", "",
            "One or more lookups were unavailable, so the prior-work search could not be completed. This memo "
            "concludes **nothing** about novelty or duplication; re-run with corpus access for a fuller picture.", ""]
if dropped:
    out += ["### Dropped (no anchor / no resolved candidate — excluded from the brief)", ""]
    out += [f"- {p.get('label') or '(no label)'}: {p.get('why','')}" for p in dropped]
    out.append("")
out += ["### Retrieval & anchoring audit", "",
        f"- overlap items surfaced: {len(items)}  ·  dropped: {len(dropped)}  ·  hallucinated/self candidate refs dropped: {n_halluc}  ·  ruling words neutralized: {n_scrubbed}",
        "- every surfaced candidate is a resolved record in candidates.json (real call + verifiable id); every anchor "
        "is a verbatim span of a contribution ledger claim.", ""]
out += ["---",
        "_Informational only. `tools/adjudicate_findings.py` lists `novelty-duplication-advisory` in "
        "`MEMO_ONLY_SKILLS` and caps every finding it emits at `info`, so this memo contributes **no verdict "
        "weight**. Novelty is a reviewer judgment; the deterministic adjudicator owns the report verdict, and neither "
        "it nor this skill rules \"trivial\" or \"duplicate\"._"]
memo_path = os.path.join(paper_dir, "novelty-duplication-advisory.memo.md")
open(memo_path, "w", encoding="utf-8").write("\n".join(out) + "\n")

# ---------- info-only findings mirror: one per surfaced item; MEMO gate caps at info ----------
mir = []
for k, p in enumerate(items, 1):
    cdesc = "; ".join(cstr(c) for c in p["candidate_ids"])
    ev = [{"claim_id": a["claim_id"], "span": a["span"], "location": a.get("location", {}),
           "artifact_hash": a.get("artifact_hash", "")} for a in p["anchors"]]
    mir.append({
        "finding_id": "NDA%03d" % k, "skill": "novelty-duplication-advisory",
        "pattern_id": p["pattern_id"],
        "title": (p["label"] or "prior-work overlap")[:120],
        "description": (p["overlap_statement"] + (" — candidates: " + cdesc if cdesc else "")
                        + ((" Residual: " + p["residual_delta_note"]) if p["residual_delta_note"] else "")
                        + "  [ADVISORY: prior-work overlap for the reviewer to weigh — NOT a trivial/duplicate ruling.]").strip(),
        "severity": "info",                        # memo-only: never verdict-bearing
        "observability_level_required": 0,
        "evidence": ev,                            # may be [] (schema permits empty evidence for info)
        "verdict_local": "needs_external_check", "requires_external_check": True,
        "false_positive_risk": "high",
        "recommended_reviewer_action": p["reviewer_action"] or ("Weigh the contribution against: " + cdesc),
        "reviewer": {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False},
    })
find_path = os.path.join(paper_dir, "novelty-duplication-advisory.findings.json")
json.dump(mir, open(find_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"disposition={disp} (informational, NOT a verdict) | surfaced={len(items)} (dup={n_dup}, comb={n_comb}) "
      f"| dropped={len(dropped)} | hallucinated/self_dropped={n_halluc} | ruling_scrubbed={n_scrubbed}")
print("memo     ->", memo_path)
print("findings ->", find_path, f"({len(mir)} info-only)")
PY
```

## Scope of this gate

**Scope of this gate:** anchor validation (verbatim span of a contribution claim), candidate
validation (the **anti-hallucination** check — every `candidate_id` must exist in
`candidates.json`; self-records excluded from the duplicate axis), ruling-word neutralization,
the informational disposition, and rendering. It computes **no verdict** and prints **no
novelty grade** — the memo is advisory and the adjudicator decides (and caps this skill at
`info`).
