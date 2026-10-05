---
name: ai-style-impressions
description: "Lists located AI writing-style impressions in a paper (LLM phrase tics, defensive hedging, jargon-stuffing, invented codenames, bullet overuse) with zero verdict weight; not an authorship classifier. Run after evidence-ledger. Triggers: \"AI style\", \"vibe check\", \"vibe paper\", \"writing fingerprint\", \"AI 文风\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, mcp__codex__codex
---

# AI Writing-Style Impressions — itemized, located, ZERO verdict weight (NOT integrity findings)

Surface AI writing-**style** impressions for: **$ARGUMENTS** (requires `claims.json`
from `/evidence-ledger`). Emit span-anchored `ai-style-impressions.findings.json`.
Every finding here is an **impression** with **ZERO verdict weight** — this skill
proposes **no integrity finding** and computes **no verdict**.

> ⚠️ **This is the repo's ONLY non-integrity output, and it is non-integrity by
> construction.** AIS findings are transparent, itemized impressions of AI-generated
> *writing style*. The adjudicator (`tools/adjudicate_findings.py`) gives **every** AIS
> finding **ZERO verdict weight** — it is forced to `info`, excluded from
> `overall_verdict`, and rendered in a **separate** report section,
> *"AI Writing-Style Impressions — NOT integrity findings · ZERO verdict weight"*. **A
> paper can be `CLEAN_GIVEN_EVIDENCE` and still list many AIS impressions.** These are
> **not** factual/integrity inconsistencies and imply **no authorship probability**. We
> are **not** an opaque AI-text classifier: no scores, never *"this is AI-written"* /
> *"likely AI-generated"*. Every finding is a **named, located, itemized** observation
> with an `fp_case`. For authorship detection use a dedicated tool (Pangram / GPTZero /
> Binoculars) — that is out of scope here, by design.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the paper or the ledger changes.

Read `reference/rationale.md` for why this skill exists (the reviewer reactions it names, and why they are not misconduct or authorship evidence); it is background, not procedure.

## Core doctrine (the non-negotiables)

**Ledger-anchored, span-verified, ZERO verdict weight, NOT an authorship classifier,
reviewer ≠ adjudicator.** Two passes feed the pipeline:

1. a **deterministic** pass (no model) — the one objectively computable style signal: a
   conservative **defensive-hedge density screen** (`AIS-DEFENSIVE-HEDGE`), which fires
   only on a genuine pattern (≥4 distinct strong-template hedge sentences across ≥2
   non-excluded sections **and** ≥25% of all scope sentences). It flags the **recurrence
   of the hedge SHAPE**, never who wrote it (`tools/check_ai_style.py`);
2. a **fresh cross-model GROSS-cases-only** semantic pass — the 13 judgment-call style
   tells, each span-anchored, `not_integrity_finding: true`, `false_positive_risk:
   high`, with an `fp_case`. (`AIS-DEFENSIVE-HEDGE` is **dual**: deterministic for the
   pervasive case above + this semantic pass for the sub-threshold/qualitative posture
   the density screen misses.)

Both emit findings conforming to `schemas/finding.schema.json` (plus the AIS-only fields
`not_integrity_finding` / `fp_case`). **Every above-info finding cites a ledger
`claim_id` + a verbatim span** (`references/integrity-forensics-contract.md` rules 1–2).
Because the ledger holds only *checkable* claims (numbers, scope, captions, citations,
table cells) and almost no free prose, a style impression that cannot land on an
extracted claim **stays `info`** — a note, never an above-info impression. The model
**proposes**; `tools/adjudicate_findings.py` **decides** — and for AIS it always decides
the same thing: **info, zero weight, separate section** (`reviewer-independence.md`
Layer 2). This skill computes **no verdict** and proposes **no integrity finding**.

## How this differs from the other auditors (route correctly)

This skill emits only the 13 `AIS-*` style impressions, at ZERO verdict weight. Every integrity question goes to its own auditor
(`consistency-audit`, `experiment-forensics`, `baseline-comparison-audit`, `citation-forensics`, `eval-design-forensics`,
`proof-derivation-forensics`); checkable surface tells go to `presentation-signals`. Never use an AIS impression to carry a substantive accusation.
Read `reference/routing.md` for the auditor table and the 13-pattern table (impression, `fp_case`, substantive route) before Step 2 and whenever a tell may be substantive.

