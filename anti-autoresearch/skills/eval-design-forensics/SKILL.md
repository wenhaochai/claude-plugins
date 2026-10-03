---
name: eval-design-forensics
description: "Audits whether a paper's evaluation measures what it claims: train/test leakage, conflicted or unvalidated LLM judges, selective reporting (dropped conditions, switched metrics). Works PDF-only, after evidence-ledger. Triggers: \"data leakage\", \"evaluation validity\", \"LLM judge bias\", \"cherry-picked\", \"数据泄漏\", \"选择性报告\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, Grep, Glob, WebSearch, WebFetch, mcp__codex__codex
---

# Eval-Design Forensics — does the evaluation measure what the paper claims?

Audit evaluation-design and reporting validity for: **$ARGUMENTS** (requires
`claims.json` from `/evidence-ledger`). Emit span-anchored
`eval-design-forensics.findings.json`. This skill computes **no verdict**.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the paper or the ledger changes, or a repo arrives and raises the level to L2.

> Adapted from the ML-evaluation-methodology literature — the leakage taxonomy of
> Kapoor & Narayanan (2023), the LLM-as-judge validity work (MT-Bench
> self-enhancement, self-preference, position bias), and the "Show Your Work" /
> reproducibility-checklist reporting norms — reframed to audit a **third party's**
> evaluation. A favourite autoresearch shortcut is to report a number that is
> arithmetically self-consistent (family A), runs real code against a real ground
> truth (family D), and **still does not measure what it claims**: the protocol
> leaks, the load-bearing metric is a conflicted/unvalidated LLM judge, or the
> reporting quietly drops a declared condition. This skill is the constraint that
> asks "is this a *valid measurement of the claim*?", pointed at a submission, and
> it stays honest — leakage and under-reporting are usually **honest methodological
> errors**, so every finding is a discrepancy to *clarify*, never an accusation.

Read `reference/rationale.md` for why this skill exists (the leakage / judge-validity / selective-reporting failure modes it targets).

## Core principle

**Ledger-anchored, span-verified, reviewer≠adjudicator, honest about what it cannot
settle.** Four properties:

1. **Anchor to a PAPER claim.** Every above-`info` finding cites a ledger `claim_id`
   and quotes a **verbatim span of that claim's `text_span`**
   (`references/integrity-forensics-contract.md` rules 1–2). The leak/judge/reporting
   tell lives in the *protocol / setup-description* — usually `method` and `scope`
   claims, with `comparison` / `number` for the judge metric and
   `caption` / `table_cell` / `baseline` for reporting. The anchor is whichever paper
   claim the finding undermines; a split-file `file:line`, a config, or a leaderboard
   date is **forensic context for the description**, never the anchor.
2. **The executor assembles facts; the reviewer judges.** At L2 the executor gathers
   **mechanical** split/preprocessing/judge/result facts (grep/hash — listing what
   exists is a fact, not a judgment) and may record one **public-record date fact**
   (a benchmark's release vs a model's cutoff, for the contamination FP guard). It
   passes **paths + the ledger + those facts + the checklist** to the reviewer and
   never pre-declares "this leaks" (`references/reviewer-independence.md`). The model
   **proposes**; `tools/adjudicate_findings.py` **decides**. This skill computes **no
   verdict**.
3. **Undecidable leakage subtypes → hand off, don't guess.** An *illegitimate-proxy
   feature*, *sampling bias in the test set*, and *pretraining/benchmark
   contamination* are domain / black-box judgments not settleable from the PDF **or
   the repo**. Emit `verdict_local: needs_external_check` + `requires_external_check:
   true` (contract rule 6); **name** the external methods a domain check would use —
   exchangeability (Oren 2023), Min-K% Prob (Shi 2023), Time-Travel (Golchin 2023),
   BIG-bench canary strings — and **never run them**.
4. **Verdict-bearing at L0/L1; observability still caps the L2-confirm.** Unlike
   `experiment-forensics` (no eval code at L0/L1 ⇒ info-only), a **stated-tell** here
   is decided from the described protocol and emits
   `observability_level_required: 0`. The **L2 confirmation** of the same leak/
   omission is a **separate** finding with `observability_level_required: 2` that
   auto-demotes on a PDF-only run (`references/observability-levels.md`). So a
   PDF-only run keeps the stated-tell as a flag and the verification as an info
   "confirm-at-L2" pointer — never the reverse.

