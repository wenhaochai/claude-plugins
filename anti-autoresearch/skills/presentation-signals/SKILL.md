---
name: presentation-signals
description: "Flags surface tells in a paper: duplicate tables, leftover chatbot/pipeline/template strings, too few or LLM-looking figures, page padding. Auxiliary, capped at minor; AI prose style goes to ai-style-impressions. Run after evidence-ledger. Triggers: \"presentation signals\", \"surface check\", \"duplicate tables\", \"排版信号\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, mcp__codex__codex
---

# Presentation Signals — the surface tells (auxiliary, never a verdict)

Run surface signal checks for: **$ARGUMENTS** (requires `claims.json` from
`/evidence-ledger`). Emit span-anchored `presentation-signals.findings.json`. This
skill computes **no verdict**.

> ⚠️ **This skill is deliberately weak by design.** A polished paper can be
> fraudulent and a rough paper can be honest, so surface signals must **never** drive
> a verdict. Everything here is emitted under skill `presentation-signals`, which the
> adjudicator **caps at `minor`** (`SURFACE_ONLY_SKILLS` + `SURFACE_PATTERNS` in
> `tools/adjudicate_findings.py`) — at most `SOFT_FLAGS`, **never** `HARD_FLAGS`. This
> is **not an AI-text classifier**; for authorship detection use a dedicated tool
> (Pangram / GPTZero / Binoculars). Our only job is to add *"combine with the
> substantive findings and look closer"* context. See
> `references/hack-pattern-taxonomy.md` §F.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the paper or the ledger changes.

Why this exists (reviewer-noticed surface tells; real but weak evidence; context for the substantive auditors, never
standalone): read `reference/rationale.md` when you need the rationale.

## Core principle

**Ledger-anchored, span-verified, capped-at-minor, reviewer ≠ adjudicator, NOT a
detector.** Two passes feed the pipeline:

1. a **deterministic** pass (no model) — the objective, reproducible surface signals
   computable without judgment: duplicate tables (`HP-DUP-TABLE`) and leftover pipeline/
   template strings (`HP-PIPELINE-ARTIFACT`);
2. a **fresh cross-model GROSS-cases-only** semantic pass — the three judgment-call
   signals (`HP-THIN-FLOAT`, `HP-LLM-FIGURE`, `HP-PAGE-PADDING`), each span-anchored and
   tagged `false_positive_risk: high`.

Both emit findings conforming to `schemas/finding.schema.json`. **Every above-info
finding cites a ledger `claim_id` + a verbatim span** (`references/integrity-forensics-contract.md`
rules 1–2). Because the ledger holds only *checkable* claims (numbers, scope,
captions, citations, table cells) and almost no free prose, a surface signal that
cannot land on an extracted claim **stays `info`** — a note, never a flag. That is the
design working: a free-prose surface impression that lands on no extracted claim
structurally almost never becomes even a `minor` flag. The model **proposes**;
`tools/adjudicate_findings.py` **decides**
(`references/reviewer-independence.md` Layer 2). This skill computes **no verdict**.

## How this differs from the other auditors (route correctly)

Pure AI writing-style impressions (AI-flavor, hedging, narrative arc, jargon, codenames) belong to `ai-style-impressions`
(zero-weight AIS track), not here. Read `reference/routing.md` for the full auditor table and the when-not-to-use list.