## What this skill REFUSES to emit (even as an impression)

These are **never** emitted, not even as an `info` note. They are unfalsifiable, or
they are authorship claims, or they are aesthetics — none is a *located, repeated,
named* observation:

- **any standalone single-punctuation tell** — one em-dash, one semicolon, one adverb.
  A style impression is about **recurrence at a location**, never a single character;
- **generic non-native English / awkward prose** — that is a writing-quality opinion,
  not an AI-style tell, and is a massive FP for international authors;
- **"this is AI-written" / any authorship probability / any classifier score** — out of
  scope by design; we audit style *impressions*, never provenance;
- **pure aesthetic judgments** — "ugly", "too polished", "looks generated" with nothing
  located;
- **presence-only flags** — "has bullets" / "has an appendix" / "short intro" with no
  located, repeated, named observation. Presence ≠ pattern.

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL          = gpt-5.5                  # different family from executor (Claude)
REVIEWER_REASONING      = xhigh                    # always; effort never lowers reviewer quality
REVIEWER_SANDBOX        = read-only                # detect-only; never mutate the paper
REVIEWER_CWD            = <paper-dir>              # so it can read claims.json + pdf-text + the PDF directly
THREAD_POLICY           = fresh mcp__codex__codex per run; NEVER mcp__codex__codex-reply
TAXONOMY_VERSION        = 0.5                      # AIS track migrated out of §F in v0.5
VERDICT_WEIGHT          = 0        # adjudicator forces every AIS finding to info + excludes it from overall_verdict
NOT_INTEGRITY_FINDING   = true     # on EVERY finding (deterministic + semantic) — not optional
DETERMINISTIC_PATTERNS  = AIS-DEFENSIVE-HEDGE   # Step 1 (tools/check_ai_style.py), pervasive case only
SEMANTIC_PATTERNS       = the 13 AIS-* style tells, GROSS cases only   # Step 2 (reviewer)
                          # AIS-DEFENSIVE-HEDGE is DUAL: density screen (Step 1) + sub-threshold (Step 2)
DEFAULT_FP_RISK         = high     # every AIS impression; this is not optional
OBS_REQUIRED            = 0        # every AIS pattern is decidable at L0 (PDF-only)
SEVERITY                = impression, never a flag (the adjudicator forces it to info; no cap needed here)
DETERMINISTIC_FINDINGS  = ai-style-impressions.deterministic.findings.json   # Step 1, ids AIS###
SEMANTIC_FINDINGS       = ai-style-impressions.findings.json                 # Step 3, ids F### (validated)
TRACE_POLICY            = forensic (never silently dropped)
TRACE_DIR               = .aris/traces/ai-style-impressions/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** builds none of the judgment: it locates the ledger + the PDF,
  passes **paths + the ledger + the checklist** to the reviewer, validates the
  reviewer's spans, forces the AIS fields, and writes the findings file. It never
  summarizes the paper, pre-judges "this looks AI-written", or leaks an opinion into the
  prompt (`reviewer-independence.md` Layer 1).
- **Reviewer (codex / gpt-5.5)** reads `claims.json` + the PDF-text + the PDF itself
  (visually only if it can render it; otherwise caption text only — see
  `AIS-SINGLE-STYLE-FIGURES`), proposes **gross-only** style impressions, and
  self-reports `fp_case`. It is the evidence-extractor, not the judge — and it never
  issues an authorship verdict.
- **Fresh thread per run.** `codex-reply` is intentionally absent from `allowed-tools`;
  never carry one run's conclusions into another (the bias guard).
- **Detect-only.** No `Edit` in `allowed-tools`; the reviewer sandbox is `read-only`.
  `Write` is used **only** for this skill's own findings / trace artifacts, never the
  audited paper. This is a third-party forensics tool, never a co-author.

---

## Step 0 — Preconditions: locate the ledger, read the level, find the PDF

The ledger is the **only** structure this skill reasons over for anchoring. Resolve it,
read the run's observability level **L** and `paper_id`, count the claim types AIS
anchors to, and locate the PDF + text source the reviewer will read (each Bash block is
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
print("SCOPE_CL     =", len(scope), "  (anchors for AIS-DEFENSIVE-HEDGE / -RESTATE-OVERCLAIM / -NARRATIVE-ARC-BREAK / -FOCUS-DRIFT)")
print("CAPTION_CL   =", len(caps), "  (anchors for AIS-SINGLE-STYLE-FIGURES / -INVENTED-CODENAME in captions)")
print("TABLE_SECS   =", len(tabs), tabs, "  (anchors for AIS-INVENTED-CODENAME used in result tables)")
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
      or "NONE (prose impressions limited to ledger spans)")