## How this differs from the other auditors (route correctly)

L0/L1-stated, L2-verified; owns only `HP-EVAL-LEAKAGE`, `HP-JUDGE-VALIDITY`, `HP-SELECTIVE-REPORTING`.
Hand off: an LLM generating ground truth → `experiment-forensics` `HP-FAKE-GT` (L2); best-as-mean /
thin scope / appendix-vs-main → `consistency-audit`; never-mentioned SOTA baseline or single-dataset
"consistently" → `baseline-comparison-audit`; number-vs-code → `experiment-forensics`; citations →
`citation-forensics`; surface → `presentation-signals`. Read `reference/routing.md` for the full table and de-dup rules.

Read `reference/leakage-taxonomy.md` when mapping a leak to one of the Kapoor & Narayanan (2023) types (8 types / 3 categories, with observability and common false positives). K&N's L1/L2/L3 are leakage types, not this repo's observability levels L0/L1/L2.

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL        = gpt-5.5                  # different family from executor (Claude)
REVIEWER_REASONING    = xhigh                    # always; effort never lowers reviewer quality
REVIEWER_SANDBOX      = read-only                # detect-only; never mutate the paper
REVIEWER_CWD          = <paper-dir>              # so it can read claims.json + the protocol/source directly
THREAD_POLICY         = fresh mcp__codex__codex per PASS (and per entry on fan-out);
                        NEVER mcp__codex__codex-reply across passes/entries (the bias guard)
TAXONOMY_VERSION      = 0.5                      # references/hack-pattern-taxonomy.md (family H)
LEAKAGE_TAXONOMY      = Kapoor & Narayanan 2023  # 8 types / 3 categories — adopted, paraphrased
PATTERNS_OWNED / ALLOWED = HP-EVAL-LEAKAGE, HP-JUDGE-VALIDITY, HP-SELECTIVE-REPORTING   # emit ONLY these
DIMENSION             = evaluation              # SKILL_TO_DIMENSION["eval-design-forensics"]
FINDINGS_FILE         = eval-design-forensics.findings.json
FINDING_ID_NAMESPACE  = ED###                    # distinct from F###/NUM###/HL### (consistency), EF### (experiment), BC### (baseline), PD### (proof)
VERDICT_BEARING_AT    = L0/L1 (stated-tells)     # NOT repo-gated; L2 only CONFIRMS
TRACE_POLICY          = forensic (never silently dropped)
TRACE_DIR             = .aris/traces/eval-design-forensics/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** builds none of the judgment: it locates the ledger, extracts
  the evaluation surface (protocol / judge / declared-condition claims), at L2 gathers
  **mechanical** split/preprocessing/judge/result facts (grep/hash) and at most one
  **public-record date fact** for the contamination guard, passes **paths + the ledger
  + those facts + the checklist** to the reviewer, validates the reviewer's spans, and
  writes the findings file. It never summarizes the paper, pre-judges "this leaks", or
  leaks an opinion into the prompt (`reviewer-independence.md`). Passing a public
  release date (with its source) is the same allowed division `citation-forensics`
  (canonical metadata) and `baseline-comparison-audit` (leaderboard dates) use —
  reference facts, not hunches.
- **Reviewer (codex / gpt-5.5)** reads `claims.json` and the source (and, at L2, the
  split/preprocessing/judge/result files) directly from its `cwd`, decides which
  evaluations leak / rest on a conflicted-or-unvalidated judge / under-report, applies
  the known false-positive cases, and self-reports `false_positive_risk`. It is the
  evidence-extractor, not the judge.
- **Fresh thread per pass.** Leakage (Step 3) and judge-validity + selective-reporting
  (Step 4) are **separate fresh** `mcp__codex__codex` calls. On `— effort: max` or many
  evaluation tracks, fan each track **entry** out into its own fresh call — never
  `codex-reply` carrying one entry's conclusion into another (the bias guard).
  `codex-reply` is intentionally absent from `allowed-tools`.