**Stay in lane.** This skill emits **only** the five §F surface (`HP-DUP-TABLE`,
`HP-PIPELINE-ARTIFACT`, `HP-THIN-FLOAT`, `HP-LLM-FIGURE`, `HP-PAGE-PADDING`)
patterns — nothing else. **Do NOT raise here** (hand off instead): if
two "duplicate" tables actually report *contradictory* numbers for the same setting →
that is a numeric self-contradiction for `consistency-audit`, not `HP-DUP-TABLE`; if a
figure *misrepresents* a result vs its caption → `consistency-audit`
(`HP-CAPTION-MISMATCH`); if a thin float count sits under a "SOTA / comprehensive"
*empirical* claim → the substantive scope question goes to
`baseline-comparison-audit` / `consistency-audit` (you may *also* emit `HP-THIN-FLOAT`
as a capped surface note); a fabricated reference → `citation-forensics`. A surface
finding is the weakest thing in the report by construction — never use it to carry a
substantive accusation.

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL          = gpt-5.5                  # different family from executor (Claude)
REVIEWER_REASONING      = xhigh                    # always; effort never lowers reviewer quality
REVIEWER_SANDBOX        = read-only                # detect-only; never mutate the paper
REVIEWER_CWD            = <paper-dir>              # so it can read claims.json + pdf-text + the PDF directly
THREAD_POLICY           = fresh mcp__codex__codex per run; NEVER mcp__codex__codex-reply
TAXONOMY_VERSION        = 0.5                      # references/hack-pattern-taxonomy.md §F
DETERMINISTIC_PATTERNS  = HP-DUP-TABLE, HP-PIPELINE-ARTIFACT   # Step 1 (tool)
SEMANTIC_PATTERNS       = HP-THIN-FLOAT, HP-LLM-FIGURE, HP-PAGE-PADDING   # Step 2 (reviewer)
SEVERITY_CAP            = minor    # SURFACE_ONLY_SKILLS + SURFACE_PATTERNS in adjudicate_findings.py
DEFAULT_FP_RISK         = high     # every surface finding; this is not optional
OBS_REQUIRED            = 0        # every F-pattern is decidable at L0 (PDF-only)
DETERMINISTIC_FINDINGS  = presentation-signals.deterministic.findings.json   # Step 1, ids PRES###
SEMANTIC_FINDINGS       = presentation-signals.findings.json                 # Step 3, ids F### (validated)
TRACE_POLICY            = forensic (never silently dropped)
TRACE_DIR               = .aris/traces/presentation-signals/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** builds none of the judgment: it locates the ledger + the PDF,
  passes **paths + the ledger + the checklist** to the reviewer, validates the
  reviewer's spans, caps severity, and writes the findings file. It never summarizes
  the paper, pre-judges "this looks AI-written", or leaks an opinion into the prompt
  (`reviewer-independence.md` Layer 1).
- **Reviewer (codex / gpt-5.5)** reads `claims.json` + the PDF-text + the PDF itself
  (visually only if it can render it; otherwise caption text only — see HP-LLM-FIGURE),
  proposes **gross-only** surface signals, and self-reports `false_positive_risk`. It
  is the evidence-extractor, not the judge.
- Executor/reviewer split and fresh-thread rule: `${CLAUDE_PLUGIN_ROOT}/support/references/reviewer-independence.md` Layer 1.
- **Detect-only.** No `Edit` in `allowed-tools`; the reviewer sandbox is `read-only`.
  `Write` is used **only** for this skill's own findings / trace artifacts, never the
  audited paper. This is a third-party forensics tool, never a co-author.

---

## Step 0 — Preconditions: locate the ledger, read the level, find the PDF

The ledger is the **only** structure this skill reasons over for anchoring. Resolve
it, read the run's observability level **L** and `paper_id`, count the float-bearing
claims, and locate the PDF + text source the reviewer will read (each Bash block is
self-contained — shell state does not persist between calls, so re-derive paths):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
# $ARGUMENTS is a paper-dir OR a claims.json path:
LEDGER="$ARGUMENTS"; [ -d "$LEDGER" ] && LEDGER="$LEDGER/claims.json"
# Only the NO-ARGUMENT case defaults to the CWD ledger. An EXPLICIT argument that
# resolves to a missing claims.json must NOT silently fall back to $(pwd) — that
# could audit the wrong paper; let the NO_LEDGER check below fire instead.
[ -z "$ARGUMENTS" ] && LEDGER="$(pwd)/claims.json"
python3 - "$LEDGER" <<'PY'
import json, sys, os
p = sys.argv[1]
if not os.path.isfile(p):
    sys.exit("NO_LEDGER: claims.json not found. Run /evidence-ledger FIRST "
             "(it writes artifact_manifest.json + claims.json).")
d = json.load(open(p, encoding="utf-8"))
cl = d.get("claims", [])
caps = [c for c in cl if c.get("type") == "caption"]
tabs = sorted({(c.get("location") or {}).get("section","") for c in cl
               if c.get("type") == "table_cell"
               and str((c.get("location") or {}).get("section","")).startswith("table:")})
scope = [c for c in cl if c.get("type") == "scope"]
print("LEDGER       =", os.path.abspath(p))
print("PAPER_DIR    =", os.path.dirname(os.path.abspath(p)) or ".")
print("PAPER_ID     =", d.get("paper_id", "?"))
print("RUN_LEVEL_L  =", d.get("observability_level", 0))
print("CLAIMS       =", len(cl))
print("CAPTION_CL   =", len(caps), "  (anchors for HP-LLM-FIGURE)")
print("TABLE_SECS   =", len(tabs), tabs, "  (float count for HP-THIN-FLOAT / HP-DUP-TABLE)")
print("SCOPE_CL     =", len(scope), "  (anchors for HP-THIN-FLOAT / HP-PAGE-PADDING)")
paper_dir = os.path.dirname(os.path.abspath(p)) or "."
srcs = d.get("source_files", [])
for sf in srcs:
    print("SOURCE       =", sf.get("kind"), sf.get("path"))
