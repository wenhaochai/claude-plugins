# Step scripts

## Contents

- Re-entrancy probe
- Step 0 — ingest
- Step 1 — read-back
- Step 2 — auditor decision
- Step 2 — anchor sweep
- Step 4 — report check

## Re-entrancy probe

```bash
PAPER_DIR="<from Step 0>"
python3 - "$PAPER_DIR" <<'PY'
import json, os, glob, sys
D = sys.argv[1]
def is_array(p):
    try: return isinstance(json.load(open(p, encoding="utf-8")), list)
    except Exception: return False
def is_ledger(p):
    try:
        d = json.load(open(p, encoding="utf-8")); return isinstance(d, dict) and "claims" in d
    except Exception: return False
def newest_source(d):
    s = []
    for ext in ("*.tex", "*.txt", "*.bib"):
        s += glob.glob(os.path.join(d, ext)) + glob.glob(os.path.join(d, "**", ext), recursive=True)
    return max((os.path.getmtime(p) for p in s), default=0.0)
led = os.path.join(D, "claims.json"); have = is_ledger(led)
stale = have and os.path.getmtime(led) < newest_source(D)
print(f"STEP1 ledger      : {'present' if have else 'MISSING'}{'  ⚠ STALE → rebuild (sources changed)' if stale else ''}")
for f in ("consistency-audit.deterministic", "consistency-audit", "citation-forensics",
          "baseline-comparison-audit", "experiment-forensics",
          "presentation-signals.deterministic", "presentation-signals",
          "proof-derivation-forensics", "eval-design-forensics",
          "ai-style-impressions.deterministic", "ai-style-impressions"):
    p = os.path.join(D, f + ".findings.json")
    print(f"STEP2 {f:<32}: {'ok' if (os.path.isfile(p) and is_array(p)) else 'todo'}")
print(f"STEP3 adversarial memo            : {'present' if os.path.isfile(os.path.join(D,'adversarial-case-builder.memo.md')) else 'todo'}")
print(f"STEP3 novelty advisory memo       : {'present' if os.path.isfile(os.path.join(D,'novelty-duplication-advisory.memo.md')) else 'todo'}")
print(f"STEP4 report.json : {'present' if os.path.isfile(os.path.join(D,'report.json')) else 'todo'}")
PY
```

## Step 0 — ingest

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
test -f "$ROOT/tools/adjudicate_findings.py" || { echo "FATAL: not inside the Anti-Autoresearch checkout (point ROOT at it)."; exit 1; }
ARG="$ARGUMENTS"