---

## Step 0 — Preconditions: locate the ledger, read the run level

The ledger is the **only** structure this skill reasons over. Resolve it and read the
observability level **L** and `paper_id` it was built at (each Bash block is
self-contained — shell state does not persist, so re-derive paths every block):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
# $ARGUMENTS is a paper-dir OR a claims.json path:
LEDGER="$ARGUMENTS"; [ -d "$LEDGER" ] && LEDGER="$LEDGER/claims.json"
# Only the NO-ARGUMENT case defaults to the CWD ledger. An EXPLICIT argument that
# resolves to a missing claims.json must NOT silently fall back to $(pwd) — that
# could audit the wrong paper; let the NO_LEDGER check below fire instead.
[ -z "$ARGUMENTS" ] && LEDGER="$(pwd)/claims.json"
python3 - "$LEDGER" <<'PY'
import json, sys, os, collections
p = sys.argv[1]
if not os.path.isfile(p):
    sys.exit("NO_LEDGER: claims.json not found. Run /evidence-ledger FIRST "
             "(it writes artifact_manifest.json + claims.json).")
d = json.load(open(p, encoding="utf-8"))
claims = d.get("claims", [])
by = collections.Counter(c.get("type") for c in claims)
print("LEDGER       =", os.path.abspath(p))
print("PAPER_DIR    =", os.path.dirname(os.path.abspath(p)) or ".")
print("PAPER_ID     =", d.get("paper_id", "?"))
print("RUN_LEVEL_L  =", d.get("observability_level", 0))
print("CLAIMS       =", len(claims), dict(by))
# applicability signal — method/scope carry the protocol; comparison/number the judge
# metric; caption/table_cell/baseline the reported conditions:
rel = sum(by.get(t, 0) for t in ("method", "scope", "comparison", "number", "table_cell", "caption", "baseline"))
print("APPLICABLE   =", "yes" if rel else "low (no protocol/scope/comparison/table claims)")
PY
```

**Failure handling.** If `NO_LEDGER` is printed, stop and tell the user to run
`/evidence-ledger` first — this skill never re-reads the raw PDF and invents its own
structure (contract rule 1). Carry `L`, `PAPER_ID`, and the absolute `LEDGER` /
`PAPER_DIR` into every step below.

## Step 1 — Extract the evaluation surface from the ledger (decide whether to run)

Pull the claims this audit reasons over — the **protocol** (leakage anchors), the
**judge** (validity anchors), and the **declared conditions** (reporting anchors) —
and decide if there is anything to audit. This is a mechanical surface scan; the
reviewer decides validity:

```bash
LEDGER="<abs path to claims.json from Step 0>"
python3 - "$LEDGER" <<'PY'
import json, re, sys, collections
d = json.load(open(sys.argv[1], encoding="utf-8"))
claims = d.get("claims", [])
LEAK = re.compile(r"\b(train(?:ing)?[\s/_-]*(?:and[\s/_-]*)?test|train[\s/_-]*test|split|held?[\s-]*out|"
                  r"cross[\s-]*validat|k-?fold|preprocess|standardi[sz]|normali[sz]|imput|"
                  r"resampl|oversampl|smote|feature[\s-]*select|leak|duplicat|de-?dup|"
                  r"temporal|time[\s-]*(?:series|order)|contaminat|pre-?train|data\s+split)\b", re.I)
JUDGE = re.compile(r"\b(LLM[-\s]*as[-\s]*a?[-\s]*judge|as\s+(?:a\s+)?judge|automatic(?:ally)?\s+(?:judg|evaluat|scor|rat)|"
                   r"GPT-?4o?|GPT-?3\.5|Claude|Gemini|win[\s-]*rate|pairwise|preference|"
                   r"rated\s+by|scored\s+by|judged\s+by|LLM\s+(?:judge|evaluator|grader))\b", re.I)