# Deterministically pick the prose source + the PDF the reviewer will read, FROM the
# ledger's source_files (authoritative); fall back to a sorted glob. source_files paths
# may be relative to PAPER_DIR or absolute. This is the ONLY selection (no shell `ls`
# later), so the PDF-only/L0 path with no pdf source resolves to NONE.
import glob
def _resolve(rel):
    cand = rel if os.path.isabs(rel or "") else os.path.join(paper_dir, rel or "")
    return os.path.abspath(cand) if os.path.isfile(cand) else ""
def _pick(kinds, globs):
    for sf in srcs:
        if sf.get("kind") in kinds:
            r = _resolve(sf.get("path"))
            if r:
                return r
    for g in globs:
        hits = sorted(h for h in glob.glob(os.path.join(paper_dir, g), recursive=True)
                      if not {".aris", "build", "_build", ".git"} & set(os.path.relpath(h, paper_dir).split(os.sep)))
        if hits:
            return os.path.abspath(hits[0])
    return ""
print("PDF_TEXT_FILE=", _pick({"text", "latex"}, ["*.txt", "*.tex", "**/*.tex"])
      or "NONE (prose signals limited to ledger spans)")
print("PDF_FILE     =", _pick({"pdf"}, ["*.pdf"])
      or "NONE (HP-LLM-FIGURE limited to caption text)")
PY
```

**Failure / edge handling.**
- `NO_LEDGER` → stop; tell the user to run `/evidence-ledger` first. This skill never
  re-reads the raw PDF and invents its own structure (contract rule 1).
- `TABLE_SECS = 0` → `Step 1` (dup-table) will correctly emit `[]`: with no parsed
  `table_cell` claims there are no tables to compare (common on a pure PDF-text run).
  Keep the empty file; continue to Step 2.
- `CAPTION_CL = 0` and/or `PDF_FILE = NONE` → `HP-LLM-FIGURE` has no caption anchor and
  no image to inspect; the reviewer will almost certainly hold it at `info`. That is
  honest, not a failure.
- `CLAIMS = 0` (degenerate ledger) → every semantic surface signal will be unanchored
  → `info`. Run anyway; the file must exist.

Step 0 **prints** `RUN_LEVEL_L`, `PAPER_ID`, the absolute `LEDGER` / `PAPER_DIR`,
`PDF_FILE`, and `PDF_TEXT_FILE`. Shell variables do **not** persist across Bash calls,
so paste these **literal absolute values** into the `<...>` placeholders of each later
step — do not assume an exported `$LEDGER` survives between blocks.

## Step 1 — Deterministic surface check (no LLM)

The one objective, eval-testable surface signal: **duplicate tables** — two tables whose
ordered numeric cells are identical after rounding to 4 decimals (`HP-DUP-TABLE`),
computed purely from the ledger's `table_cell` values. Runs before any model:

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json from Step 0>"
python3 "$ROOT/tools/check_presentation.py" \
    --ledger "$LEDGER" \
    --out "$(dirname "$LEDGER")/presentation-signals.deterministic.findings.json"
```

This emits, per duplicate pair, a finding with `pattern_id: HP-DUP-TABLE`,
`severity: minor`, `false_positive_risk: high`, `observability_level_required: 0`,
`reviewer.deterministic: true`, `finding_id: PRES###`, and two `evidence` entries —
one per table section, each anchored to a **representative** `table_cell` claim of that
section (its verbatim `text_span`); the full matching ordered values appear in the
finding's `description`, not as per-cell evidence. Two tables qualify only if they share
an identical *ordered* sequence of ≥ `MIN_CELLS` (2) numeric cells (each rounded to 4
decimals before comparison).

**Failure handling.** If the tool errors, fix the invocation
(`python3 "$ROOT/tools/check_presentation.py" --help`) — do **not** hand-fabricate
deterministic findings. An empty output (`[]`) is a valid, expected result (no
identical tables, or no `table_cell` claims were extracted to compare); keep the file.

## Step 2 — Cross-model GROSS-cases-only semantic pass (reviewer ≠ adjudicator)

