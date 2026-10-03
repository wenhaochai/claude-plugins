# Step 2c — candidates validation + self-record gate script

## Script

```bash
PAPER_DIR="<abs PAPER_DIR from Step 0>"
CAND="$PAPER_DIR/novelty-duplication-advisory.candidates.json"
PROF="$PAPER_DIR/novelty-duplication-advisory.profile.json"
python3 - "$CAND" "$PROF" <<'PY'
import json, sys, re
cand_path, prof_path = sys.argv[1], sys.argv[2]
prof = json.load(open(prof_path, encoding="utf-8"))
def norm(s): return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()
ptitle = norm(prof.get("title_seed"))
pauthors = {norm(a) for a in (prof.get("authors") or []) if a}   # audited paper's authors (for self-record check)
try:
    arr = json.load(open(cand_path, encoding="utf-8"))
except Exception as e:
    sys.exit(f"CANDIDATES_PARSE_FAILED: {e} — fix candidates.json (assemble from REAL calls only).")
SRC = {"dblp_fuzzy_title", "dblp_boolean", "websearch", "webfetch"}
seen, clean, dropped = set(), [], 0
for c in arr:
    if not isinstance(c, dict): dropped += 1; continue
    ident = c.get("identifier") or {}
    idval = next((v for v in (ident.get("arxiv"), ident.get("doi"),
                              ident.get("dblp_url"), ident.get("url")) if v), None)
    if c.get("source") not in SRC or not c.get("title") or not idval:
        dropped += 1; continue                      # no real source / no identifier -> not a real record
    key = idval.strip().lower()
    if key in seen: continue                        # de-dup by identifier
    seen.add(key)
    c["candidate_id"] = "K%02d" % (len(clean) + 1)  # re-id deterministically
    # self-record guard: a near-identical title MAY be the AUDITED paper's own record (its
    # preprint/venue copy). But title-similarity ALONE is not enough — a real duplicate-
    # publication by DIFFERENT authors can share a near-identical title. Treat as the paper's
    # OWN record (and exclude) ONLY when title is near-identical AND authorship overlaps; if the
    # title matches but authorship can't be confirmed, SURFACE it flagged for human author-check
    # rather than silently dropping a possible real duplicate.
    sim = c.get("title_similarity")
    title_match = bool(ptitle) and (norm(c.get("title")) == ptitle
                                    or (isinstance(sim, (int, float)) and sim >= 0.95))
    cand_auth = {norm(a) for a in (c.get("authors") or []) if a}
    authors_overlap = bool(pauthors and cand_auth and (pauthors & cand_auth))
    c["self_record_suspected"]   = bool(title_match and authors_overlap)        # confirmed own record -> exclude
    c["self_record_unconfirmed"] = bool(title_match and not authors_overlap)    # near title, authorship unverified -> surface + flag
    clean.append(c)
json.dump(clean, open(cand_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
dup = sum(1 for c in clean if c["retrieved_for"] == "duplicate" and not c["self_record_suspected"])
comb = sum(1 for c in clean if str(c["retrieved_for"]).startswith("combination"))
self_n = sum(1 for c in clean if c["self_record_suspected"])
print(f"candidates kept={len(clean)} (duplicate-axis usable={dup}, combination-axis={comb}, "
      f"self-record-suspected={self_n}) dropped(no-source/no-id/malformed)={dropped} -> {cand_path}")
if not clean:
    print("NO_CANDIDATES: retrieval surfaced nothing usable. This is a VALID result and says "
          "NOTHING about novelty (absence of a match is not evidence of originality). "
          "Step 4 -> disposition=no_candidate_overlap_found.")
PY
```