DECLARE = re.compile(r"\b(we\s+(?:evaluate|report|test|measure|use)|datasets?|benchmarks?|metrics?|"
                     r"seeds?|over\s+\d+\s+(?:seed|run)|best\s+(?:checkpoint|prompt|run|model|epoch)|"
                     r"five|four|three|\{[^}]*\})\b", re.I)
leak_a, judge_a, report_a = [], [], []
for c in claims:
    t, span = c.get("type"), c.get("text_span", "")
    sec = c.get("location", {}).get("section", "?")
    if t in ("method", "scope") and LEAK.search(span):
        leak_a.append((c["claim_id"], t, sec, span[:160]))
    if t in ("comparison", "scope", "method", "number") and JUDGE.search(span):
        judge_a.append((c["claim_id"], t, sec, span[:160]))
    if t in ("scope", "method", "caption", "table_cell", "baseline") and DECLARE.search(span):
        report_a.append((c["claim_id"], t, sec, span[:160]))
print(f"LEAKAGE anchors: {len(leak_a)}  JUDGE anchors: {len(judge_a)}  REPORTING anchors: {len(report_a)}")
for tag, rows in (("leak", leak_a), ("judge", judge_a), ("report", report_a)):
    for cid, t, sec, sp in rows[:30]:
        print(f"  [{tag}:{t}] {cid} [{sec}] {sp!r}")
print("APPLICABLE   =", "yes" if (leak_a or judge_a or report_a) else "no -> write [] and stop")
PY
```

**Branch.** If **APPLICABLE = no** (no protocol / judge / declared-condition claims),
this skill is **not applicable**: write an empty `eval-design-forensics.findings.json`
(`[]`), record a one-line `NOT_APPLICABLE` reason in the trace (Step 7), and stop.
**Silent skip is forbidden** — the orchestrator globs `*.findings.json` and expects
the file to exist. Otherwise record the three anchor lists for the prompts. A purely
mechanical grep of the source helps surface the protocol/table language (do **not**
judge validity here — that is the reviewer's job):

```bash
LEDGER="<abs path to claims.json from Step 0>"
grep -rInE 'train[ /_-]*test|split|held[ -]*out|cross[ -]*valid|preprocess|standardi|normali|impute|leak|duplicat|as a judge|win rate|pairwise|we (evaluate|report) on|best (checkpoint|prompt|run)' \
    "$(dirname "$LEDGER")" --include='*.tex' --include='*.txt' 2>/dev/null | head -60