The other three §F signals are judgment calls. Open a **fresh** `mcp__codex__codex`
thread (the Reviewer Calling Convention above), `cwd = PAPER_DIR` so it can read
`claims.json`, the PDF-text, and the PDF directly. First create the forensic trace dir
and fix the exact response path — shell state does not persist, so this prints the
literal paths to reuse:

```bash
LEDGER="<abs path to claims.json from Step 0>"; PAPER_DIR="$(dirname "$LEDGER")"
TS="$(date +%F)"; BASE="$PAPER_DIR/.aris/traces/presentation-signals"
NN=1; while [ -d "$(printf '%s/%s_run%02d' "$BASE" "$TS" "$NN")" ]; do NN=$((NN+1)); done
TRACE_DIR="$(printf '%s/%s_run%02d' "$BASE" "$TS" "$NN")"; mkdir -p "$TRACE_DIR"
echo "TRACE_DIR = $TRACE_DIR"
echo "PROPOSED  = $TRACE_DIR/001-surface-semantic.response.md   # save the raw reply here; reuse as PROPOSED in Step 3"
```

Replace the bracketed placeholders below with the real values from Step 0, send EXACTLY
this, and save the **verbatim** reviewer reply to the `PROPOSED` path above (the Step 3
input) **before** parsing:

Send the call verbatim from `reference/reviewer-prompt.md`, filling `cwd`, `PDF_TEXT_FILE`, `PDF_FILE` and `L`.


**Failure handling.**
- *MCP stall / hang* (common in long sessions): re-invoke the **identical** prompt as a
  **fresh** `mcp__codex__codex` call (gpt-5.5, xhigh) — never `codex-reply`.
- *Reviewer returns prose, not a JSON array*: the Step 3 validator extracts the
  outermost `[...]`; if there is none, re-ask once with "Output ONLY the JSON array,
  nothing else." Do not hand-author findings on the reviewer's behalf.
- *Reviewer over-flags a surface impression*: that is what the Step 3 anchor gate + the
  adjudicator's surface cap are for — an unanchored impression falls to `info` and even
  anchored surface findings cap at `minor`. Do not pre-suppress; let the gates work.

## Step 3 — Validate + anchor + cap (the anti-detector gate)

The executor enforces the ANCHOR gate **and** the surface cap **before** keeping
anything — exactly the rules `tools/adjudicate_findings.py` re-applies, so nothing you
keep is silently rejected downstream. The span must be a verbatim,
whitespace-normalized **substring of** the cited claim (`span in base`, never
`base in span` — appending hallucinated text to a real claim must fail):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"
PROPOSED="<the PROPOSED path printed in Step 2>"   # the verbatim reviewer reply you saved
OUT="$(dirname "$LEDGER")/presentation-signals.findings.json"
python3 - "$LEDGER" "$PROPOSED" "$OUT" <<'PY'
import json, re, sys
ledger_path, proposed_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

def nw(s):                                   # mirror adjudicator _norm_ws (whitespace only)
    return " ".join((s or "").split())

# the THREE semantic surface patterns this skill's Step 2 may emit. HP-DUP-TABLE and
# HP-PIPELINE-ARTIFACT are deterministic-only (Step 1) and are DROPPED here to avoid
# double-counting under the orchestrator's *.findings.json glob; any non-surface
# (substantive) pattern is also dropped — it belongs to another skill and must never be
# smuggled in capped-at-minor. The pure AI writing-style patterns moved to the
# zero-weight AIS track (skills/ai-style-impressions) and are no longer emitted here.
SEMANTIC_SURFACE = {"HP-THIN-FLOAT", "HP-LLM-FIGURE", "HP-PAGE-PADDING"}
SEV = {"critical", "major", "minor", "info"}
VL  = {"fail", "warn", "clean", "needs_external_check"}
ABOVE_INFO = {"critical", "major", "minor"}

ledger = json.load(open(ledger_path, encoding="utf-8"))
claims = {c["claim_id"]: c for c in ledger.get("claims", []) if c.get("claim_id")}

raw = open(proposed_path, encoding="utf-8").read()
m = re.search(r"\[.*\]", raw, re.S)          # tolerate prose / code-fence wrapping
proposed = json.loads(m.group(0) if m else raw)
if isinstance(proposed, dict):               # tolerate {"findings": [...]}
    proposed = proposed.get("findings", [])

