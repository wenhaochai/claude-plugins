---
name: citation-forensics
description: "Checks each cited reference against DBLP/arXiv/DOI: exists, metadata right, not retracted, supports the citing sentence. Run after evidence-ledger on LaTeX source; a PDF-only ledger has no citations. Triggers: \"check the references\", \"verify references\", \"hallucinated citations\", \"wrong-context citation\", \"引用核对\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, Grep, Glob, WebSearch, WebFetch, mcp__codex__codex, mcp__mcp-dblp__search, mcp__mcp-dblp__fuzzy_title_search, mcp__mcp-dblp__get_venue_info
---

# Citation Forensics — are the references real and honestly used?

Audit citation integrity for: **$ARGUMENTS** (requires `claims.json` from
`/evidence-ledger`; reasons over its `type:"citation"` claims). Emit span-anchored
`citation-forensics.findings.json`. This skill computes **no verdict**.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the paper, the ledger or the bibliography changes (bibliography finalized → ledger rebuilt → audit once).

Read `reference/rationale.md` for the ARIS `citation-audit` lineage and the failure modes this skill exists to catch.

## Core principle

**Ledger-anchored, span-verified, canonical-fact-checked-or-handed-off,
reviewer≠adjudicator, detect-only.**

1. The cite keys and the **citing sentences** come from the deterministic ledger
   (`claims.json`, `type:"citation"`), never from re-reading the PDF.
2. The executor assembles a neutral per-key **dossier** (citing spans + the claimed
   `.bib` metadata) and gathers a reproducible **resolution snapshot** of the
   canonical record (DBLP / arXiv / DOI). It gathers **facts, never a judgment** —
   whether a mismatch is fabrication, a typo, or a preprint→venue migration is the
   reviewer's call.
3. A **fresh cross-model reviewer** (gpt-5.5 xhigh, one thread per cited key)
   *proposes* findings, judging existence + metadata + context over those facts.
4. **Every above-info finding cites a ledger `claim_id` + a verbatim span** of the
   **citing sentence** (`references/integrity-forensics-contract.md` rules 1–2). The
   bib entry, the canonical record, and any URL live in the finding's `description`,
   never as the anchor span.
5. The model **proposes**; `tools/adjudicate_findings.py` **decides**
   (`references/reviewer-independence.md` Layer 2). This skill emits findings only.
6. **Fact-or-hand-off honesty.** Existence/metadata MUST be settled against a real
   source (snapshot record + URL in `description`). Cannot settle → `verdict_local:
   needs_external_check` — **never** a guessed "fabricated". A false hallucination
   flag is a serious error.

> **The anchor is the citing sentence, not the bib line.** `tools/build_claim_ledger.py`
> puts `type:"citation"` claims in the ledger whose `text_span` is the *sentence that
> contains `\cite{key}`* and whose `refs` are the cite keys — it does **not** parse
> the `.bib`. So a citation finding always anchors to that citing sentence (quote a
> verbatim substring of it, e.g. `\cite{smith2024bar}` or the surrounding phrase).
> What the `.bib` claims and what DBLP/arXiv actually return go in `description` —
> there is no ledger claim for the `.bib` line to anchor to. A bib key that is in the
> `.bib` but never `\cite`d has no citation claim, cannot be anchored, and is
> therefore **out of scope** (detect-only; not flagged).

## How this differs from the other auditors (route correctly)