```

## Step 2 — Gather mechanical facts (L2 split/preprocessing/judge/result; optional date fact)

Create the run's trace dir **now** — its first use is the facts file written just below,
so it must exist before Step 7. Reuse this exact `RUNDIR` in Steps 3–7 (do **not**
create a second one):

```bash
DATE=$(date +%Y-%m-%d); N=1
while [ -d ".aris/traces/eval-design-forensics/${DATE}_run$(printf %02d $N)" ]; do N=$((N+1)); done
RUNDIR=".aris/traces/eval-design-forensics/${DATE}_run$(printf %02d $N)"; mkdir -p "$RUNDIR"
echo "RUNDIR = $RUNDIR"   # carry this exact path forward (shell state does not persist)
```

**At L2 only** (repo + result files present), gather raw, uninterpreted facts — paths
+ grep/hash only, the same executor/reviewer division as `experiment-forensics`. Skip
this block at L0/L1 (there is no code to read — the reviewer block gets "L<2: ..."):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
PAPER_DIR="<abs PAPER_DIR from Step 0>"; L="<L from Step 0>"; RUNDIR="<the RUNDIR above>"
if [ "$L" = "2" ]; then
  # (a) split / preprocessing / dedup ordering FACTS (the K&N-L1 / L3 tells) -> leakage_grep.txt
  grep -rInE 'train_test_split|StratifiedKFold|KFold|GroupKFold|TimeSeriesSplit|\.split\(|train/val|holdout|hold-out|'\
'StandardScaler|MinMaxScaler|fit_transform|\.fit\(|SimpleImputer|impute|SMOTE|resample|oversampl|'\
'SelectKBest|feature_select|drop_duplicates|duplicated\(|dedup|shuffle=True|random_state' \
      "$PAPER_DIR" --include='*.py' --include='*.ipynb' 2>/dev/null | head -80 > "$RUNDIR/leakage_grep.txt"
  # (b) LLM-judge calling code FACTS -> judge_grep.txt
  grep -rInE 'as_judge|llm_judge|judge_model|gpt-?4|gpt-?3\.5|claude|gemini|openai|anthropic|'\
'pairwise|win_rate|preference|rate_response|score_response|annotate' \
      "$PAPER_DIR" --include='*.py' --include='*.ipynb' --include='*.yaml' --include='*.json' 2>/dev/null | head -60 > "$RUNDIR/judge_grep.txt"
  # (c) which DECLARED conditions actually produced result files (the selective-reporting L2 confirm) -> reporting_grep.txt
  { find "$PAPER_DIR/results" "$PAPER_DIR/outputs" "$PAPER_DIR/logs" -type f \( -name '*.json' -o -name '*.csv' \) 2>/dev/null | sort | head -60
    echo "## metric/dataset keys present in result files:"
    grep -rIhoE '"(dataset|benchmark|metric|seed|split|task)"[^,}]{0,40}' \
      "$PAPER_DIR/results" "$PAPER_DIR/outputs" "$PAPER_DIR/logs" 2>/dev/null | sort -u | head -60; } > "$RUNDIR/reporting_grep.txt"
  # (d) reproducibility anchors: hash each discovered file (space-safe; tolerant of zero matches)
  { grep -rIlE 'split|scaler|judge|metric' "$PAPER_DIR" --include='*.py' 2>/dev/null | head -n 20
    find "$PAPER_DIR" -maxdepth 3 -path '*results*' -name '*.json' 2>/dev/null | head -n 20; } \
    | while IFS= read -r ff; do shasum -a 256 "$ff" 2>/dev/null; done > "$RUNDIR/hashes.txt"
  echo "L2 facts -> $RUNDIR/{leakage_grep,judge_grep,reporting_grep,hashes}.txt"
else
  echo "L<2: stated-tell pass only (no split/judge/result files to read)."
fi
```

**Optional contamination date fact (the FP guard, not a detector).** If a benchmark is
named and an evaluated model's training cutoff is knowable, you MAY record **one**
public-record date fact — `WebSearch`/`WebFetch` for "<benchmark> release date" and
"<model> training cutoff" — and write it (URL + access date) to
`$RUNDIR/contamination_dates.json`. This is a **fact** that *suppresses* a false
contamination flag (benchmark released after the cutoff → legitimate); it is **never**
a contamination *detector*. The skill never runs Min-K% / exchangeability / Time-Travel.

**Failure handling.** No network → skip the date fact; the reviewer treats
contamination as `needs_external_check` regardless. Empty L2 greps (a thin repo) → pass
"L2 but no split/judge/result files found" to the reviewer so it does not invent a leak.

## Step 3 — Leakage pass (cross-model, fresh thread) → HP-EVAL-LEAKAGE

Open a **fresh** `mcp__codex__codex` thread (Reviewer Calling Convention). The reviewer
reads `claims.json` from its `cwd` for the described protocol and, at L2, the split/
preprocessing files; every finding anchors to a ledger `claim_id`. Send EXACTLY (fill
every `[ ... ]`):

The prompt is the **Step 3 — Leakage prompt** block in `reference/reviewer-prompts.md`; read it and send it verbatim (gpt-5.5, xhigh, read-only, `cwd` = PAPER_DIR; it holds the K&N mapping, hard rules, severity decision and JSON output schema).

Persist the raw response to the trace dir (Step 7) **before** parsing. **Failure
handling:** MCP stall → re-invoke the **identical** prompt as a fresh
`mcp__codex__codex` (never `codex-reply`). Prose instead of JSON → the Step 5 validator
extracts the outermost `[...]`; if none, re-ask once "Output ONLY the JSON array." If
the L2 facts were empty, bias every code-confirm item toward `needs_external_check` —
never invent a split file.

## Step 4 — Judge-validity + Selective-reporting pass (cross-model, fresh thread)