print("PDF_FILE     =", _pick({"pdf"}, ["*.pdf"])
      or "NONE (AIS-SINGLE-STYLE-FIGURES limited to caption text)")
PY
```

**Failure / edge handling.**
- `NO_LEDGER` → stop; tell the user to run `/evidence-ledger` first. This skill never
  re-reads the raw PDF and invents its own structure (contract rule 1).
- `SCOPE_CL = 0` → the hedge / restatement / arc / drift anchors are absent; those
  impressions will correctly hold at `info` (common on a pure PDF-text run that parsed
  no scope sentences). Continue.
- `CAPTION_CL = 0` and/or `PDF_FILE = NONE` → `AIS-SINGLE-STYLE-FIGURES` has no caption
  anchor and no image to inspect; the reviewer will almost certainly hold it at `info`.
  That is honest, not a failure.
- `CLAIMS = 0` (degenerate ledger) → every semantic impression will be unanchored →
  `info`. Run anyway; the file must exist.

Step 0 **prints** `RUN_LEVEL_L`, `PAPER_ID`, the absolute `LEDGER` / `PAPER_DIR`,
`PDF_FILE`, and `PDF_TEXT_FILE`. Shell variables do **not** persist across Bash calls,
so paste these **literal absolute values** into the `<...>` placeholders of each later
step — do not assume an exported `$LEDGER` survives between blocks.

## Step 1 — Deterministic impression check (no LLM): `AIS-DEFENSIVE-HEDGE`

The one objective, eval-testable style signal: a conservative **defensive-hedge density
screen**, computed purely from the ledger's `scope` claims. It fires **only** on a
genuine pattern — never on one scoping sentence — and flags the recurrence of the hedge
SHAPE, never who wrote it. Runs before any model:

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json from Step 0>"
python3 "$ROOT/tools/check_ai_style.py" \
    --ledger "$LEDGER" \
    --out "$(dirname "$LEDGER")/ai-style-impressions.deterministic.findings.json"
```