if [ -d "$ARG" ]; then                       # ---- DIRECTORY ----
  PAPER_DIR="$(cd "$ARG" && pwd)"
  # if only a PDF is present, extract text so the ledger has an L0 source
  if ! ls "$PAPER_DIR"/*.tex >/dev/null 2>&1 && ! ls "$PAPER_DIR"/*.txt >/dev/null 2>&1; then
    P=$(ls "$PAPER_DIR"/*.pdf 2>/dev/null | head -1)
    [ -n "$P" ] && pdftotext -layout "$P" "$PAPER_DIR/paper.txt"
  fi

elif [ -f "$ARG" ] && case "$ARG" in *.pdf) true;; *) false;; esac; then   # ---- PDF FILE ----
  PAPER_DIR="$(cd "$(dirname "$ARG")" && pwd)"
  pdftotext -layout "$ARG" "$PAPER_DIR/paper.txt" \
    || echo "WARN: pdftotext failed/missing — try: mutool draw -F txt, or pip install pdfminer.six (pdf2txt.py)."

else                                          # ---- ARXIV ID (e.g. 2401.01234) ----
  ID=$(printf '%s' "$ARG" | grep -oE '[0-9]{4}\.[0-9]{4,5}(v[0-9]+)?' | head -1)
  [ -n "$ID" ] || { echo "FATAL: '$ARG' is not a dir, a .pdf, or an arXiv id."; exit 1; }
  PAPER_DIR="$(pwd)/aar-$ID"; mkdir -p "$PAPER_DIR"
  # LaTeX source first (best spans → L1). e-print may be a tarball OR a single gzipped .tex.
  if curl -fsSL "https://arxiv.org/e-print/$ID" -o "$PAPER_DIR/src.tgz"; then
    tar -xzf "$PAPER_DIR/src.tgz" -C "$PAPER_DIR" 2>/dev/null \
      || gunzip -c "$PAPER_DIR/src.tgz" > "$PAPER_DIR/main.tex" 2>/dev/null
  fi
  if ! ls "$PAPER_DIR"/*.tex >/dev/null 2>&1; then     # fallback: PDF → text (L0)
    curl -fsSL "https://arxiv.org/pdf/$ID.pdf" -o "$PAPER_DIR/paper.pdf" \
      && pdftotext -layout "$PAPER_DIR/paper.pdf" "$PAPER_DIR/paper.txt"
  fi
fi

echo "PAPER_DIR = $PAPER_DIR"
ls -1 "$PAPER_DIR"/*.tex "$PAPER_DIR"/*.bib "$PAPER_DIR"/*.txt "$PAPER_DIR"/*.pdf 2>/dev/null
ls -d  "$PAPER_DIR"/code "$PAPER_DIR"/src "$PAPER_DIR"/results "$PAPER_DIR"/outputs 2>/dev/null   # L2 candidates
```

## Step 1 — read-back

```bash
PAPER_DIR="<from Step 0>"
test -f "$PAPER_DIR/claims.json" || { echo "FATAL: /evidence-ledger did not produce claims.json — re-run Step 1."; exit 1; }
L=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["observability_level"])' "$PAPER_DIR/claims.json")
PAPER_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["paper_id"])' "$PAPER_DIR/claims.json")
python3 - "$PAPER_DIR/claims.json" "$PAPER_DIR/artifact_manifest.json" <<'PY'
import json, sys, collections
L = json.load(open(sys.argv[1], encoding="utf-8")); M = json.load(open(sys.argv[2], encoding="utf-8"))
assert L["observability_level"] == M["observability_level"], "ledger level != manifest level"
t = collections.Counter(c["type"] for c in L["claims"])
print(f"PAPER_ID={L['paper_id']}  L={L['observability_level']}  claims={len(L['claims'])}  types={dict(t)}")
PY
```

## Step 2 — auditor decision

```bash
PAPER_DIR="<from Step 0>"
python3 - "$PAPER_DIR/claims.json" <<'PY'
import json, re, sys, os
d = json.load(open(sys.argv[1], encoding="utf-8")); cl = d.get("claims", [])
paper_dir = os.path.dirname(os.path.abspath(sys.argv[1])) or "."
CMP = re.compile(r"state[- ]of[- ]the[- ]art|\bSOTA\b|outperform\w*|\bbest\b|surpass\w*|"
                 r"beats?|superior|first to|compared? (?:to|with)|baseline|prior (?:work|art)", re.I)
has_cite = any(c.get("type") == "citation" for c in cl)
has_cmp  = any(c.get("type") in ("scope", "comparison", "baseline", "caption") and CMP.search(c.get("text_span","")) for c in cl)
# proofs: scan the SOURCE for theorem/proof/derivation markers (mirrors /proof-derivation-forensics's
# own HAS_PROOFS gate). The skill self-guards (writes [] if it finds none), so this gate is a
# budget hint, not a correctness gate — running proof-derivation-forensics unconditionally is safe.
TH  = re.compile(r"\\begin\{(theorem|lemma|proposition|corollary|claim|conjecture|"
                 r"proof|definition|assumption)\*?\}", re.I)
EQ  = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray)\*?\}|\\\[", re.I)
TXT = re.compile(r"\b(Theorem|Lemma|Proposition|Corollary|Proof|Q\.?E\.?D\.?)\b")
ph = 0
for s in d.get("source_files", []):
    sp = s.get("path", ""); kind = s.get("kind", "")
    cand = sp if os.path.isabs(sp) else os.path.join(paper_dir, sp)
    if not os.path.isfile(cand): cand = sp
    try: t = open(cand, encoding="utf-8", errors="replace").read()
    except OSError: continue
    ph += (len(TH.findall(t)) + len(EQ.findall(t))) if kind == "latex" else len(TXT.findall(t))
if ph == 0:                                            # L0 fallback: theorem/proof words inside ledger spans
    ph = sum(1 for c in cl if TXT.search(c.get("text_span", "") or ""))
has_proof = ph > 0
# contribution claims (Step 3 novelty advisory anchor universe): scope/method/comparison OR abstract/intro
CONTRIB_SECT = {"abstract", "intro", "introduction"}
has_contrib = any((c.get("type") in ("scope", "method", "comparison")
                   or ((c.get("location") or {}).get("section", "") or "").lower() in CONTRIB_SECT)
                  and c.get("claim_id") and c.get("text_span") for c in cl)
print("RUN (always): /consistency-audit  /experiment-forensics  /presentation-signals  /ai-style-impressions")
print(f"RUN /citation-forensics            : {has_cite}   (≥1 citation claim)")
print(f"RUN /baseline-comparison-audit     : {has_cmp}    (≥1 comparison/SOTA scope claim)")
print(f"RUN /proof-derivation-forensics    : {has_proof}   (≥1 theorem/proof/derivation marker; self-guards → [] if none)")
print(f"RUN /eval-design-forensics         : {has_cmp}    (≥1 comparison/eval claim · leakage / judge-validity / selective-reporting; self-guards → [] if no eval protocol)")
print(f"RUN /novelty-duplication-advisory  : {has_contrib}   (Step 3 memo · ≥1 contribution claim · MEMO-ONLY)")
PY
```

## Step 2 — anchor sweep

```bash
PAPER_DIR="<from Step 0>"
python3 - "$PAPER_DIR" <<'PY'
import json, glob, os, sys
D = sys.argv[1]
claims = {c["claim_id"]: " ".join((c.get("text_span") or "").split())
          for c in json.load(open(f"{D}/claims.json", encoding="utf-8"))["claims"] if c.get("claim_id")}
nw = lambda s: " ".join((s or "").split()); ABOVE = {"critical", "major", "minor"}
mandatory = ["consistency-audit.deterministic", "consistency-audit", "experiment-forensics",
             "presentation-signals.deterministic", "presentation-signals",
             "ai-style-impressions.deterministic", "ai-style-impressions"]
missing = []
for f in mandatory:
    p = f"{D}/{f}.findings.json"; ok = os.path.isfile(p)
    if ok:
        try: ok = isinstance(json.load(open(p, encoding="utf-8")), list)
        except Exception: ok = False
    if not ok: missing.append(f)
total_bad = 0
for p in sorted(glob.glob(f"{D}/*.findings.json")):
    if p.endswith(".proposed.findings.json"): continue   # defensive: never adjudicate a raw/intermediate file
    try: arr = json.load(open(p, encoding="utf-8"))
    except Exception: print(f"BAD JSON  {os.path.basename(p)}"); continue
    bad = sum(1 for f in arr if f.get("severity") in ABOVE and not any(
        ev.get("claim_id") in claims and nw(ev.get("span")) and nw(ev["span"]) in claims[ev["claim_id"]]
        for ev in (f.get("evidence") or [])))
    total_bad += bad
    print(f"{os.path.basename(p):<46} findings={len(arr):<3} above-info-unanchored={bad}")
if missing: print("MISSING/BAD mandatory:", ", ".join(missing), "-> re-run those auditors")
print(f"TOTAL unanchored above-info (adjudicator will demote to info): {total_bad}")
PY
```

## Step 4 — report check

```bash
PAPER_DIR="<from Step 0>"
python3 - "$PAPER_DIR/report.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1], encoding="utf-8"))
assert r["overall_verdict"] in {"CLEAN_GIVEN_EVIDENCE", "SOFT_FLAGS", "HARD_FLAGS"}, r["overall_verdict"]
assert r["adjudicator"] == "deterministic-rules-v0" and r["human_review_required"] is True
assert r["anchoring_verified"] is True, "ledger anchoring did not run — --ledger missing?"
assert r["limitations"], "limitations must always be populated (the honesty contract)"
c = r["counts"]
print(f"verdict={r['overall_verdict']}  L={r['observability_level']}  taxonomy=v{r['taxonomy_version']}")
print(f"counts: crit={c['critical']} maj={c['major']} min={c['minor']} info={c['info']} "
      f"obs-demoted={c['downgraded_for_observability']} unanchored-demoted={c.get('unanchored_demoted',0)}")
PY
```