A **separate, new** `mcp__codex__codex` thread. Send EXACTLY (fill every `[ ... ]`):

The prompt is the **Step 4 — Judge-validity + Selective-reporting prompt** block in `reference/reviewer-prompts.md`; read it and send it verbatim (hard rules, the two-item checklist with severities and de-dup routing, JSON output).

**Deepen at L2.** When `L == 2`, the judge/result facts let the reviewer promote a
text-only suspicion to a confirmed finding (keep `observability_level_required: 0` if
the text already showed the tell; use `2` only for what the files reveal). **Fan-out
(optional, breadth).** On `— effort: max` or many evaluation tracks, issue the relevant
checklist item **per track** as a separate fresh `mcp__codex__codex` call and
concatenate the arrays — never `codex-reply`. Persist each raw reply to the trace
(Step 7). **Failure handling:** identical to Step 3.

## Step 5 — Validate + anchor (the anti-hallucination gate)

The executor enforces the **ANCHOR** gate (the one `tools/adjudicate_findings.py`
re-applies, so an anchored finding you keep is not silently rejected downstream) plus
eval-design-specific **owned-pattern + schema-hygiene + external-check** pre-filters,
**before** keeping anything. The span must be a verbatim, whitespace-normalized
**substring of** the cited claim (`span in base`, never `base in span` — appending
hallucinated text to a real claim must fail). Pass **every** saved raw reviewer response
(leakage + judge/reporting + any per-track fan-out files); they merge into one findings
file with one `ED###` namespace:

The validator is the bash block in `reference/validator.md`; read it and run it verbatim with `LEDGER`, `OUT` (`$(dirname "$LEDGER")/eval-design-forensics.findings.json`), then every saved raw reviewer response file from Steps 3–4. Export `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"` first: variables are substituted in SKILL.md only, not in reference files.

Scope of this gate: **anchoring + owned-pattern + schema hygiene + external-check
pinning only** (schema hygiene = the *presence/validity* of the reviewer's required
fields — a missing/invalid `observability_level_required` or `false_positive_risk` on an
above-info finding fails **closed to info**, never a guessed default). Do **not**
re-implement the adjudicator's verdict-bearing gates (the observability LEVEL *downgrade*
`req > run_level`, the FP-risk *cap* `{high:minor, medium:major, low:critical}`, the
verdict) — those need the run level and belong to `tools/adjudicate_findings.py`, the
single decider. `needs_external_check` findings (the 3 leakage external subtypes, and any
unsure judge/GT call) are pinned to `info`, never dropped. The remaining judgments are the
**reviewer's**, per the prompt — the K&N type, the conflicted-vs-unvalidated split, the
`observability_level_required: 2` tag for a code-only confirm; if a kept finding plainly
violates one, re-run that pass with the correction noted (never hand-fabricate). A finding
that loses all evidence is **kept as info** (the forensic record stays).

Worked findings (stated preprocessing leak, contamination hand-off, conflicted judge, declared-but-unreported datasets) are in `reference/worked-examples.md`; read them when unsure of a finding's expected shape or severity.

## Step 6 — Emit (one file)

Step 5 wrote the validated array to **`eval-design-forensics.findings.json`** (a bare
JSON array conforming to `schemas/finding.schema.json`), in the ledger's directory. If
both passes found nothing — or this skill was not applicable (Step 1) — the file is
`[]`; **write it anyway** (silent skip is forbidden; the orchestrator's `*.findings.json`
glob and the standalone adjudicate command both expect it at a predictable path). This
skill writes **exactly one** findings file and runs **no deterministic tool of its own**
(unlike `consistency-audit`): every finding is a cross-model proposal, span-anchored,
gated, and handed to the adjudicator.

## Step 7 — Trace (forensic; never silently dropped)

Save every reviewer call under the **same `RUNDIR` created at the start of Step 2**
(`.aris/traces/eval-design-forensics/<YYYY-MM-DD>_run<NN>/`). This repo ships no
`save_trace.sh`, so write files directly — reuse that path; do **not** re-run the bump
loop here (it would allocate a second empty dir):

