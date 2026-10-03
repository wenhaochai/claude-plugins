# Step 1 — retrieval profile script

## Script

```bash
LEDGER="<abs claims.json from Step 0>"
PAPER_DIR="$(dirname "$LEDGER")"
python3 - "$LEDGER" "$PAPER_DIR" <<'PY'
import json, sys, os, re
ledger_path, paper_dir = sys.argv[1], sys.argv[2]
d = json.load(open(ledger_path, encoding="utf-8"))
claims = d.get("claims", []); PID = d.get("paper_id", "?")
src = d.get("source_files", []) or []
def sect(c): return ((c.get("location") or {}).get("section") or "").lower()

CONTRIB_TYPES = {"scope", "method", "comparison"}
CONTRIB_SECT  = {"abstract", "intro", "introduction"}
PRI = {"abstract", "intro", "introduction"}
CUE = re.compile(r"\b(we\s+(propose|present|introduce|develop|design|show|demonstrate)|"
                 r"our\s+(approach|method|framework|model|contribution|key\s+idea)|"
                 r"in\s+this\s+(paper|work)|the\s+first\s+to|novel|contributions?\s+(are|of))\b", re.I)

ranked = []
for c in claims:
    if not c.get("claim_id") or not c.get("text_span"):
        continue
    s = sect(c)
    if not (c.get("type") in CONTRIB_TYPES or s in CONTRIB_SECT):
        continue
    span = c["text_span"]
    score = (2 if s in PRI else 0) + (2 if CUE.search(span) else 0) + (1 if c.get("type") in CONTRIB_TYPES else 0)
    ranked.append((score, {"claim_id": c["claim_id"], "type": c.get("type", "?"),
                           "section": s or "?", "text_span": span}))
ranked.sort(key=lambda x: -x[0])
contrib = [c for _, c in ranked][:10]

# title SEARCH SEED (never an anchor): prefer a title-section ledger claim, else \title{...}
# from a latex source (brace-matched), else the first substantive line of the pdf text.
def strip_tex(s):
    s = re.sub(r"\\thanks\{[^}]*\}", " ", s)
    s = re.sub(r"\\[a-zA-Z]+\*?", " ", s)
    return " ".join(s.replace("{", " ").replace("}", " ").replace("\\", " ").split())
def title_from_latex(txt):
    m = re.search(r"\\title\s*(\[[^\]]*\])?\s*\{", txt)
    if not m: return None
    i, depth = m.end(), 1
    while i < len(txt) and depth:
        depth += (txt[i] == "{") - (txt[i] == "}"); i += 1
    t = strip_tex(txt[m.end():i-1]); return t if len(t) >= 6 else None

title, title_src = None, None
for c in claims:
    if sect(c) == "title" and c.get("text_span"):
        title, title_src = c["text_span"], "ledger:title-claim"; break
if not title:
    for s in src:
        if s.get("kind") == "latex" and os.path.isfile(s.get("path", "")):
            t = title_from_latex(open(s["path"], encoding="utf-8", errors="replace").read())
            if t: title, title_src = t[:240], "source:" + os.path.basename(s["path"]); break
if not title:
    for s in src:
        if s.get("kind") in ("text", "pdf") and os.path.isfile(s.get("path", "")):
            for ln in open(s["path"], encoding="utf-8", errors="replace"):
                ln = ln.strip()
                if len(ln) >= 12 and not ln.lower().startswith(("arxiv", "http", "doi")):
                    title, title_src = ln[:240], "source:" + os.path.basename(s["path"]); break
        if title: break
if not title and contrib:
    title, title_src = contrib[0]["text_span"][:240], "fallback:abstract-claim"

prof = {"paper_id": PID, "title_seed": title, "title_seed_source": title_src,
        "title_seed_is_anchor": False, "contribution_claims": contrib,
        "n_contribution_claims": len(contrib)}
out = os.path.join(paper_dir, "novelty-duplication-advisory.profile.json")
json.dump(prof, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("PROFILE  =", out)
print("TITLE    =", (title or "(none — combination axis only)")[:120], "| source:", title_src)
print("CONTRIB  =", len(contrib))
for c in contrib[:10]:
    print(f"  [{c['claim_id']}] ({c['section']}/{c['type']}) {c['text_span'][:100]}")
if not contrib:
    print("NO_CONTRIB: ledger has no scope/method/comparison/abstract/intro claim — "
          "cannot build a retrieval query. Treat like CONTRIB_CLAIMS==0 (Step 4 honest-null).")
PY
```