This skill judges only whether the cited work exists, is described correctly, and supports the citing sentence. Numeric self-contradiction / method drift → `consistency-audit`; empirical "SOTA/first" → `baseline-comparison-audit` (`needs_external_check`); code/result fraud → `experiment-forensics` (L2); prose surface → `presentation-signals`.
Read `reference/routing.md` for the full auditor table and hand-off list.

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL       = gpt-5.5                  # different family from executor (Claude)
REVIEWER_REASONING   = xhigh                    # always; effort never lowers reviewer quality
REVIEWER_SANDBOX     = read-only                # detect-only; never mutate the paper or .bib
REVIEWER_CWD         = <PAPER_DIR>              # so it can re-open claims.json + the .bib to confirm a span
THREAD_POLICY        = ONE fresh mcp__codex__codex per CITED KEY; NEVER mcp__codex__codex-reply across keys
TAXONOMY_VERSION     = 0.5                      # references/hack-pattern-taxonomy.md §E
PATTERNS             = HP-CITE-HALLUC (existence/metadata) | HP-CITE-CONTEXT (wrong context) | HP-CITE-RETRACTED (retracted/withdrawn)
OBS_REQUIRED         = 0 for all three patterns # decidable at L0 (text + canonical / retraction sources)
FACT_GATHERING       = executor, Step 2: DBLP MCP + WebSearch/WebFetch -> resolution.json (FACTS, never a verdict)
DOSSIER              = <PAPER_DIR>/.aris/citation-forensics/dossier.json      # Step 1 (rehashable; NOT /tmp)
RESOLUTION           = <PAPER_DIR>/.aris/citation-forensics/resolution.json   # Step 2 (rehashable; NOT /tmp)
FINDINGS             = <PAPER_DIR>/citation-forensics.findings.json           # Step 4 output
TRACE_POLICY         = forensic (never silently dropped)
TRACE_DIR            = <PAPER_DIR>/.aris/traces/citation-forensics/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** builds none of the judgment: it pulls the citation claims
  from the ledger, assembles the per-key dossier, gathers the canonical resolution
  facts, validates the reviewer's spans, and writes the findings file. It never
  summarizes the paper, pre-judges "this reference is fake", or leaks an opinion into
  the prompt — only structured inputs (the dossier + the neutral resolution snapshot
  + the checklist). (`reviewer-independence.md` Layer 1.)
- **Reviewer (codex / gpt-5.5)** judges existence + metadata + context per key over
  the executor's facts and self-reports `false_positive_risk`. It is the
  evidence-weigher, not the judge. Like the other auditors it runs
  `config: {"model_reasoning_effort": "xhigh"}`, `sandbox: read-only`; the lookups
  are the executor's job (Step 2), not the reviewer's.
- **Fresh thread per cited key.** `codex-reply` is intentionally absent from
  `allowed-tools`; never carry one key's conclusion into another (the bias guard).
- **Detect-only.** No `Edit` in `allowed-tools` — this skill never rewrites the
  `.bib` or any `.tex` (that is ARIS `citation-audit`'s job, not a forensics tool's).

---

## Step 0 — Preconditions: locate the ledger, read the level, find the bib, set the run dir

The ledger is the **only** structure this skill reasons over. Resolve it and read the
run's observability level **L**, `paper_id`, the set of cited keys, and the
bibliography path(s) (each Bash block is self-contained — shell state does not
persist, so re-derive paths every time):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
# $ARGUMENTS is a paper-dir OR a claims.json path:
LEDGER="$ARGUMENTS"; [ -d "$LEDGER" ] && LEDGER="$LEDGER/claims.json"
# Only the NO-ARGUMENT case defaults to the CWD ledger. An EXPLICIT argument that
# resolves to a missing claims.json must NOT silently fall back to $(pwd) — that
# could audit the wrong paper; let the NO_LEDGER check below fire instead.
[ -z "$ARGUMENTS" ] && LEDGER="$(pwd)/claims.json"
python3 - "$LEDGER" <<'PY'
import json, sys, os, glob
p = sys.argv[1]
if not os.path.isfile(p):
    sys.exit("NO_LEDGER: claims.json not found. Run /evidence-ledger FIRST "
             "(it writes artifact_manifest.json + claims.json).")