```bash
RUNDIR="<the RUNDIR printed in Step 2>"   # e.g. .aris/traces/eval-design-forensics/<date>_run01
mkdir -p "$RUNDIR"                          # idempotent — the dir already exists from Step 2
```

Populate it:

```
.aris/traces/eval-design-forensics/<date>_run<NN>/
  run.meta.json                       # {skill, paper_id, run_level_L, taxonomy_version:"0.5", leakage_taxonomy:"K&N 2023", generated_at, not_applicable?}
  leakage_grep.txt / judge_grep.txt / reporting_grep.txt / hashes.txt   # Step 2 L2 facts (if L2)
  contamination_dates.json            # optional public-record date fact (if gathered)
  001-leakage.request.json            # the EXACT Step-3 prompt sent (paths + ledger + facts + taxonomy + checklist)
  001-leakage.response.md             # the FULL raw reviewer response (input to Step 5)
  001-leakage.meta.json               # {model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}
  002-judge-reporting.request.json
  002-judge-reporting.response.md
  002-judge-reporting.meta.json
  # 00N-track-<entry>.* for each per-track fan-out call, if used
```

Each `request.json` is the independence audit trail — it must show the executor sent
only **paths + the ledger + the K&N taxonomy + the mechanical facts + the checklist**,
never a digest or pre-judgment of the paper (`references/reviewer-independence.md`).

## Step 8 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here**: the orchestrator globs every
`*.findings.json`, runs the adjudicator once over the union, and emits `REPORT.md` +
`report.json`. When running this skill **alone**, you may produce the report yourself —
`--ledger` is **required** (it verifies each finding quotes a real ledger span; without
it every above-info finding fails closed to `info`):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D/eval-design-forensics.findings.json" \
    --ledger "$LEDGER" \
    --paper-id "<PAPER_ID>" --observability-level <L> --taxonomy-version 0.5 \
    --out "$D/eval-design.report.json" --md "$D/eval-design.REPORT.md"