kept, dropped, demoted, capped = [], 0, 0, 0
n = 0
for f in proposed:
    if not isinstance(f, dict):
        dropped += 1; continue
    pid = f.get("pattern_id")
    if pid not in SEMANTIC_SURFACE:          # drop dup-table (deterministic) + any non-surface pattern
        dropped += 1; continue
    n += 1
    f["finding_id"] = f"F{n:03d}"
    f["skill"] = "presentation-signals"      # force-correct the skill tag
    f["pattern_id"] = pid
    if f.get("verdict_local") not in VL: f["verdict_local"] = "warn"
    f["false_positive_risk"] = "high"        # surface signals are high-FP by design (not optional)
    f["observability_level_required"] = 0    # every F-pattern is L0-decidable
    sev = f.get("severity")
    if sev not in SEV: sev = "info"
    if sev in {"critical", "major"}:         # SURFACE cap: a surface signal is NEVER above minor
        sev = "minor"; capped += 1
    # ANCHOR gate: span must be a verbatim ws-normalized SUBSTRING of its cited claim
    anchored = []
    for ev in (f.get("evidence") or []):
        cid, span = ev.get("claim_id"), nw(ev.get("span", ""))
        c = claims.get(cid)
        if c and span and span in nw(c.get("text_span", "")):   # span IN claim, not claim IN span
            ev.setdefault("location", c.get("location", {}))     # enrich for human navigation
            ev.setdefault("artifact_hash", c.get("evidence_anchor", ""))
            anchored.append(ev)
    f["evidence"] = anchored
    if sev in ABOVE_INFO and not anchored:
        sev = "info"; demoted += 1           # unanchored surface signal -> info note, NEVER a flag
    f["severity"] = sev
    # cross-model provenance (reviewer-independence: this is a proposal, not a verdict)
    f["reviewer"] = {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False}
    kept.append(f)

json.dump(kept, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"validated {len(kept)} surface findings "
      f"({capped} capped to minor, {demoted} demoted to info for unanchored span, "
      f"{dropped} dropped: non-surface/dup-table/malformed) -> {out_path}")
PY
```

Scope of this gate: **anchoring + the surface cap + enum/field coercion** (it does
**not** run `schemas/finding.schema.json`) — verbatim-span anchoring, severity cap to
`minor`, FP-risk forced to `high`, observability fixed to `0`, surface-pattern
allow-list (drop everything else), enum coercion, and cross-model provenance. It does
**not** compute the verdict; that belongs to
`tools/adjudicate_findings.py`, the single decider, which **independently re-applies**
the same `SURFACE_ONLY_SKILLS` + `SURFACE_PATTERNS` cap (double-belt: by skill AND by
pattern_id, so a surface signal cannot bypass the cap even if mis-tagged).

Read `reference/worked-examples.md` for worked `HP-THIN-FLOAT` / `HP-PAGE-PADDING` findings and an `HP-LLM-FIGURE`
non-finding held at `info`.


**Failure handling.** A `KeyError` / `JSONDecodeError` means the reviewer output was
malformed → re-run Step 2 once with the strict-JSON reminder. If it is **still**
unparseable, fail closed: write an empty array to `presentation-signals.findings.json`
(`printf '[]' > "$OUT"`) so the output contract's file exists — never hand-author
findings on the reviewer's behalf. If a finding loses all evidence, it is *kept as
`info`* (never silently dropped — the forensic record stays).

## Step 4 — Emit (two files, no merge)

Step 1 wrote `presentation-signals.deterministic.findings.json` (ids `PRES###`);
Step 3 wrote `presentation-signals.findings.json` (validated semantic findings, ids
`F###`). **Keep them separate. Do NOT copy the deterministic findings into the
semantic file** — the orchestrator concatenates `*.findings.json`, so merging would
double-count `HP-DUP-TABLE`. The id namespaces (`PRES###` vs `F###`) do not collide.

If the semantic pass found nothing blatant, `presentation-signals.findings.json` is
`[]` — write it anyway. **Silent skip is forbidden**: the orchestrator and the
standalone adjudicate command both expect the file to exist at a predictable path. For
this auxiliary skill, `[]` (or all-`info`) is the **common, correct** result.

## Step 5 — Trace (forensic; never silently dropped)

Save the raw reviewer call under the `TRACE_DIR` created in Step 2
(`.aris/traces/presentation-signals/<YYYY-MM-DD>_run<NN>/`). This repo ships no
`save_trace.sh`, so write the files directly:

```
.aris/traces/presentation-signals/<date>_run<NN>/
  run.meta.json                       # {skill, paper_id, run_level_L, ledger_sha?, generated_at}
  001-surface-semantic.request.json   # the EXACT prompt sent (paths + checklist; no paper digest)
  001-surface-semantic.response.md    # the FULL raw reviewer response (input to Step 3)
  001-surface-semantic.meta.json      # {model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}
```

The `request.json` is the independence audit trail — it must show the executor sent
only **paths + the ledger + the checklist**, never a hunch like "this looks
AI-generated". (Step 1 is deterministic and needs no trace beyond its output file.)

## Step 6 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here**: the orchestrator globs every
`*.findings.json`, runs the adjudicator, and emits `REPORT.md` + `report.json`. When
running this skill **alone**, you may produce the report yourself — `--ledger` is
**required** (it is what re-verifies each finding quotes a real ledger span; without it
every above-info finding fails closed to `info`):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
# derive paper-id + level from the ledger so this block is self-contained (no carried vars):
PAPER_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["paper_id"])' "$LEDGER")"
L="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("observability_level",0))' "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D/presentation-signals.deterministic.findings.json" \
               "$D/presentation-signals.findings.json" \
    --ledger "$LEDGER" \
    --paper-id "$PAPER_ID" --observability-level "$L" --taxonomy-version 0.5 \
    --out "$D/report.json" --md "$D/REPORT.md"
```

The adjudicator applies, in order: ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE
gates, then computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS,
HARD_FLAGS}. **Because every finding here is a surface signal, the strongest possible
contribution is `SOFT_FLAGS`** — a span-anchored, surviving `minor`. A
presentation-signals-only run can **never** produce `HARD_FLAGS`. No model is in the
final decision.

## Output contract

This skill **always** writes, into the ledger's directory:

- `presentation-signals.deterministic.findings.json` — Step 1, a JSON array
  (`schemas/finding.schema.json`); `HP-DUP-TABLE` findings, `reviewer.deterministic:true`,
  ids `PRES###` (or `[]`).
- `presentation-signals.findings.json` — Step 3, a JSON array; validated semantic
  surface findings, ids `F###` (or `[]`). Each above-info finding carries
  `evidence[].claim_id` + a verbatim `span`, `severity: minor`,
  `false_positive_risk: high`, `observability_level_required: 0`, and a
  `pattern_id` ∈ {HP-THIN-FLOAT, HP-LLM-FIGURE, HP-PAGE-PADDING}.
- `.aris/traces/presentation-signals/<date>_run<NN>/` — Step 5, the raw reviewer call.

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 6 / the orchestrator).

## Key rules

- **Auxiliary only; never a verdict.** Surface signals contribute at most
  `SOFT_FLAGS` and are **capped at `minor`** by the adjudicator (by skill AND by
  pattern_id). They are context for the substantive findings, not standalone evidence.
- **Not authorship detection.** Never label a paper "AI-generated" or imply misconduct
  from a surface signal. This repo is **not** an AI-text classifier — it audits
  integrity, not provenance.
- **Default to silence.** Most papers should produce few or zero surface findings; an
  empty (or all-`info`) result is the common, correct output.
- **No span → no flag.** Reject unanchored / paraphrased findings to `info` here (the
  adjudicator re-enforces). `span in claim`, whitespace-normalized — never
  `claim in span`. The sparse ledger is what keeps AI-flavor from ever becoming a flag.
- **FP-risk is always `high`; severity is always `minor`.** Forced by the validator;
  do not argue past the cap.
- **Stay in lane.** Emit only the five §F surface patterns. Substantive problems
  (numeric contradiction, fake citation, missing baseline) are handed to the
  substantive auditors, never encoded as a capped surface note.
- **Two files, no merge.** Deterministic (`PRES###`) and semantic (`F###`) findings
  stay in separate files to avoid double-counting under the orchestrator's glob.
- **Cross-model, fresh thread.** Reviewer is a different family (gpt-5.5 xhigh); every
  run is a new `mcp__codex__codex` thread; `codex-reply` is never used.
- **Detect-only.** Never edit the audited paper (no `Edit` in `allowed-tools`; reviewer
  sandbox is `read-only`).
- **Reproducible.** Same ledger + same findings → same verdict.

## When NOT to use this skill

Read `reference/routing.md` (When NOT to use this skill) before using this as the basis for any verdict or accusation.


## Review tracing

Forensic trace policy and file layout are defined once in **Step 5** (Policy:
**forensic** — never silently skipped). The `request.json` records only the paths +
ledger + checklist that were sent (the reviewer-independence audit trail); the
`response.md` is the immutable input that Step 3 validates.