This emits at most one finding with `pattern_id: AIS-DEFENSIVE-HEDGE`,
`reviewer.deterministic: true`, `not_integrity_finding: true`,
`false_positive_risk: high`, `observability_level_required: 0`, `finding_id: AIS###`,
and ≤3 representative hedge spans, each anchored to a `scope` ledger claim. It fires only
when **≥4 distinct strong-template hedge sentences** ("we do not claim …", "not X but
rather Y", "本文并不声称 …") appear **across ≥2 non-excluded sections** AND constitute
**≥25% of all scope sentences** — hedges in Limitations / Related-Work / Ethics /
Broader-Impact / Acknowledgements are **excluded** (expected and legitimate). Because
PDF-text ledgers label every section `unknown`, the ≥2-section gate makes this
effectively LaTeX-decided — conservative by design.

**Failure handling.** If the tool errors, fix the invocation
(`python3 "$ROOT/tools/check_ai_style.py" --help`) — do **not** hand-fabricate
deterministic findings. An empty output (`[]`) is a valid, expected result (no pervasive
hedging, or no `scope` claims were extracted); keep the file.

## Step 2 — Cross-model GROSS-cases-only semantic pass (the 13 impressions; reviewer ≠ adjudicator)

The style tells are judgment calls. Open a **fresh** `mcp__codex__codex` thread (the
Reviewer Calling Convention above), `cwd = PAPER_DIR` so it can read `claims.json`, the
PDF-text, and the PDF directly. First create the forensic trace dir and fix the exact
response path — shell state does not persist, so this prints the literal paths to reuse:

```bash
LEDGER="<abs path to claims.json from Step 0>"; PAPER_DIR="$(dirname "$LEDGER")"
TS="$(date +%F)"; BASE="$PAPER_DIR/.aris/traces/ai-style-impressions"
NN=1; while [ -d "$(printf '%s/%s_run%02d' "$BASE" "$TS" "$NN")" ]; do NN=$((NN+1)); done
TRACE_DIR="$(printf '%s/%s_run%02d' "$BASE" "$TS" "$NN")"; mkdir -p "$TRACE_DIR"
echo "TRACE_DIR = $TRACE_DIR"
echo "PROPOSED  = $TRACE_DIR/001-style-semantic.response.md   # save the raw reply here; reuse as PROPOSED in Step 3"
```

Replace the bracketed placeholders below with the real values from Step 0, send EXACTLY
this, and save the **verbatim** reviewer reply to the `PROPOSED` path above (the Step 3
input) **before** parsing:

Read the "Step 2 — reviewer prompt" block in `reference/reviewer-prompt.md` and send it verbatim, every placeholder filled.

**Failure handling.**
- *MCP stall / hang* (common in long sessions): re-invoke the **identical** prompt as a
  **fresh** `mcp__codex__codex` call (gpt-5.5, xhigh) — never `codex-reply`.
- *Reviewer returns prose, not a JSON array*: the Step 3 validator extracts the
  outermost `[...]`; if there is none, re-ask once with "Output ONLY the JSON array,
  nothing else." Do not hand-author findings on the reviewer's behalf.
- *Reviewer slips toward authorship/probability language, or emits a non-AIS pattern*:
  that is what the Step 3 fields + the AIS allow-list are for — the validator strips any
  authorship verdict shape by forcing `not_integrity_finding` and drops any non-`AIS-`
  pattern. Do not pre-suppress; let the gate work.

## Step 3 — Validate + anchor + tag (keep only `AIS-*`; never cap; never let integrity through)

The executor enforces the ANCHOR gate, the AIS allow-list, and the AIS field-forcing
**before** keeping anything. Unlike `presentation-signals`, this validator does **not**
cap severity — the adjudicator zero-weights every AIS finding regardless — but it
**MUST** drop any non-`AIS-` pattern (an integrity problem must be raised by its own
auditor, never smuggled into the zero-weight track). The span must be a verbatim,
whitespace-normalized **substring of** the cited claim (`span in base`, never `base in
span` — appending hallucinated text to a real claim must fail):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"
PROPOSED="<the PROPOSED path printed in Step 2>"   # the verbatim reviewer reply you saved
OUT="$(dirname "$LEDGER")/ai-style-impressions.findings.json"
python3 - "$LEDGER" "$PROPOSED" "$OUT" <<'PY'
import json, re, sys
ledger_path, proposed_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

def nw(s):                                   # mirror adjudicator _norm_ws (whitespace only)
    return " ".join((s or "").split())

# The 13 AIS-* style impressions. The deterministic Step 1 (tools/check_ai_style.py) owns the
# PERVASIVE AIS-DEFENSIVE-HEDGE case; it is KEPT here too because that pattern is DUAL (Step 2
# catches the sub-threshold/qualitative posture the density screen misses; ids never collide —
# Step 1 is AIS###, this file is F###). EVERYTHING ELSE is DROPPED: any HP-* / integrity pattern,
# any non-AIS id, anything malformed. An integrity problem belongs to its own auditor and must
# NEVER be smuggled into the zero-weight AIS track.
AIS_PATTERNS = {
    "AIS-NARRATIVE-ARC-BREAK", "AIS-LLM-PHRASE-TICS", "AIS-DEFENSIVE-HEDGE",
    "AIS-JARGON-STUFF", "AIS-INVENTED-CODENAME", "AIS-CLAUSE-FORMULA-WALL",
    "AIS-GRATUITOUS-PSEUDOCODE", "AIS-BULLET-LIST-OVERUSE", "AIS-BOLD-MODULE-SPAM",
    "AIS-RESTATE-OVERCLAIM", "AIS-FOCUS-DRIFT", "AIS-SINGLE-STYLE-FIGURES",
    "AIS-APPENDIX-DUMPING-GROUND",
}
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

kept, dropped, demoted = [], 0, 0
n = 0
for f in proposed:
    if not isinstance(f, dict):
        dropped += 1; continue
    pid = f.get("pattern_id")
    if pid not in AIS_PATTERNS:              # keep ONLY AIS-*; never let an integrity/non-AIS pattern through
        dropped += 1; continue
    n += 1
    f["finding_id"] = f"F{n:03d}"
    f["skill"] = "ai-style-impressions"      # force-correct the skill tag
    f["pattern_id"] = pid
    f["not_integrity_finding"] = True        # the doctrine, on EVERY finding (not optional)
    f["false_positive_risk"] = "high"        # AIS impressions are high-FP by design (not optional)
    f["observability_level_required"] = 0    # every AIS pattern is L0-decidable
    if f.get("verdict_local") not in VL: f["verdict_local"] = "warn"
    f.setdefault("fp_case", "Style impression only; common in honest LLM-assisted / "
                 "non-native writing and house style — not evidence of AI authorship.")
    f.setdefault("recommended_reviewer_action", "Glance at the cited span as a readability "
                 "impression; not misconduct, not an authorship judgment, no score.")
    sev = f.get("severity")
    if sev not in SEV: sev = "minor"         # neutral default. NO severity cap: the adjudicator
                                             # forces every AIS finding to info + zero weight regardless.
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
        sev = "info"; demoted += 1           # unanchored impression -> info note, NEVER silently dropped
    f["severity"] = sev
    # cross-model provenance (reviewer-independence: this is a proposal, not a verdict)
    f["reviewer"] = {"model": "gpt-5.5", "reasoning": "xhigh", "deterministic": False}
    kept.append(f)

json.dump(kept, open(out_path, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"validated {len(kept)} AI-style impressions "
      f"({demoted} unanchored -> info note, "
      f"{dropped} dropped: non-AIS/integrity/malformed) -> {out_path}")
PY
```

Read `reference/rationale.md` ("Step 3 gate scope") for exactly what this gate enforces and why it does not cap severity.

Read `reference/worked-examples.md` for a kept impression, a refused non-finding and a routing case before you judge borderline output.

**Failure handling.** A `KeyError` / `JSONDecodeError` means the reviewer output was
malformed → re-run Step 2 once with the strict-JSON reminder. If it is **still**
unparseable, fail closed: write an empty array to `ai-style-impressions.findings.json`
(`printf '[]' > "$OUT"`) so the output contract's file exists — never hand-author
findings on the reviewer's behalf. If a finding loses all evidence, it is *kept as
`info`* (never silently dropped — the forensic record stays).

## Step 4 — Emit (two files, no merge)

Step 1 wrote `ai-style-impressions.deterministic.findings.json` (ids `AIS###`); Step 3
wrote `ai-style-impressions.findings.json` (validated semantic impressions, ids `F###`).
**Keep them separate. Do NOT copy the deterministic finding into the semantic file** —
the orchestrator concatenates `*.findings.json`, so merging would double-count
`AIS-DEFENSIVE-HEDGE`. The id namespaces (`AIS###` vs `F###`) do not collide.

If the semantic pass found nothing blatant, `ai-style-impressions.findings.json` is `[]`
— write it anyway. **Silent skip is forbidden**: the orchestrator and the standalone
adjudicate command both expect the file to exist at a predictable path. For this
style-impression skill, `[]` (or all-`info`) is the **common, correct** result.

## Step 5 — Trace (forensic; never silently dropped)

Save the raw reviewer call under the `TRACE_DIR` created in Step 2
(`.aris/traces/ai-style-impressions/<YYYY-MM-DD>_run<NN>/`). This repo ships no
`save_trace.sh`, so write the files directly:

```
.aris/traces/ai-style-impressions/<date>_run<NN>/
  run.meta.json                    # {skill, paper_id, run_level_L, ledger_sha?, generated_at}
  001-style-semantic.request.json  # the EXACT prompt sent (paths + checklist; no paper digest)
  001-style-semantic.response.md   # the FULL raw reviewer response (input to Step 3)
  001-style-semantic.meta.json     # {model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}
```

The `request.json` is the independence audit trail — it must show the executor sent only
**paths + the ledger + the checklist**, never a hunch like "this looks AI-generated".
(Step 1 is deterministic and needs no trace beyond its output file.)

## Step 6 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here**: the orchestrator globs every
`*.findings.json`, runs the adjudicator, and emits `REPORT.md` + `report.json` — with
the AIS findings rendered in their **separate, zero-weight** section. When running this
skill **alone**, you may produce the report yourself — `--ledger` is **required** (it is
what re-verifies each finding quotes a real ledger span):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
# derive paper-id + level from the ledger so this block is self-contained (no carried vars):
PAPER_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["paper_id"])' "$LEDGER")"
L="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("observability_level",0))' "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D/ai-style-impressions.deterministic.findings.json" \
               "$D/ai-style-impressions.findings.json" \
    --ledger "$LEDGER" \
    --paper-id "$PAPER_ID" --observability-level "$L" --taxonomy-version 0.5 \
    --out "$D/report.json" --md "$D/REPORT.md"
```

The adjudicator forces every AIS finding to `info` and `_verdict_weight = 0`, then
renders them under *"## AI Writing-Style Impressions — NOT integrity findings · ZERO
verdict weight"* with their `fp_case` and reviewer note. Because **every** finding here
is zero-weight, an **AIS-only run's `overall_verdict` is ALWAYS
`CLEAN_GIVEN_EVIDENCE`** — no AIS impression can reach even `SOFT_FLAGS`, let alone
`HARD_FLAGS`. The impressions populate the separate section only; they **never** move
the integrity verdict. No model is in the final decision.

## Output contract

This skill **always** writes, into the ledger's directory:

- `ai-style-impressions.deterministic.findings.json` — Step 1, a JSON array
  (`schemas/finding.schema.json` + AIS fields); the `AIS-DEFENSIVE-HEDGE` density finding
  with `reviewer.deterministic:true`, `not_integrity_finding:true`, ids `AIS###` (or `[]`).
- `ai-style-impressions.findings.json` — Step 3, a JSON array; validated semantic style
  impressions, ids `F###` (or `[]`). Each above-info finding carries
  `evidence[].claim_id` + a verbatim `span`, `severity` ≤ `minor`,
  `false_positive_risk: high`, `not_integrity_finding: true`,
  `observability_level_required: 0`, an `fp_case`, and a `pattern_id` ∈ the 13 `AIS-*`
  set.
- `.aris/traces/ai-style-impressions/<date>_run<NN>/` — Step 5, the raw reviewer call.

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 6 / the orchestrator), which renders the
AIS findings in the separate zero-weight section. They **never** move `overall_verdict`.