# prints e.g.: verdict=SOFT_FLAGS crit=0 maj=1 min=1 -> eval-design.report.json, eval-design.REPORT.md
```

The adjudicator applies, in order: ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE →
EXTERNAL-CHECK gates, then computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE,
SOFT_FLAGS, HARD_FLAGS} (any span-anchored **critical** decidable at `L` → HARD_FLAGS).
No model is in the final decision; this skill rolls up under the **`evaluation`**
dimension via `SKILL_TO_DIMENSION`. `needs_external_check` findings carry no severity
weight — they surface as open questions for a human, never as a flag. *(Use the
`eval-design.*` output names when standalone so you do not clobber the orchestrator's
combined `report.json` / `REPORT.md`.)*

## Output contract

This skill **always** writes, into the ledger's directory:

- `eval-design-forensics.findings.json` — a JSON array (`schemas/finding.schema.json`);
  the validated leakage + judge-validity + selective-reporting findings (or `[]`). Each
  above-info finding carries `evidence[].claim_id` + a verbatim `span`, an integer
  `observability_level_required`, a `pattern_id` ∈ {`HP-EVAL-LEAKAGE`,
  `HP-JUDGE-VALIDITY`, `HP-SELECTIVE-REPORTING`}, and an honest `false_positive_risk`.
  The three undecidable leakage subtypes (illegitimate-proxy / sampling-bias /
  contamination) and any unsure judge-vs-GT call appear as
  `verdict_local: needs_external_check` + `requires_external_check: true`, never a
  guessed leak.
- `.aris/traces/eval-design-forensics/<date>_run<NN>/` — the mechanical-facts files +
  the raw reviewer call(s).

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 8 / the orchestrator). It writes **no
second deterministic file** and never edits the audited paper.

## Key rules

- **Verdict-bearing at L0/L1; the L2-confirm is separate.** A stated leak / conflicted
  judge / declared-but-unreported condition is decidable from the described protocol →
  `observability_level_required: 0` (this is the opposite of `experiment-forensics`,
  which is info-only below L2). The L2 *confirmation* of the same tell is a separate
  `observability_level_required: 2` finding that auto-demotes on a PDF-only run.
- **No span → no severity.** Reject unanchored/paraphrased findings to `info` here (the
  adjudicator re-enforces). `span in claim`, whitespace-normalized — never `claim in
  span`. The anchor is a PAPER claim (the protocol / judge / declared-condition
  sentence); the split-file `file:line`, config, or leaderboard date is forensic detail
  in the description, never the anchor.
- **Two scales — never conflate.** K&N leakage **types** L1/L2/L3 are not this repo's
  **observability** levels L0/L1/L2. Carry both: the K&N type in `description`, the
  observability in `observability_level_required`.
- **Hand off the 3 undecidable leakage subtypes.** Illegitimate-proxy feature, sampling
  bias, and pretraining/benchmark contamination → `needs_external_check`; name the
  external methods (Oren 2023 / Min-K% / Time-Travel / canary) but **never run them**.
- **Judge ≠ ground-truth generator.** A judge whose preference IS the metric is
  `HP-JUDGE-VALIDITY` (here); a model that fabricates the reference the metric is
  computed against is `HP-FAKE-GT` (`experiment-forensics`, L2). Conflicted (family
  overlap) caps at major (FP medium); unvalidated-only caps at minor (FP high).
- **Selective-reporting stays in lane.** Only declared-but-unreported / metric-switch /
  best-without-held-out. best-as-mean → `HP-AGG-DRIFT`; thin scope → `HP-SCOPE-INFLATE`;
  never-mentioned baseline → `HP-MISSING-BASELINE`; appendix-vs-main on the same quantity
  → `HP-APPENDIX-CONTRA`. Do not double-emit.
- **Discrepancy, not accusation.** Leakage and under-reporting are usually honest
  methodological errors; output asks a reviewer to *check/clarify*, never to reject. The
  absence of a *reported* validation is not proof none was done (high-FP care).
- **Reviewer ≠ adjudicator.** The model proposes findings; `adjudicate_findings.py`
  decides the verdict. This skill emits findings only.
- **Cross-model, fresh thread per pass/track.** Reviewer is a different family (gpt-5.5
  xhigh); leakage and judge/reporting are separate fresh `mcp__codex__codex` threads;
  `codex-reply` is never used (absent from `allowed-tools`).
- **Detect-only.** Never edit the audited paper (reviewer sandbox is read-only).
- **Reproducible.** Same ledger + same findings → same verdict; the mechanical facts and
  any date fact (with URL + date) are traced so the expectation is auditable.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **The paper describes no evaluation protocol / judge / declared conditions**
  (`APPLICABLE = no` in Step 1) → write `[]` and stop.
- **An LLM generating the ground-truth labels/targets** (not judging outputs) →
  `/experiment-forensics` `HP-FAKE-GT` at **L2**.
- **best-reported-as-mean / appendix-vs-main / thin in-text scope with no comparison**
  → `/consistency-audit` (`HP-AGG-DRIFT` / `HP-APPENDIX-CONTRA` / `HP-SCOPE-INFLATE`).
- **A never-mentioned expected baseline, or "SOTA / first / beats prior work"** →
  `/baseline-comparison-audit` (+ `/citation-forensics`), handed off via
  `needs_external_check`.
- **Whether a reported number matches the repo / code** (fake GT, self-norm, phantom)
  → `/experiment-forensics` at **L2**.
- **An AI-text / "looks machine-written" verdict** → out of scope; surface hints live in
  `/presentation-signals` (auxiliary, capped at minor). This repo is **not** an AI-text
  classifier.
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the paper, ledger, or observability level changes (see the fence at the top).

## Review tracing

Forensic policy — never silently skipped. The exact `RUNDIR` layout and the
reviewer-independence audit-trail rule for each `request.json` (only paths + ledger +
the K&N taxonomy + mechanical facts + checklist were sent — no digest, no pre-judgment)
are specified once in **Step 7**; follow it for every `mcp__codex__codex` call (leakage,
judge/reporting, and any per-track fan-out).

## Acknowledgements

The sources this skill adapts (Kapoor & Narayanan 2023; MT-Bench judge-bias work; Show Your Work / reproducibility checklist) are acknowledged in `reference/rationale.md`.
