---
name: novelty-duplication-advisory
description: "Retrieves uncited prior work and lays it beside a paper's contribution claims so a reviewer can weigh A+B+C stapling or duplicate publication. Memo-only, never rules novelty, not a plagiarism checker. Run after evidence-ledger. Triggers: \"prior-work overlap\", \"duplicate submission\", \"is this stapling\", \"缝合\", \"重复发表\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, WebSearch, WebFetch, mcp__codex__codex, mcp__mcp-dblp__fuzzy_title_search, mcp__mcp-dblp__search
---

# Novelty & Duplication Advisory — the overlap a reviewer should weigh

Lay out, for **$ARGUMENTS** (a paper-dir or a `claims.json` from `/evidence-ledger`), the
candidate prior-work overlap a human reviewer should weigh for two reviewer-judgment signals
— **trivial combination** ("standard A+B+C") and **duplicate publication** ("repackaged prior
work"). Retrieve candidates, map them side-by-side against the paper's ledger-anchored
contribution, and emit `novelty-duplication-advisory.memo.md`. Run AFTER `/evidence-ledger`
(so `claims.json` exists). This skill **decides nothing** — it never rules "trivial" or
"duplicate", and the deterministic adjudicator caps it at `info`.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the ledger, the paper or the literature changes.

> Lineage (adapted from ARIS `novelty-check`: reframed to a reviewer-facing brief, downgraded to memo-only),
> why this skill exists, and the full parent comparison: read `reference/rationale.md` when you need the why.


## Core principle

**MEMO-ONLY · retrieve-don't-rule · ledger-anchored on the paper side · real-record-bound on
the prior-work side · cross-model, fresh thread per axis · reviewer ≠ adjudicator · never
rules novelty · absence ≠ originality.** Three honesty spines hold this skill up:

1. **Paper side is ledger-anchored.** The contribution being compared is pulled from
   `claims.json` (`claim_id` + verbatim span) — never re-invented from the raw PDF
   (`references/integrity-forensics-contract.md` rule 1). The paper's **title** may be read
   from the source *as a search seed only* — it is never used as an anchor.
2. **Prior-work side is real-record-bound.** Every candidate comes from a **real retrieval
   call** (DBLP / WebSearch / WebFetch) and carries a **verifiable identifier** (arXiv id /
   DOI / DBLP url). Nothing is recalled "from memory" — fabricating a prior paper here is the
   same sin as a hallucinated citation (mirrors ARIS `novelty-check`'s anti-hallucination rule
   and `citation-discipline`).
3. **No verdict — by design.** The cross-model reviewers **propose** an overlap map + the open
   questions; they are forbidden to conclude "trivial" or "duplicate." The executor
   **validates** anchors; `tools/adjudicate_findings.py` **owns the verdict** and caps this
   skill at `info` (`references/reviewer-independence.md` Layer 2). A retrieval that finds
   nothing is a valid output that says **nothing** about novelty — "no candidate overlap
   found" is not "the paper is original."

> Two design notes (the deliberate external-corpus exception to "the reviewer reads only the ledger"; why the anchor is
> the contribution sentence, never the prior work) are in `reference/rationale.md`; read them before changing the anchor rules.

## Routing (summary)

This skill owns only the two advisory overlap signals (`ADV-TRIVIAL-COMBINATION`, `ADV-DUPLICATE-PUBLICATION`), and only surfaces them.
Cited-reference existence/context → `citation-forensics`; "SOTA / first / beats prior work" → `baseline-comparison-audit`;
internal scope-overclaim → `consistency-audit` (`HP-SCOPE-INFLATE`). Read `reference/routing.md` when unsure which auditor owns a
finding (full comparison table, ARIS `novelty-check` table, and the when-not-to-use list).

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL       = gpt-5.5                # different family from the executor (Claude)
REVIEWER_REASONING   = xhigh                  # always; effort never lowers reviewer quality
REVIEWER_SANDBOX     = read-only              # detect-only; never mutate the paper
REVIEWER_CWD         = <paper-dir>            # so it reads claims.json + candidates.json from cwd
THREAD_POLICY        = TWO fresh mcp__codex__codex calls — ONE per axis (duplicate / combination);
                       NEVER mcp__codex__codex-reply across them (the per-dimension bias guard)
CONCURRENCY          = serial                 # Codex MCP hangs on concurrent calls — Thread 2 waits for Thread 1
AXES                 = duplicate (ADV-DUPLICATE-PUBLICATION) | combination (ADV-TRIVIAL-COMBINATION)
OBS_REQUIRED         = 0 for both             # decidable-as-advisory from text + the public corpus (no repo/results)
RETRIEVAL_SOURCES    = DBLP (fuzzy_title_search + boolean search) · WebSearch · WebFetch (abstracts)
ANTI_HALLUCINATION   = every candidate comes from a REAL retrieval call + carries a verifiable id +
                       is a record in candidates.json; the reviewer cites candidate_id ONLY (never "from memory")
ANCHOR_UNIVERSE      = contribution claims = type∈{scope,method,comparison} OR section∈{abstract,intro,introduction};
                       prior work goes in the memo/description, NOT the anchor span
DISPOSITION          = candidate_overlap_surfaced | no_candidate_overlap_found | retrieval_incomplete
                       (INFORMATIONAL, NOT a verdict; "no overlap found" ≠ "the paper is original")
ADVISORY_PATTERNS    = ADV-TRIVIAL-COMBINATION · ADV-DUPLICATE-PUBLICATION   (zero verdict weight)
TAXONOMY_VERSION     = 0.5                     # references/hack-pattern-taxonomy.md
MEMO_FILE            = novelty-duplication-advisory.memo.md            # canonical human-facing output
FINDINGS_FILE        = novelty-duplication-advisory.findings.json      # info-only mirror (or []); globbed, capped at info
PROFILE_FILE         = novelty-duplication-advisory.profile.json       # executor-built retrieval profile (from the ledger)
CANDIDATES_FILE      = novelty-duplication-advisory.candidates.json    # retrieved prior work (REAL records only)
TRACE_POLICY         = forensic (never silently dropped)
TRACE_DIR            = .aris/traces/novelty-duplication-advisory/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** owns the **retrieval** and **none of the judgment**: it pulls the
  contribution spans from the ledger, reads the title from the source as a search seed, runs
  the external searches, assembles a structured `candidates.json` of **real returned records**,
  passes **the ledger + the candidates file + the per-axis checklist** to each reviewer,
  validates every anchor the reviewers return, and renders the memo. It never summarizes the
  paper, pre-judges overlap, or leaks an opinion into a prompt
  (`references/reviewer-independence.md`).
- **Reviewer (codex / gpt-5.5, xhigh, read-only)** reads `claims.json` + `candidates.json`
  from its `cwd`, lays each candidate beside the contribution span it overlaps with, and lists
  the open questions. It is the overlap-mapper, **not** the judge — and it is **forbidden** to
  output a "trivial" / "duplicate" / "not novel" verdict. It cites only `candidate_id`s that
  exist in `candidates.json`.
- **Two fresh threads, serial, no `codex-reply`.** The duplicate axis and the combination axis
  are independent `mcp__codex__codex` calls; never carry one axis's conclusion into the other
  (the per-dimension bias guard). `codex-reply` is intentionally absent from `allowed-tools`.
- **Detect-only.** No `Edit` in `allowed-tools`; the reviewer sandbox is `read-only`. This
  skill never touches the audited paper.

---

## Step 0 — Preconditions: locate the ledger, read the run level, open the trace

This skill reasons over the **ledger** (paper side) + **retrieved candidates** (prior-work
side) — never the raw PDF for structure. Resolve the ledger and read the observability level
**L**, `paper_id`, and the count of contribution claims (each Bash block is self-contained —
shell state does not persist between calls, so re-derive paths every step):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
# $ARGUMENTS is a paper-dir OR a claims.json path:
LEDGER="$ARGUMENTS"; [ -d "$LEDGER" ] && LEDGER="$LEDGER/claims.json"
# Only the NO-ARGUMENT case defaults to the CWD ledger. An EXPLICIT argument that
# resolves to a missing claims.json must NOT silently fall back to $(pwd) — that could
# advise on the wrong paper; let the NO_LEDGER check below fire instead.
[ -z "$ARGUMENTS" ] && LEDGER="$(pwd)/claims.json"
python3 - "$LEDGER" <<'PY'
import json, sys, os
p = sys.argv[1]
if not os.path.isfile(p):
    sys.exit("NO_LEDGER: claims.json not found. Run /evidence-ledger FIRST "
             "(it writes artifact_manifest.json + claims.json).")
d = json.load(open(p, encoding="utf-8"))
CONTRIB_TYPES = {"scope", "method", "comparison"}
CONTRIB_SECT  = {"abstract", "intro", "introduction"}
def sect(c): return ((c.get("location") or {}).get("section") or "").lower()
contrib = [c for c in d.get("claims", [])
           if c.get("claim_id") and c.get("text_span")
           and (c.get("type") in CONTRIB_TYPES or sect(c) in CONTRIB_SECT)]
print("LEDGER         =", os.path.abspath(p))
print("PAPER_DIR      =", os.path.dirname(os.path.abspath(p)) or ".")
print("PAPER_ID       =", d.get("paper_id", "?"))
print("RUN_LEVEL_L    =", d.get("observability_level", 0))
print("CONTRIB_CLAIMS =", len(contrib), "(scope/method/comparison + abstract/intro — the anchor universe)")
PY
```

**Carry forward** the absolute `LEDGER` / `PAPER_DIR`, plus `L` and `PAPER_ID`, into every step
below.

**Failure / edge handling.**
- **`NO_LEDGER`** → stop and tell the user to run `/evidence-ledger` first. This skill never
  re-reads the raw PDF and invents its own structure (contract rule 1).
- **`CONTRIB_CLAIMS == 0`** → there is no contribution claim to anchor to. Recall scales with
  the ledger: an **L0 PDF-text** ledger extracts mostly number/scope spans, so contribution
  anchoring is thin; the richer abstract/intro spans enter via the **L1 LaTeX** path. Prefer
  re-running `/evidence-ledger` on the LaTeX source. If you cannot, skip the reviewer call,
  write the honest-null memo + an empty findings file directly (Step 4's honest-null snippet),
  and stop. Never invent a contribution claim.
- **Observability level does not gate *whether* this skill runs.** Retrieval needs only the
  title/contribution text, available at L0+. There is no graded verdict to gate — the judgment
  is not decidable at *any* level (it is a human call). The info-only mirror carries
  `observability_level_required: 0`, and the MEMO gate caps it at `info` regardless.

Create the trace directory now (forensic; written before any reviewer/retrieval call):

```bash
PAPER_DIR="<abs PAPER_DIR from Step 0>"
DATE=$(date +%F); N=1
while [ -d "$PAPER_DIR/.aris/traces/novelty-duplication-advisory/${DATE}_run$(printf %02d $N)" ]; do N=$((N+1)); done
TRACE="$PAPER_DIR/.aris/traces/novelty-duplication-advisory/${DATE}_run$(printf %02d $N)"
mkdir -p "$TRACE"; echo "TRACE = $TRACE"   # carry this absolute path into every later step
```

Write `"$TRACE/run.meta.json"` (via **Write**) =
`{"skill":"novelty-duplication-advisory","paper_id":"<PAPER_ID>","run_level_L":<L>,"taxonomy_version":"0.5","retrieval":{"duplicate":"pending","combination":"pending"},"generated_at":"<UTC ISO-8601>"}`.

## Step 1 — Build the retrieval profile from the ledger (executor, deterministic)

Pull the paper's **contribution** (the thing whose novelty a reviewer weighs) straight from the
ledger — `scope` / `method` / `comparison` claims plus anything in the `abstract` / `intro`
sections — and read the **title** from the source as a *search seed*. These spans are the
**paper-side anchors**; the executor never paraphrases them and never invents a contribution
the ledger does not contain.

Run the profile builder verbatim from `reference/profile-script.md` (self-contained bash + python; fill in `LEDGER`).
It writes `novelty-duplication-advisory.profile.json` and prints `PROFILE` / `TITLE` / `CONTRIB` (or `NO_CONTRIB`).


**Sanity gate (before searching).** `title_seed` should look like a paper title and `CONTRIB`
should be > 0 for any normal paper. If a span looks truncated or mis-sectioned, **Read**
`claims.json` and spot-check that contribution `claim_id`'s `text_span` before you build a
query from it — a malformed seed wastes the external-search budget. Never fabricate a title or
a contribution to fill a gap.

**Building the queries (literal terms only).** From `profile.json`:
- **Title (for the duplicate axis).** Use `title_seed` verbatim. It is a **query seed, not an
  anchor** (`title_seed_is_anchor: false`); re-opening a source to quote it is permitted
  because it is a query input, not a finding. If it is `None`, run only the combination axis.
- **Constituent techniques (for the combination axis).** Decompose the contribution into ≤4
  named techniques using **literal terms copied from the contribution spans** (the method
  names, the architecture, the training objective). Do **not** introduce vocabulary the spans
  do not contain — that would manufacture overlap. If the contribution is one atomic method (no
  decomposition into ≥2 known components), the combination axis is **N/A**; say so and run only
  the duplicate axis.

**Failure handling.** `NO_CONTRIB` → write the honest-null memo + empty findings (Step 4
snippet) and stop. A thin ledger may yield a weak query — note that limitation in the memo; do
not pad the query with guessed terms.

## Step 2 — Retrieve candidate prior work (executor; real records only)

The executor runs the searches and assembles `candidates.json`. **This step records FACTS,
never a ruling** — whether a candidate is "the same paper", a benign extended version, or
unrelated is the reviewer's lay-out (Step 3) and ultimately the human's call. **Every record
must come from a real call below and carry a verifiable identifier.** Never add a paper you
"remember."

**2a — Duplicate axis (DBLP fuzzy title + exact-phrase web).** A near-identical title / DOI to
a *different* paper is the strongest reportable duplicate-candidate (taxonomy: *"an exact
title/abstract/DOI match is reportable"*). Call DBLP with the profile title:

```
mcp__mcp-dblp__fuzzy_title_search:
  title: "<title_seed from profile.json>"
  similarity_threshold: 0.7
  max_results: 10
  include_bibtex: false
```

Then a web pass for an exact-phrase / preprint match (DBLP indexes venues, not all preprints):

```
WebSearch:
  query: "\"<the exact paper title>\""          # quoted: catch a repackaged/duplicate posting
WebSearch:
  query: "<paper title, unquoted> arxiv"        # catch a near-duplicate preprint
```

For the top title-similar hits (and any exact web hit), `WebFetch` the abstract to record a
snippet for the side-by-side (the abstract is what lets the reviewer judge *degree* of
overlap):

```
WebFetch:
  url: "<arxiv abs / DOI / DBLP ee url of the candidate>"
  prompt: "Return ONLY: the paper title, the author list, the venue+year, and the verbatim
           first 2-3 sentences of the abstract. No commentary."
```

**2b — Combination axis (per-technique prior work).** For each constituent technique from Step
1, find the canonical prior work that *establishes* it — the work a reviewer would cite to call
it "well-known." Use DBLP boolean search (terms joined by `and`; **parentheses are
unsupported**) and/or WebSearch:

```
mcp__mcp-dblp__search:
  query: "<technique-A literal terms> and <technique-A qualifier>"
  max_results: 8
  year_from: 2015
mcp__mcp-dblp__search:
  query: "<technique-B literal terms> and <technique-B qualifier>"
  max_results: 8
WebSearch:
  query: "<technique-C literal terms> method  (survey OR original)"
```

Record the 1–2 most representative prior works per technique. The goal is to lay out *"the
contribution = A [prior work] + B [prior work] + C [prior work]"* for the human — **not** to
conclude the staple is trivial.

**2c — Assemble + validate `candidates.json`.** Use **Write** to create
`<PAPER_DIR>/novelty-duplication-advisory.candidates.json` from the **actual returned records**
— one object per candidate, exactly these keys:

```json
[
  {
    "candidate_id": "K01",
    "source": "dblp_fuzzy_title | dblp_boolean | websearch | webfetch",
    "title": "<verbatim returned title>",
    "authors": ["<as returned, if available>"],
    "venue": "<as returned>",
    "year": 2024,
    "identifier": {"arxiv": "", "doi": "", "dblp_url": "", "url": "<at least ONE non-empty>"},
    "title_similarity": 0.83,
    "abstract_snippet": "<verbatim from WebFetch, if fetched>",
    "retrieved_for": "duplicate | combination:A | combination:B | combination:C",
    "query": "<the exact query string used>"
  }
]
```

Then run the validation + self-record gate (de-dups by identifier, flags the paper's own record
so it is never mis-reported as a duplicate, and refuses memory-sourced entries):

Run the gate verbatim from `reference/candidates-gate-script.md` (fill in `PAPER_DIR`). It prints the kept/dropped
counts, or `CANDIDATES_PARSE_FAILED` / `NO_CANDIDATES`.


`candidates.json` lives in `PAPER_DIR` so each reviewer reads it from its `cwd`. When done,
update `"$TRACE/run.meta.json"` `retrieval` to record per-axis status (`"done"` /
`"unavailable"`). **Failure handling.** `CANDIDATES_PARSE_FAILED` → the assembled JSON is
malformed; rebuild it from the real returned records (never hand-fabricate). `NO_CANDIDATES` →
skip Step 3, go to Step 4's honest-null path. If a DBLP/web tool errors or web access is
unavailable for a whole axis, set that axis to `"unavailable"` in `run.meta.json` → the run
becomes `retrieval_incomplete` (Step 4), and the memo will say the search could not be
completed and therefore concludes **nothing** about originality. Do **not** backfill from
memory.

## Step 3 — Cross-model overlap mapping (TWO fresh per-axis threads; never rules)

Issue **two fresh** `mcp__codex__codex` calls — **one per axis, serial** (Codex MCP hangs on
concurrent calls; never `codex-reply`, never carry one axis into the other). Each reviewer reads
`claims.json` + `candidates.json` from its `cwd` and lays out overlap. Each is told —
repeatedly — that it must **not** conclude "trivial" or "duplicate."

### Thread 1 — duplicate axis (tag `001`)

Send the Thread 1 call verbatim from `reference/reviewer-prompts.md` (section Thread 1), filling `cwd` and `L`.


### Thread 2 — combination axis (tag `002`, a SECOND fresh thread)

Send the Thread 2 call verbatim from `reference/reviewer-prompts.md` (section Thread 2), filling `cwd` and `L`.


**Persist immediately, then run the next thread.** After EACH call returns, save the FULL raw
reply with **Write** to `"$TRACE/<NNN>-<axis>.response.md"` (`001-duplicate.response.md`,
`002-combination.response.md`), the exact prompt to `"$TRACE/<NNN>-<axis>.request.json"`, and
`"$TRACE/<NNN>-<axis>.meta.json"`
(`{"model":"gpt-5.5","reasoning":"xhigh","sandbox":"read-only","thread_id":"<id>"}`). The
`.response.md` files are the immutable input to Step 4. Keep each `thread_id`.

**Failure handling.**
- *MCP stall / hang* (common in long sessions): re-invoke the **identical** prompt as a
  **fresh** `mcp__codex__codex` call (gpt-5.5, xhigh) — never `codex-reply`.
- *Returns prose, not a JSON array*: Step 4 extracts the outermost `[...]`; if there is none,
  re-ask that one axis with "Output ONLY the JSON array, nothing else." Never hand-author
  overlap items on the reviewer's behalf.
- *Reviewer slips in a verdict* ("this is trivial / a duplicate"): that text is advisory memo
  content only; Step 4 strips leaked ruling words and the adjudicator caps the skill at `info`.
  Do not propagate it as a conclusion.
- *(Optional fan-out, `— effort: max`)*: read `reference/reviewer-prompts.md` (Optional fan-out) before running per-component probes.

## Step 4 — Validate + anchor, render the memo + the info-only findings mirror

Everything the reviewers proposed is now **validated deterministically** by the executor: every
**anchor** must be a verbatim span of a real ledger contribution claim, and every
**candidate_id** must exist in `candidates.json` (the anti-hallucination gate — a candidate the
file does not contain is *deleted*, so the memo can never name a prior-work paper that was not
actually retrieved; a self-record cannot appear on the duplicate axis). Leaked ruling words are
neutralized. The adjudicator independently re-applies the span-anchor gate and the MEMO cap as
the authoritative verdict, so this memo can never out-rank it. This single command writes both
deliverables:

Run the validator/renderer verbatim from `reference/validate-render-script.md` (fill in `PAPER_DIR` and `TRACE`). It
prints the disposition and writes `novelty-duplication-advisory.memo.md` + `novelty-duplication-advisory.findings.json`.


Read `reference/validate-render-script.md` (Scope of this gate) for exactly what the gate checks; it computes no verdict.

**CONTRIB_CLAIMS == 0 / NO_CONTRIB / NO_CANDIDATES — honest-null path.** When Step 0/1/2 sent
you here, write the two files directly (no reviewer call) so the orchestrator's globs still find
them:

```bash
PAPER_DIR="<abs PAPER_DIR from Step 0>"
printf '[]\n' > "$PAPER_DIR/novelty-duplication-advisory.findings.json"
# then Write novelty-duplication-advisory.memo.md stating: retrieval found no candidate
# overlap (or the ledger had no contribution to query); disposition=no_candidate_overlap_found;
# and — explicitly — that this is NOT evidence of originality.
```

**Always emit.** Write `novelty-duplication-advisory.findings.json` even when it is `[]` —
**silent skip is forbidden**; the orchestrator and the standalone adjudicate command both expect
the file at a predictable path. **Failure handling.** *All candidates dropped as hallucinated
AND the reviewer made strong overlap claims* → the reviewer cited prior work not in the file;
re-run that axis's Step 3 once (it must cite only `candidates.json` ids). Do **not** ship a memo
naming a paper that was never retrieved. *Empty items + complete retrieval* →
`no_candidate_overlap_found` (a correct output; do not re-run to manufacture overlap). *Lookups
unavailable* → `retrieval_incomplete` (concludes nothing).

## Step 5 — Trace (forensic; never silently dropped)

The trace dir from Step 0 must, after the run, contain both reviewer calls and the retrieval
inputs (this repo ships no `save_trace.sh`, so write the files directly with **Write**):

```
.aris/traces/novelty-duplication-advisory/<date>_run<NN>/
  run.meta.json                       # {skill, paper_id, run_level_L, taxonomy_version, retrieval{duplicate,combination}, disposition, generated_at}
  001-duplicate.request.json          # the EXACT prompt + paths sent (ledger + candidates + checklist — the independence audit trail)
  001-duplicate.response.md           # the FULL raw reviewer array (input to Step 4)
  001-duplicate.meta.json             # {model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}
  002-combination.request.json        # the EXACT prompt sent
  002-combination.response.md         # the FULL raw reviewer array
  002-combination.meta.json
```

The retrieval artifacts `novelty-duplication-advisory.profile.json` and
`novelty-duplication-advisory.candidates.json` live in `PAPER_DIR` (so each reviewer reads
`candidates.json` from its `cwd`); `run.meta.json` references both and records the per-axis
retrieval status. Each `request.json` must show the executor sent only **paths + the ledger +
the candidates + the per-axis checklist** — never a Claude-authored digest or hunch like "this
looks derivative" (reviewer-independence). The `response.md` files are the immutable inputs Step
4 consumes.

## Step 6 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here.** The orchestrator globs every `*.findings.json` —
your info-only `novelty-duplication-advisory.findings.json` included, which the MEMO gate caps
at `info` — so the skill's presence reliably reaches the report without raising the verdict. The
canonical human-facing artifact is `novelty-duplication-advisory.memo.md` in `PAPER_DIR`,
surfaced to the human **alongside** `REPORT.md` as a standalone advisory. (The adjudicator's
single `--memo` slot carries the `adversarial-case-builder` memo; this advisory is presented
directly, not through `--memo`.)

Running this skill **alone** is fine — `--ledger` is **required** (it anchors every above-info
finding; without it everything fails closed to `info`). Adjudicating confirms the
no-verdict-weight property:

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
PAPER_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["paper_id"])' "$LEDGER")
L=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["observability_level"])' "$LEDGER")
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D"/*.findings.json \
    --ledger "$LEDGER" \
    --paper-id "$PAPER_ID" --observability-level "$L" --taxonomy-version 0.5 \
    --out "$D/report.json" --md "$D/REPORT.md"
```

A standalone run with no other findings yields `CLEAN_GIVEN_EVIDENCE` by design; read `reference/rationale.md` for the gate order and why. Read the memo.

## Output contract

This skill **always** writes, into the ledger's directory (`PAPER_DIR`):

- `novelty-duplication-advisory.memo.md` — **canonical.** Core overlap brief per axis
  (`ADV-DUPLICATE-PUBLICATION` candidate table + `ADV-TRIVIAL-COMBINATION` decomposition), the
  mandatory *absence-≠-originality* caveat, the self-overlap caveat, the informational
  disposition, and the retrieval/anchoring audit. Carries no verdict weight; surfaced to the
  human alongside `REPORT.md`. Prints **no** novelty score and **no** trivial/duplicate verdict.
- `novelty-duplication-advisory.findings.json` — **info-only** mirror (one entry per surfaced
  overlap item; possibly `[]`), conforming to `schemas/finding.schema.json`,
  `"skill":"novelty-duplication-advisory"`, `pattern_id` ∈ {ADV-DUPLICATE-PUBLICATION,
  ADV-TRIVIAL-COMBINATION}, every entry `severity:"info"`,
  `verdict_local:"needs_external_check"`, `observability_level_required:0`. Written even when
  empty for predictable `*.findings.json` globbing; the MEMO gate makes it a no-op.
- `novelty-duplication-advisory.candidates.json` — the retrieved prior work (real records, with
  identifiers; self-records flagged). Each reviewer's prior-work universe; forensic.
- `novelty-duplication-advisory.profile.json` — the ledger-derived retrieval profile.
- `.aris/traces/novelty-duplication-advisory/<date>_run<NN>/` — the two raw reviewer calls.

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come only from
`tools/adjudicate_findings.py` (Step 6 / the orchestrator).

## Key rules

- **Never rules novelty — by design.** The skill never outputs "trivial", "not novel",
  "duplicate", a novelty score, or a recommendation. It surfaces overlap and questions; the
  human judges; the adjudicator's `MEMO_ONLY_SKILLS` cap pins it to `info` and it is absent from
  `SKILL_TO_DIMENSION`. Leaked ruling words are neutralized in Step 4.
- **Absence ≠ originality.** "No candidate overlap found" / "retrieval incomplete" is a valid
  result that says **nothing** about novelty — the corpus is incomplete by construction. The
  memo states this explicitly; never let an empty retrieval read as "the paper is novel."
- **Prior-work side real-record-bound (anti-hallucination).** Every candidate comes from a real
  DBLP/WebSearch/WebFetch call and carries a verifiable identifier; the reviewer cites only
  `candidate_id`s in `candidates.json`. A fabricated prior paper is the same sin as a
  hallucinated citation — forbidden, and dropped in Step 4.
- **Paper side ledger-anchored.** Every contribution reference cites a contribution `claim_id`
  (type∈{scope,method,comparison} or section∈{abstract,intro}) + a verbatim span (`span in
  text_span`, whitespace-normalized, never the reverse; LaTeX escapes quoted exactly). The
  candidate goes in the table / `description`, never in the span. No anchor → dropped.
- **The title is a seed, not an anchor.** `\title{…}` (or the PDF's first line) seeds the
  duplicate search; it anchors nothing (`title_seed_is_anchor: false`). A duplicate overlap
  anchors to a contribution `claim_id`.
- **Exclude the paper's own record.** A near-identical title flagged `self_record_suspected` is
  the audited paper's own preprint/venue copy, not a duplicate; it is excluded from the
  duplicate axis (flagged, never silently dropped). Self-overlap (arXiv→venue,
  workshop→conference, extended journal) is legitimate, never misconduct.
- **Executor retrieves; reviewers map.** WebSearch / DBLP / WebFetch lookups are the executor's
  Step 2; each reviewer lays out overlap over those facts. The executor never pre-judges overlap
  into the prompt — it hands raw retrieved records (structured, not a digest), preserving
  reviewer-independence even though the corpus is external.
- **Cross-model, two fresh serial per-axis threads.** Reviewer is a different family (gpt-5.5
  xhigh, read-only); each axis is a new `mcp__codex__codex` thread, run sequentially;
  `codex-reply` is never used. Reviewer ≠ executor ≠ adjudicator.
- **Hand off external truth it does not own.** A "SOTA/first/beats prior work" claim →
  `baseline-comparison-audit`; a wrong-context/fabricated *cited* work → `citation-forensics`.
  This skill owns only the two advisory overlap signals.
- **L0 advisory framing.** `observability_level_required: 0` for both signals (decidable-as-
  advisory from text + the public corpus). Output asks a reviewer to CHECK/WEIGH, never
  "reject" / "plagiarism" / "the authors faked X." The tool audits overlap, not provenance.
- **Detect-only.** Never edit the audited paper (no `Edit`; reviewer sandbox read-only).
- **Taxonomy is a mapping layer (v0.4).** The two `ADV-*` ids are advisory signals with zero
  verdict weight — set them on the info-only findings, never to claim a decision.
- **Reproducible.** Same ledger + same candidates snapshot + same reviewer outputs → same
  validated memo + same disposition.


## Review tracing

Forensic, never skipped; the layout is in Step 5. Read `reference/rationale.md` (Review tracing) for the request.json audit-trail requirements.