## Key rules

- **ZERO verdict weight, always.** Every AIS finding is forced to `info` and excluded
  from `overall_verdict` by the adjudicator (by `skill`, by the `AIS-` prefix, and by
  the deprecated-style-id set). A paper can be `CLEAN_GIVEN_EVIDENCE` and list many.
- **Not authorship detection; not a classifier.** Never label a paper "AI-generated" /
  "likely AI", never assign a probability or a score. We surface located *impressions*,
  not provenance.
- **Every finding is named + located + has an `fp_case`.** No vibe, no "looks
  generated" with nothing anchored; `not_integrity_finding: true` on all of them.
- **Default to silence.** Most papers should produce few or zero AIS impressions; an
  empty (or all-`info`) result is the common, correct output.
- **No span → no above-info impression.** Reject unanchored / paraphrased findings to
  `info` here (the adjudicator re-enforces). `span in claim`, whitespace-normalized —
  never `claim in span`.
- **Stay in lane; route the substantive.** Emit only the 13 `AIS-*` patterns. When a
  tell is actually substantive (contradiction, fake citation, undefined notation, method
  drift, phantom result), hand it to the named integrity auditor — never encode it as a
  zero-weight style impression.
- **No severity cap needed, but no non-AIS pattern through.** The validator does not cap
  (the adjudicator zero-weights AIS regardless), but it **must** drop every non-`AIS-`
  pattern.
- **Two files, no merge.** Deterministic (`AIS###`) and semantic (`F###`) findings stay
  in separate files to avoid double-counting the dual `AIS-DEFENSIVE-HEDGE`.
- **Cross-model, fresh thread.** Reviewer is a different family (gpt-5.5 xhigh); every
  run is a new `mcp__codex__codex` thread; `codex-reply` is never used.
- **Detect-only.** Never edit the audited paper (no `Edit` in `allowed-tools`; reviewer
  sandbox is `read-only`).
- **Reproducible.** Same ledger + same findings → same (always-`CLEAN_GIVEN_EVIDENCE`,
  AIS-only) verdict + same impression list.

## When NOT to use this skill

Read `reference/routing.md` ("When NOT to use this skill") before running if the request is an authorship verdict, a real integrity problem, or a reject basis; it lists where each goes.

## Review tracing

Forensic trace policy and file layout are defined once in **Step 5** (Policy:
**forensic** — never silently skipped). The `request.json` records only the paths +
ledger + checklist that were sent (the reviewer-independence audit trail); the
`response.md` is the immutable input that Step 3 validates.