d = json.load(open(p, encoding="utf-8"))
paper_dir = os.path.dirname(os.path.abspath(p)) or "."
cites = [c for c in d.get("claims", []) if c.get("type") == "citation"]
keys  = sorted({k for c in cites for k in (c.get("refs") or [])})
bibs  = glob.glob(os.path.join(paper_dir, "**", "*.bib"), recursive=True)
print("LEDGER      =", os.path.abspath(p))
print("PAPER_DIR   =", paper_dir)
print("PAPER_ID    =", d.get("paper_id", "?"))
print("RUN_LEVEL_L =", d.get("observability_level", 0))
print("CITE_CLAIMS =", len(cites))
print("CITE_KEYS   =", len(keys), keys)
print("BIB_FILES   =", bibs or "NONE (metadata layer will be partial)")
PY
```

Then create the run directories (start `NN` at `01`, bump if it exists):

```bash
PAPER_DIR="<PAPER_DIR printed above>"
DATE=$(date -u +%Y-%m-%d)
TBASE="$PAPER_DIR/.aris/traces/citation-forensics"
NN=01; while [ -d "$TBASE/${DATE}_run$NN" ]; do NN=$(printf '%02d' $((10#$NN + 1))); done
RUN="${DATE}_run$NN"
mkdir -p "$TBASE/$RUN" "$PAPER_DIR/.aris/citation-forensics"
echo "RUN        = $RUN"
echo "TRACE_DIR  = $TBASE/$RUN"
echo "DOSSIER    = $PAPER_DIR/.aris/citation-forensics/dossier.json"
echo "RESOLUTION = $PAPER_DIR/.aris/citation-forensics/resolution.json"
echo "FINDINGS   = $PAPER_DIR/citation-forensics.findings.json"
```

**Failure / edge handling.**
- `NO_LEDGER` → **stop**; tell the user to run `/evidence-ledger` first. This skill
  never re-reads the raw PDF and invents structure (contract rule 1).
- `CITE_CLAIMS = 0` → the ledger has no `type:"citation"` claims. This is expected on
  an **L0 PDF-text-only** run: `extract_from_text` in `tools/build_claim_ledger.py`
  extracts numbers + scope language but **not** citations (only the LaTeX path
  `extract_from_latex` emits `citation` claims). Skip to Step 4, write
  `citation-forensics.findings.json` = `[]`, and note: *"no citation claims in ledger
  — re-run /evidence-ledger with the LaTeX source, or the paper has no `\cite`."*
  **Silent skip is forbidden** — the file must exist.
- `BIB_FILES = NONE` (or only a `.bbl`) → continue. The citing sentences still anchor
  the audit, and existence + context are checkable from the cite key + the sentence +
  canonical sources. The **metadata** layer is then partial (no claimed
  authors/year/venue to compare) — say so in the dossier and tell the reviewer the
  bib entry is unavailable for that key. That is honest, not a failure.

Carry the absolute `LEDGER`, `PAPER_DIR`, `PAPER_ID`, `L`, `RUN`, `TRACE_DIR`,
`DOSSIER`, and `RESOLUTION` paths into the steps below.

## Step 1 — Build the per-key citation dossier (deterministic; no judgment)

Group every `type:"citation"` claim by cite key (a `\cite{a,b}` claim contributes to
both `a` and `b`) and, best-effort, attach the **claimed** `.bib` metadata for each
key by balanced-brace extraction from any `*.bib` under the paper dir. Pure assembly —
no web, no opinion. Stage it under `.aris/` so the verifier can rehash it (never
`/tmp`):

```bash
LEDGER="<abs LEDGER>"; PAPER_DIR="<abs PAPER_DIR>"
OUT="$PAPER_DIR/.aris/citation-forensics/dossier.json"
python3 - "$LEDGER" "$PAPER_DIR" "$OUT" <<'PY'
import json, os, re, sys, glob
ledger_path, paper_dir, out = sys.argv[1], sys.argv[2], sys.argv[3]
L = json.load(open(ledger_path, encoding="utf-8"))
cites = [c for c in L.get("claims", []) if c.get("type") == "citation"]

# 1) group citing spans by cite key
keys = {}
for c in cites:
    for k in (c.get("refs") or []):
        keys.setdefault(k, []).append({
            "claim_id": c["claim_id"],
            "span":     c.get("text_span", ""),
            "location": c.get("location", {}),
        })

# 2) best-effort: parse claimed metadata per key from any .bib (balanced-brace)
bibtext, bibfiles = "", []
for p in glob.glob(os.path.join(paper_dir, "**", "*.bib"), recursive=True):
    try:                                         # best-effort: skip an unreadable .bib
        txt = open(p, encoding="utf-8", errors="replace").read()
    except OSError:
        continue
    bibfiles.append(p)
    bibtext += txt + "\n"

def bib_entry(key):                          # @type{key, ... } with brace matching
    m = re.search(r"@\w+\s*\{\s*" + re.escape(key) + r"\s*,", bibtext)
    if not m:
        return None
    i, depth = m.end(), 1
    while i < len(bibtext) and depth:
        depth += (bibtext[i] == "{") - (bibtext[i] == "}")
        i += 1
    return bibtext[m.start():i][:1200]

entries = [{"key": k, "n_cites": len(keys[k]),
            "bib_entry": bib_entry(k), "citing": keys[k]} for k in sorted(keys)]
os.makedirs(os.path.dirname(out), exist_ok=True)
json.dump({"n_keys": len(entries), "bib_files": bibfiles, "entries": entries},
          open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
missing = [e["key"] for e in entries if not e["bib_entry"]]
print(f"dossier: {len(entries)} cited keys from {len(cites)} citation claims; "
      f"bib_files={bibfiles or 'NONE'}; no-bib-entry keys={missing} -> {out}")
PY
```

**Gate — sanity.** The printed `cited keys` count should match what you expect for
the paper. `0` keys with `CITE_CLAIMS > 0` (rare) means the `refs` were empty —
spot-read a citation claim in `claims.json`. Keys flagged `no-bib-entry` (no `.bib`,
or the key missing from it) are audited **existence + context only** — the metadata
layer is partial because there is no claimed authors/year/venue to compare. That is
honest; the reviewer infers the intended work from the cite key + the citing
sentences.

## Step 2 — Canonical-source resolution (executor gathers FACTS; non-blocking)

For each cited key, gather a **reproducible snapshot** of what the canonical record
actually is — so a finding is reproducible against staged facts even if DBLP changes
later, and so the reviewer has the evidence it needs to judge. **This step records
facts, never a verdict**: whether a mismatch is fabrication, a typo, or a
preprint→venue migration is the reviewer's call in Step 3. (Same executor-gathers /
reviewer-weighs division as `baseline-comparison-audit` Step 2.)

For each key, seed the queries from the dossier's bib title / authors / venue. If
`bib_entry` is null (no `.bib`, or only a `.bbl`), seed instead from the cite-key
tokens (author / year / keyword) plus distinctive words from that key's citing
sentence(s) in the dossier — existence + context stay checkable; the metadata layer is
then partial (nothing claimed to compare against), which is honest, not a failure:

- **DBLP fuzzy title** — `mcp__mcp-dblp__fuzzy_title_search` with `title=<bib title>`,
  `similarity_threshold=0.7` (lower to ~0.5 only if no hit). Returns canonical
  `{title, authors, venue, year, doi, ee, url}` for the top matches.
- **DBLP boolean cross-check** — `mcp__mcp-dblp__search` with
  `query="<first-author surname> and <distinctive title word>"` (the query supports
  only `and`/`or`, **no parentheses**). Confirms author↔title↔year coherence;
  `venue_filter` / `year_from` / `year_to` narrow it.
- **Venue exists** — `mcp__mcp-dblp__get_venue_info` with `venue_name=<bib venue>` to
  confirm the venue is real and of the claimed `type` (Conference or Workshop /
  Journal / Repository).
- **arXiv / DOI resolve + content** — `WebFetch` the arXiv abstract page built from
  the bib `eprint`/`arxiv` id (`https://arxiv.org/abs/<id>`) and capture the returned
  title + authors **and the abstract text** (the abstract is what lets the reviewer
  judge *context*); `WebFetch https://doi.org/<doi>` to confirm the DOI resolves to
  this work. Use `WebSearch` as a fallback for very recent papers (< ~2 weeks) not yet
  in DBLP.

Write one neutral record per key to the staged snapshot (use `Write`), and copy it
into the trace dir (Step 5):

```json
// .aris/citation-forensics/resolution.json
{
  "smith2024bar": {
    "dblp_fuzzy_top": [{"title": "...", "authors": ["..."], "venue": "...",
                        "year": 2024, "doi": "...", "url": "https://dblp.org/..."}],
    "venue_info": {"venue": "...", "type": "Conference or Workshop"},
    "arxiv": {"id": "2401.01234", "resolves": true, "title_returned": "...",
              "abstract": "... fetched abstract text, for the context layer ..."},
    "doi": {"doi": "10.1145/...", "resolves": true},
    "notes": "facts only — not a verdict"
  }
}
```

**Failure handling (non-blocking).** If a DBLP MCP call errors, or web access is
unavailable, write `{"<key>": {"status": "unavailable", "reason": "..."}}` for that
key and continue — the Step 3 reviewer then falls back to
`verdict_local: needs_external_check` for that key rather than guessing. Note the skip
in the trace. **Never** hand-author a "fabricated" conclusion from a failed lookup.

## Step 3 — Per-entry cross-model audit (existence → metadata → context)

Existence and metadata are mechanical fact-checks against the snapshot; *context*
needs judgment. **Read `dossier.json` + `resolution.json`.** For **each** entry, issue
**one fresh** `mcp__codex__codex` call (key order; tag `001`, `002`, …), `cwd =
PAPER_DIR` so the reviewer can re-open `claims.json` / the `.bib` to confirm a span.
**Inject that one key's dossier record and resolution record** in place of the two
bracketed blocks. Send EXACTLY this — it is the reviewer's complete instruction set;
add no commentary of your own about the paper:

The exact `mcp__codex__codex` call (envelope, layers A–D, hard rules, output schema) is in `reference/reviewer-prompt.md`. Read it and send it verbatim per key, with that key's dossier and resolution records injected.

**Immediately after each call returns**, persist the trace (Step 5) **before** the
next key's call: write the FULL raw reply with `Write` to
`<TRACE_DIR>/<NNN>-<key>.response.md`, the exact prompt sent to
`<NNN>-<key>.request.json`, and `<NNN>-<key>.meta.json`
(`{model, reasoning, sandbox, thread_id}`). The `.response.md` files are the immutable
input to Step 4.

Read `reference/worked-examples.md` for what good findings look like (a major `HP-CITE-CONTEXT`, a critical `HP-CITE-HALLUC`, and the typo / preprint-migration contrast).

**Budget / fan-out.** Default: **one fresh thread per cited key** (the bias guard).
For a long bibliography you MAY group a handful of keys into one fresh
`mcp__codex__codex` call **only if** the prompt keeps each key in its own clearly
labeled block (with its own dossier + resolution records) and emits a flat array of
findings each anchored to its key's citing claim — but **never** use `codex-reply` to
carry one key's conclusion into another.

**Failure handling.**
- *MCP stall / hang* (common in long sessions): re-invoke the **identical** prompt as
  a **fresh** `mcp__codex__codex` call (gpt-5.5, xhigh) — never `codex-reply`.
- *Reviewer returns prose, not a JSON array*: the Step 4 validator extracts the
  outermost `[...]`; if there is none, re-ask that one key with "Output ONLY the JSON
  array, nothing else." Never hand-author findings on the reviewer's behalf.
- *Resolution unavailable for a key*: that is the honest path — expect `info` /
  `needs_external_check` for existence/metadata. Do **not** upgrade them.

## Step 4 — Validate + anchor + emit (the anti-hallucination gate)

**Coverage gate (fail closed).** First confirm Step 3 actually ran: count
`ls "$TRACE_DIR"/*.response.md | wc -l` and require one `.response.md` per cited key
(fewer only if you deliberately batched keys into a shared response — then each
batched key must still appear in some `.response.md`). **Zero response files while
`CITE_CLAIMS > 0` means Step 3 never ran — STOP and run it; do NOT emit a clean `[]`.**
The *only* legitimate empty-findings path is the `CITE_CLAIMS = 0` short-circuit from
Step 0.

Enforce the ANCHOR gate **before** keeping anything — it mirrors the verbatim-span
rule `tools/adjudicate_findings.py` re-applies (so nothing you keep is silently
rejected downstream), **plus** one citation-specific check: a citation finding must
rest on a `type:"citation"` (citing-sentence) claim, not a stray number/scope claim.
This reads every `*.response.md` in the trace dir, applies schema hygiene, merges, and
renumbers. The span must be a verbatim, whitespace-normalized **substring of** the
cited claim (`span in claim`, never `claim in span` — appending hallucinated text to a
real sentence must fail):

Run the validator script in `reference/validate-anchor.md` (set `LEDGER`, `TRACE_DIR`, `OUT` as shown there); it merges every `*.response.md` into `citation-forensics.findings.json`.

Scope of this gate: **anchoring + schema hygiene** — verbatim-span anchoring (the span
must be a substring of a `type:"citation"` claim), enum coercion, non-citation-pattern
rejection, observability fallback, and cross-model provenance — so every kept finding
is well-formed and honestly anchored. It does **not** compute the verdict, the FP-risk
cap, or the observability *downgrade* against the run level; those belong to
`tools/adjudicate_findings.py`, the single decider.

**Always emit.** Write `citation-forensics.findings.json` even when it is `[]` (no
citation claims, or every key clean) — **silent skip is forbidden**; the orchestrator
and the standalone adjudicate command both expect the file at a predictable path. If
the `CITE_CLAIMS = 0` short-circuit from Step 0 fired, simply
`echo '[]' > "<PAPER_DIR>/citation-forensics.findings.json"` here. This skill has no
deterministic-tool pass — there is no `check_citations.py`; existence/metadata require
the live public record, which the executor fetches in Step 2.

**Failure handling.** A bad response file is reported and skipped (treated as `[]`) so
one malformed entry never aborts the merge — re-run that key's Step 3 with the
strict-JSON reminder if you want its findings back. A finding that loses all evidence
is **kept as info**, never silently dropped (the forensic record stays).

## Step 5 — Trace (forensic; never silently dropped)

Save every reviewer call under
`<PAPER_DIR>/.aris/traces/citation-forensics/<YYYY-MM-DD>_run<NN>/`. This repo ships
no `save_trace.sh`, so write the files directly, one set per cited key (mirror ARIS
review-tracing — fresh thread per key, full reply preserved; the `.response.md` is also
the forensic record of what the reviewer concluded over the gathered facts):

```
.aris/traces/citation-forensics/<date>_run<NN>/
  run.meta.json                       # {skill, paper_id, run_level_L, n_keys, generated_at}
  resolution.json                     # the executor's Step 2 canonical-facts snapshot (copy)
  001-<key>.request.json              # the EXACT prompt sent for this key (dossier+resolution+checklist; no paper digest)
  001-<key>.response.md               # the FULL raw reviewer reply (input to Step 4)
  001-<key>.meta.json                 # {model:"gpt-5.5", reasoning:"xhigh", sandbox:"read-only", thread_id}
  002-<key>.request.json ...
```

```bash
TRACE_DIR="<abs TRACE_DIR>"
python3 - "$TRACE_DIR" "<PAPER_ID>" "<L>" "<N_KEYS>" <<'PY'
import json, sys, datetime
d, pid, L, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
json.dump({"skill": "citation-forensics", "paper_id": pid, "run_level_L": L,
           "n_keys": n,
           "generated_at": datetime.datetime.now(datetime.timezone.utc)
                               .isoformat().replace("+00:00", "Z")},
          open(d + "/run.meta.json", "w", encoding="utf-8"), indent=2)
print("wrote", d + "/run.meta.json")
PY
```

Each `request.json` is the independence audit trail — it must show the executor sent
only the **dossier record + the neutral resolution facts + the checklist**, never a
hunch like "this looks AI-generated".

## Step 6 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here**: the orchestrator globs every
`*.findings.json`, runs the adjudicator, and emits `REPORT.md` + `report.json`. When
running this skill **alone**, you may produce the report yourself — `--ledger` is
**required** (it re-verifies each finding quotes a real ledger span; without it every
above-info finding fails closed to `info`):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs LEDGER>"; D="$(dirname "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D/citation-forensics.findings.json" \
    --ledger "$LEDGER" \
    --paper-id "<PAPER_ID>" --observability-level <L> --taxonomy-version 0.5 \
    --out "$D/report.json" --md "$D/REPORT.md"
```

The adjudicator applies, in order: ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE
gates, then computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS,
HARD_FLAGS}. A span-anchored, low-FP **HP-CITE-HALLUC critical** (a reference with no
canonical record) decidable at L0 → **HARD_FLAGS**; a high-FP context flag survives at
most as `minor` → **SOFT_FLAGS**. No model is in the final decision.

## Output contract

This skill **always** writes, into the ledger's directory:

- `citation-forensics.findings.json` — Step 4, a JSON array conforming to
  `schemas/finding.schema.json` (or `[]` when there are no citation claims or all are
  clean — written regardless; **silent skip is forbidden**). Each above-info finding
  carries `evidence[].claim_id` + a verbatim `span` of the citing sentence,
  `pattern_id` ∈ {HP-CITE-HALLUC, HP-CITE-CONTEXT, HP-CITE-RETRACTED}, and
  `observability_level_required: 0`.
- `.aris/citation-forensics/dossier.json` + `resolution.json` — Steps 1–2, the
  rehashable staged inputs (per-key citing spans + claimed bib metadata + canonical
  facts).
- `.aris/traces/citation-forensics/<date>_run<NN>/` — Step 5, the raw per-key reviewer
  calls (`run.meta.json` + `resolution.json` + per-key
  `request.json` / `response.md` / `meta.json`).

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 6 / the orchestrator).

## Key rules

- **The anchor is the citing sentence.** Every above-info finding quotes a verbatim
  substring of a `type:"citation"` claim's `text_span`; the `.bib` line, the
  canonical record, and any URL go in `description` (the ledger has no bib claim to
  anchor to). `span in claim`, whitespace-normalized — never `claim in span`.
- **Executor gathers facts; reviewer weighs them.** DBLP / arXiv / DOI lookups are
  the executor's Step 2 (`resolution.json`); the reviewer judges existence + metadata
  + context over those facts. Same division as `baseline-comparison-audit`.
- **Fact-verify or hand off.** Existence/metadata must be settled against the
  canonical record (cited in `description`). Cannot settle → `needs_external_check`,
  never a guessed "fabricated". A false hallucination flag is a serious error.
- **Don't trust the bib.** A `.bib` entry's metadata is the *claim under audit*, not
  ground truth — verify it against DBLP / arXiv / the publisher.
- **Wrong-context > metadata.** A real paper used to support a claim it never makes is
  more dangerous than a typo'd author — and is the headline value of this skill.
- **L0 only — stay in lane.** `observability_level_required: 0` for all three patterns;
  they are decidable from text + canonical sources, no repo or results. This skill
  never asserts code/result-level fraud (that needs L2 → `experiment-forensics`).
- **Cross-model, one fresh thread per cited key.** Reviewer is a different family
  (gpt-5.5 xhigh); each key is a new `mcp__codex__codex` thread; `codex-reply` is
  never used across keys.
- **Reviewer ≠ adjudicator.** The model proposes findings; `adjudicate_findings.py`
  decides the verdict. This skill emits findings only.
- **Discrepancy, not accusation.** Output asks a reviewer to *check / ask*, never to
  reject; the tool audits citation integrity, not authorship — preprint migrations,
  "see also" framing, and `and others` truncation are honest FPs, not fraud.
- **Uncited bib entries are out of scope** by default — no citation claim to anchor
  to; detect-only, not flagged unless explicitly requested (no budget spent on them).
- **Detect-only.** Never edit the `.bib` or any `.tex` (no `Edit` in `allowed-tools`;
  reviewer sandbox `read-only`). Rewriting citations is ARIS `citation-audit`'s job.
- **Reproducible.** Same ledger + same resolution snapshot + same findings → same
  verdict.

## When NOT to use this skill

No `claims.json` → `/evidence-ledger` first; no citation claims → re-run the ledger on LaTeX or emit `[]`; other dimensions → their own auditors; never on a timer.
Read `reference/routing.md` (section "When NOT to use this skill") for the full hand-off list.

## Review tracing

Policy: **forensic** — never silently skip. The full per-key trace layout
(`run.meta.json` + the `resolution.json` snapshot + per-key
`NNN-<key>.request.json` / `.response.md` / `.meta.json`) is defined in **Step 5**;
write each `.response.md` during Step 3, immediately after its reviewer call. Each
`request.json` must hold only the dossier record + neutral resolution facts + the
checklist (the reviewer-independence audit trail) — never a hunch.
