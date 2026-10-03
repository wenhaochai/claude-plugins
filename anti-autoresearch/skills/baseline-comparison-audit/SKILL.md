---
name: baseline-comparison-audit
description: "Audits a paper's baseline comparisons: missing SOTA/floor baselines, undertuned or unequal-budget ones, \"outperforms\" within error bars or without seeds, cross-row gains miscomputed. Needs evidence-ledger. Triggers: \"missing baselines\", \"weak baseline\", \"is the comparison fair\", \"SOTA earned?\", \"baseline 误报\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, Grep, Glob, WebSearch, WebFetch, mcp__codex__codex
---

# Baseline Comparison Audit — is the comparison complete, fair, and significant?

Audit baseline-comparison integrity for: **$ARGUMENTS** (requires `claims.json`
from `/evidence-ledger`). Emit span-anchored `baseline-comparison-audit.findings.json`.
This skill computes **no verdict**.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the paper, the ledger or the live leaderboard it cross-checks changes.

Read `reference/rationale.md` for the ARIS lineage and the failure modes this audit targets (why it exists); it is background, not procedure.

## Core principle

**Ledger-anchored, span-verified, reviewer≠adjudicator, honest about what it cannot
settle.** Four properties:

1. **Anchor to a PAPER claim.** Every above-`info` finding cites a ledger `claim_id`
   and quotes a **verbatim span of that claim's `text_span`**
   (`references/integrity-forensics-contract.md` rules 1–2). The "outperforms / SOTA
   / best / first" language lives in `comparison` and `scope` claims; the reported
   baseline set lives in `baseline` claims; values/table rows in `number` /
   `table_cell` claims. The anchor is whichever paper claim the finding undermines —
   the expected-baseline list, a leaderboard URL, or a config `file:line` are
   **forensic context for the description**, never the anchor.
2. **The executor assembles facts; the reviewer judges.** The profile + a live
   `WebSearch`/`WebFetch` give a *candidate expected-baseline set with sources and
   dates*; the executor passes it as **structured input** and never pre-declares
   "baseline X is missing" (`references/reviewer-independence.md`). The model
   **proposes**; `tools/adjudicate_findings.py` **decides**. This skill computes **no
   verdict**.
3. **Unsettleable completeness → hand off, don't guess.** "Is this really SOTA /
   first / the right baseline set?" cannot be closed from inside the paper. Unless an
   omission is *unambiguous, sourced, same-benchmark, and pre-dating*, emit
   `verdict_local: needs_external_check` + `requires_external_check: true`, not a flag
   (contract rule 6).
4. **Observability caps severity.** Stated-comparison checks are L0; a fairness
   finding that needs the actual config/seed files is `observability_level_required:
   2` and auto-demotes on a PDF-only run (`references/observability-levels.md`).

## How this differs from the other auditors (route correctly)

This skill owns completeness, fairness, significance and cross-row delta of baseline comparisons (L0 stated / L2 verified).
Text-only scope inflation and single-sentence deltas belong to `consistency-audit`; baseline-number-vs-code to `experiment-forensics` (L2);
cited-paper existence to `citation-forensics`; surface tells to `presentation-signals`. This skill never emits an F-pattern.
Read `reference/routing.md` for the full auditor table and the hand-off list when a finding might belong to another auditor.

## Per-domain baseline profile (`PROFILE_VERSION = 0.1` — a SEED prior, always verified live)

The per-domain table (expected baseline families, fairness control, variance norm) is in `reference/domain-profiles.md`. Read it at Step 2 item 1.

**Cross-domain control (always applicable, even off-profile):** the single most
informative baseline is the proposed method's **own backbone / base model with the
new component removed, run at an identical budget** — the ablation-as-baseline. Its
absence, or an unequal budget for it, is the most common fairness failure and is
checkable for *any* paper, profile row or not.

**Honesty rule (load-bearing): no profile row + inconclusive search ⇒ NO guessed
"missing baseline".** Run the *fairness* + *significance* checks (which need no
profile) and emit the completeness question as `needs_external_check`. The profile
seeds a *question*, never a detector.

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL        = gpt-5.5                  # different family from executor (Claude)
REVIEWER_REASONING    = xhigh                    # always; effort never lowers reviewer quality
REVIEWER_SANDBOX      = read-only                # detect-only; never mutate the paper
REVIEWER_CWD          = <paper-dir>              # so it can read claims.json + sources directly
THREAD_POLICY         = fresh mcp__codex__codex per DIMENSION (and per entry on fan-out);
                        NEVER mcp__codex__codex-reply across dimensions/entries
TAXONOMY_VERSION      = 0.5                      # references/hack-pattern-taxonomy.md
PROFILE_VERSION       = 0.1                      # the per-domain baseline profile above (advisory)
PATTERNS_OWNED        = HP-MISSING-BASELINE, HP-WEAK-BASELINE, HP-SIG-OVERLAP,
                        HP-DELTA-ERROR (cross-row comparison form only — see Step 4),
                        HP-RESOURCE-IDENTITY-MISMATCH (named dataset/model/benchmark vs its
                        public record — HF card / Papers-with-Code; gather-facts-then-judge,
                        observability_level_required 0; FP-suppress subset/variant/version)
FINDINGS_FILE         = baseline-comparison-audit.findings.json
FINDING_ID_NAMESPACE  = BC###                    # distinct from F###/NUM###/HL### (consistency), EF### (experiment)
TRACE_POLICY          = forensic (never silently dropped)
TRACE_DIR             = .aris/traces/baseline-comparison-audit/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** builds none of the judgment: it locates the ledger, extracts
  the comparison surface, assembles the candidate expected set **with sources and
  publication dates**, at L2 gathers **mechanical config/result facts** (grep/hash —
  listing what exists is a fact, not a judgment), passes **paths + the ledger + those
  facts + the checklist** to the reviewer, validates the reviewer's spans, and writes
  the findings file. It never summarizes the paper, pre-judges "X is missing", or
  leaks an opinion into the prompt (`reviewer-independence.md`). Passing what a public
  leaderboard says (with its date) is the same allowed division `experiment-forensics`
  (grep/hash facts) and `citation-forensics` (canonical metadata) use — reference
  facts, not hunches about the manuscript.
- **Reviewer (codex / gpt-5.5)** reads `claims.json` and the sources, decides which
  comparisons are incomplete / unfair / not significant, applies the known
  false-positive cases, and self-reports `false_positive_risk`. It is the
  evidence-extractor, not the judge.
- **Fresh thread per dimension.** Completeness (Step 3) and fairness + significance +
  delta (Step 4) are **separate fresh** `mcp__codex__codex` calls. On `— effort: max`
  or many comparison rows, fan each comparison **entry** out into its own fresh call —
  never `codex-reply` carrying one entry's conclusion into another (the bias guard).
  `codex-reply` is intentionally absent from `allowed-tools`.

---

## Step 0 — Preconditions: locate the ledger, read the run level

The ledger is the **only** structure this skill reasons over. Resolve it and read
the observability level **L** and `paper_id` it was built at (each Bash block is
self-contained — shell state does not persist between calls, so re-derive paths every
block):

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
# applicability signal — comparison / scope / baseline / table_cell are this skill's inputs:
rel = sum(by.get(t, 0) for t in ("comparison", "scope", "baseline", "table_cell"))
print("APPLICABLE   =", "yes" if rel else "low (no comparison/scope/baseline/table claims)")
PY
```

**Failure handling.** If `NO_LEDGER` is printed, stop and tell the user to run
`/evidence-ledger` first — this skill never re-reads the raw PDF and invents its own
structure (contract rule 1). Carry `L`, `PAPER_ID`, and the absolute `LEDGER` /
`PAPER_DIR` into every step below.

## Step 1 — Extract the comparison surface from the ledger (decide whether to run)

Pull the claims this audit reasons over and decide if there is anything to audit:

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json from Step 0>"
python3 - "$LEDGER" <<'PY'
import json, re, sys, collections
d = json.load(open(sys.argv[1], encoding="utf-8"))
claims = d.get("claims", [])
COMPARE = re.compile(r"\b(state[- ]of[- ]the[- ]art|SOTA|outperform\w*|best|"
                     r"surpass\w*|beats?|superior|first to|consistently|"
                     r"compared?\s+(?:to|with)|baseline|prior\s+(?:work|art))\b", re.I)
anchors, baselines = [], []
for c in claims:
    t, span = c.get("type"), c.get("text_span", "")
    # the SOTA / outperforms assertion (the anchor for completeness + fairness):
    if t == "comparison" or (t == "scope" and COMPARE.search(span)):
        anchors.append((c["claim_id"], t, c.get("location", {}).get("section", "?"), span[:150]))
    # the baseline SET the paper reports (mechanical; the reviewer decides completeness):
    if t == "baseline":
        baselines.append((c["claim_id"], c.get("location", {}).get("section", "?"), span[:150]))
print(f"ANCHOR (comparison/SOTA) claims: {len(anchors)}   baseline-list claims: {len(baselines)}")
for cid, t, sec, sp in anchors[:40]:
    print(f"  [anchor:{t}] {cid} [{sec}] {sp!r}")
for cid, sec, sp in baselines[:20]:
    print(f"  [baseline] {cid} [{sec}] {sp!r}")
nums = collections.Counter(c.get("type") for c in claims if c.get("type") in ("number", "table_cell"))
mets = collections.Counter((c.get("value") or {}).get("metric") for c in claims
                           if (c.get("value") or {}).get("metric"))
print("VALUE CLAIMS =", dict(nums), "  METRICS (seed the profile row) =", dict(mets))
print("APPLICABLE   =", "yes" if (anchors or baselines) else "no -> write [] and stop")
PY
```

**Branch.** If **APPLICABLE = no** (zero comparison/SOTA/baseline claims), this skill
is **not applicable**: write an empty `baseline-comparison-audit.findings.json`
(`[]`), record a one-line `NOT_APPLICABLE` reason in the trace (Step 7), and stop.
**Silent skip is forbidden** — the orchestrator globs `*.findings.json` and expects
the file to exist. Otherwise record the **anchor claims** (the SOTA/comparison
assertions) and the **reported-baseline list** for the prompts. A purely mechanical
grep helps surface the table/baseline names (do **not** judge completeness here — that
is the reviewer's job):

```bash
LEDGER="<abs path to claims.json from Step 0>"
grep -rInE '\\begin\{tabular|\\caption|baseline|w\.r\.t|vs\.?|\bours?\b' \
    "$(dirname "$LEDGER")" --include='*.tex' 2>/dev/null | head -60
```

## Step 2 — Assemble the candidate expected-baseline set (profile + live search + recency guard)

Determine the benchmark/task from the anchor claims (and the method section), then
build a **candidate expected set with sources** — structured *evidence*, not a
verdict. The recency guard is what stops you from naming a hallucinated or concurrent
baseline as "missing":

Read `reference/domain-profiles.md` now; item 1 looks the task up in its table.

1. **Profile lookup.** If the task is in the per-domain profile above, take its
   expected baseline families (incl. the **floor**) and the matched-budget axis. If
   no row matches → mark the domain `NO_PROFILE`; completeness defaults to
   `needs_external_check`.
2. **Live leaderboard cross-check** (the authoritative source; record the query + the
   top systems + their **dates/venues**):
   ```
   WebSearch: "<benchmark> state-of-the-art <paper/current year> leaderboard"
   WebSearch: "<benchmark> papers with code"
   WebFetch:  <the Papers-with-Code / leaderboard URL>   # top 5–8 systems + their dates
   ```
3. **Recency + existence guard.** For each candidate baseline, record its
   `same_benchmark?` · `published_before_paper?` · `source_url` · `date`. A system
   concurrent with or post-dating the audited paper is a **legitimate omission** (a
   false positive for "missing"), not a flag.

Create the run's trace dir **now** — its first use is the file written just below, so
it must exist before Step 7. Reuse this exact `RUNDIR` in Steps 3–7 (do **not** create
a second one):

```bash
DATE=$(date +%Y-%m-%d); N=1
while [ -d ".aris/traces/baseline-comparison-audit/${DATE}_run$(printf %02d $N)" ]; do N=$((N+1)); done
RUNDIR=".aris/traces/baseline-comparison-audit/${DATE}_run$(printf %02d $N)"; mkdir -p "$RUNDIR"
echo "RUNDIR = $RUNDIR"   # carry this exact path forward (shell state does not persist)
```

Write these facts (not opinions) into `$RUNDIR/expected_baseline_set.json`:

```json
{
  "task": "GSM8K grade-school math (LLM reasoning)",
  "profile_version": "0.1",
  "profile_hit": true,
  "leaderboard_source": "https://paperswithcode.com/sota/arithmetic-reasoning-on-gsm8k  (read <UTC date>)",
  "expected_baselines": [
    {"name": "Self-Consistency CoT", "year": 2023, "same_benchmark": true, "published_before_paper": true, "source": "<url>"},
    {"name": "<recent frontier model> few-shot CoT", "year": 2024, "same_benchmark": true, "published_before_paper": true, "source": "<url>"}
  ],
  "notes": "off-profile or inconclusive search -> completeness becomes needs_external_check, not a guess"
}
```

**Failure handling.** No network / search fails → fall back to the profile alone and
mark every completeness candidate `requires_external_check: true` (you could not
confirm recency/availability). An empty candidate set + `NO_PROFILE` ⇒ skip the
completeness flag and emit a single `needs_external_check` info finding instead.
**Never** phrase the set as "the paper is missing X" — that is the reviewer's call.

## Step 3 — Completeness pass (cross-model, fresh thread) → HP-MISSING-BASELINE

Open a **fresh** `mcp__codex__codex` thread (Reviewer Calling Convention). The
reviewer reads `claims.json` from its `cwd` for the *present* baselines and compares
against your *external* expected-set facts; every finding anchors to a ledger
`claim_id`. Send EXACTLY (fill every `[ ... ]`):

Read the "Step 3 — completeness prompt" block in `reference/reviewer-prompts.md` and send it verbatim, every `[ ... ]` filled.

Persist the raw response to the trace dir (Step 7) **before** parsing. **Failure
handling:** MCP stall → re-invoke the **identical** prompt as a fresh
`mcp__codex__codex` (never `codex-reply`). Prose instead of JSON → the Step 5
validator extracts the outermost `[...]`; if none, re-ask once "Output ONLY the JSON
array." If the web cross-check was unavailable, bias every completeness item toward
`needs_external_check` — never invent a leaderboard entry.

## Step 4 — Fairness + Significance + cross-row Delta pass (cross-model, fresh thread; L2 deepen)

A **separate, new** `mcp__codex__codex` thread for the head-to-head rows. At **L2**
first gather mechanical config/seed facts (paths + raw grep/hash only — no
interpretation, the same executor/reviewer division as `experiment-forensics`);
**skip this block at L0/L1** (there are no configs to read):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
PAPER_DIR="<abs PAPER_DIR from Step 0>"
L="<L from Step 0>"
# (L2 ONLY) per-method budget / tuning / seed asymmetry FACTS — paths + raw hits.
# Guarded: skip entirely at L0/L1 (no configs to read — the reviewer block gets "L<2: ...").
if [ "$L" = "2" ]; then
  grep -rInE 'epochs?|max_steps|learning_rate|\blr\b|batch_?size|seed|n_seeds|num_runs|backbone|warm.?up|sweep|tune|budget' \
      "$PAPER_DIR" --include='*.yaml' --include='*.yml' --include='*.json' --include='*.toml' 2>/dev/null | head -80
  find "$PAPER_DIR" -type f \( -name '*config*' -o -name '*args*' -o -name 'hparams*' \) 2>/dev/null | sort | head -40
  # space-safe and tolerant of zero matches (a bare `shasum $(...)` would hang on no args):
  find "$PAPER_DIR" -maxdepth 3 \( -name '*config*' -o -path '*results*.json' \) 2>/dev/null \
      | head -n 20 | while IFS= read -r ff; do shasum -a 256 "$ff" 2>/dev/null; done
fi
```

Then send EXACTLY (fill every `[ ... ]`):

Read the "Step 4 — fairness + significance + cross-row delta prompt" block in `reference/reviewer-prompts.md` and send it verbatim, every `[ ... ]` filled.

**Deepen at L2.** When `L == 2`, the L2 config facts let the reviewer promote a
text-only suspicion to a confirmed `HP-WEAK-BASELINE` (keep `observability_level_required:
0` if the text already showed the asymmetry; use `2` for asymmetry only the configs
reveal). **Fan-out (optional, breadth).** On `— effort: max` or many comparison rows,
issue this checklist **per comparison entry** as a separate fresh `mcp__codex__codex`
call and concatenate the arrays — never `codex-reply`. Persist each raw reply to the
trace (Step 7). **Failure handling:** identical to Step 3 (fresh identical re-invoke
on stall; re-ask for the strict JSON array on prose; never hand-author findings).

## Step 5 — Validate + anchor + dedup (the anti-hallucination gate)

The executor enforces the **ANCHOR** gate (the one `tools/adjudicate_findings.py`
re-applies, so an anchored finding you keep is not silently rejected downstream) plus
baseline-specific **owned-pattern + delta-dedup + schema-hygiene** pre-filters,
**before** keeping anything. The span must be a verbatim, whitespace-normalized
**substring of** the cited claim (`span in base`, never `base in span` — appending
hallucinated text to a real claim must fail). Pass **every** saved raw reviewer
response (completeness + fairness + any per-entry fan-out files); they merge into one
findings file with one `BC###` namespace:

Run the validator script in `reference/validator.md` verbatim (fill `LEDGER` and pass every saved raw response file). Export `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"` first: variables are substituted in SKILL.md only, not in reference files.

Scope of this gate: **anchoring + owned-pattern + delta-dedup + schema hygiene only**
(schema hygiene = the *presence/validity* of the reviewer's required fields — a
missing/invalid `observability_level_required` or `false_positive_risk` on an
above-info finding fails **closed to info**, never a guessed default). Do **not**
re-implement the adjudicator's verdict-bearing gates (the observability LEVEL
*downgrade* `req > run_level`, the FP-risk *cap*, the surface cap, the verdict) — those
need the run level and belong to `tools/adjudicate_findings.py`, the single decider.
`needs_external_check` findings are pinned to `info` (the honest hand-off carries no
severity weight), never dropped. The remaining judgments are the **reviewer's**, per the
prompt — concurrency/post-dating FP on a missing baseline, a large-gap/significance-
test FP on overlap, the `observability_level_required: 2` tag for config-only
asymmetry; if a kept finding plainly violates one of these, re-run that pass with the
correction noted (never hand-fabricate). **Failure handling.** A `JSONDecodeError`/
empty array for a step means that reviewer reply was malformed → re-run that step with
the strict-JSON reminder. A finding that loses all evidence is **kept as info** (never
silently dropped — the forensic record stays).

Read `reference/worked-examples.md` for three worked findings (a critical HP-MISSING-BASELINE, a needs_external_check hand-off, an L2 HP-WEAK-BASELINE) when you shape the output.

## Step 6 — Emit (one file)

Step 5 wrote the validated array to **`baseline-comparison-audit.findings.json`** (a
bare JSON array conforming to `schemas/finding.schema.json`), in the ledger's
directory. If both passes found nothing — or this skill was not applicable (Step 1) —
the file is `[]`; **write it anyway** (silent skip is forbidden; the orchestrator's
`*.findings.json` glob and the standalone adjudicate command both expect it at a
predictable path). This skill writes **exactly one** findings file: **no second
deterministic file** — unlike `consistency-audit`, baseline runs no deterministic tool
of its own, and it **never re-runs `tools/check_numeric_consistency.py`** (that tool
stamps `skill: consistency-audit`, so re-running it here would double-count under the
orchestrator glob). Its delta dimension is cross-model and deliberately
non-overlapping with consistency-audit's deterministic delta pass.

## Step 7 — Trace (forensic; never silently dropped)

Save every reviewer call under the **same `RUNDIR` created at the start of Step 2**
(`.aris/traces/baseline-comparison-audit/<YYYY-MM-DD>_run<NN>/`). This repo ships no
`save_trace.sh`, so write files directly — reuse that path; do **not** re-run the bump
loop here (it would allocate a second empty dir):

```bash
RUNDIR="<the RUNDIR printed in Step 2>"   # e.g. .aris/traces/baseline-comparison-audit/<date>_run01
mkdir -p "$RUNDIR"                          # idempotent — the dir already exists from Step 2
```

Populate it:

```
.aris/traces/baseline-comparison-audit/<date>_run<NN>/
  run.meta.json                       # {skill, paper_id, run_level_L, profile_version:"0.1", domain, ledger_sha?, generated_at, not_applicable?}
  expected_baseline_set.json          # Step 2 external facts (leaderboard URL + dates + candidate set)
  001-completeness.request.json       # the EXACT Step-3 prompt sent (paths + ledger + sourced facts + checklist)
  001-completeness.response.md        # the FULL raw reviewer response (input to Step 5)
  001-completeness.meta.json          # {model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}
  002-fairness-significance.request.json
  002-fairness-significance.response.md
  002-fairness-significance.meta.json
  # 00N-comparison-<entry>.* for each per-entry fan-out call, if used
```

Each `request.json` is the independence audit trail — it must show the executor sent
only **paths + the ledger + sourced external facts + the checklist**, never a digest
or pre-judgment of the paper. `expected_baseline_set.json` makes the completeness
expectation reproducible (which leaderboard, when, what dates).

## Step 8 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here**: the orchestrator globs every
`*.findings.json`, runs the adjudicator once over the union, and emits `REPORT.md` +
`report.json`. When running this skill **alone**, you may produce the report yourself
— `--ledger` is **required** (it is what verifies each finding quotes a real ledger
span; without it every above-info finding fails closed to `info`):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D/baseline-comparison-audit.findings.json" \
    --ledger "$LEDGER" \
    --paper-id "<PAPER_ID>" --observability-level <L> --taxonomy-version 0.5 \
    --out "$D/baseline.report.json" --md "$D/baseline.REPORT.md"
# prints e.g.: verdict=SOFT_FLAGS crit=0 maj=1 min=2 -> baseline.report.json, baseline.REPORT.md
```

The adjudicator applies, in order: ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE
gates, then computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS,
HARD_FLAGS} (any span-anchored **critical** decidable at `L` → HARD_FLAGS). No model
is in the final decision; this skill rolls up under the `baseline` dimension via
`SKILL_TO_DIMENSION`. `needs_external_check` findings carry no severity weight — they
surface as open questions for a human, never as a flag. *(Use the `baseline.*` output
names when standalone so you do not clobber the orchestrator's combined `report.json`
/ `REPORT.md`.)*

## Output contract

This skill **always** writes, into the ledger's directory:

- `baseline-comparison-audit.findings.json` — a JSON array
  (`schemas/finding.schema.json`); the validated completeness + fairness +
  significance + cross-row delta findings (or `[]`). Each above-info finding carries
  `evidence[].claim_id` + a verbatim `span`, an integer `observability_level_required`,
  a `pattern_id` ∈ {`HP-MISSING-BASELINE`, `HP-WEAK-BASELINE`, `HP-SIG-OVERLAP`,
  `HP-DELTA-ERROR`}, and an honest `false_positive_risk`. Unsettleable completeness
  appears as `verdict_local: needs_external_check` + `requires_external_check: true`,
  never a guessed missing baseline.
- `.aris/traces/baseline-comparison-audit/<date>_run<NN>/` — the external-facts file +
  the raw reviewer call(s).

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 8 / the orchestrator). It writes **no
second deterministic file** and never edits the audited paper.

## Key rules

- **No span → no severity.** Reject unanchored/paraphrased findings to `info` here
  (the adjudicator re-enforces). `span in claim`, whitespace-normalized — never
  `claim in span`. The anchor is a PAPER claim; the expected-set list / leaderboard
  URL / config `file:line` is forensic detail in the description, never the anchor.
- **No profile + inconclusive search ⇒ no guessed "missing baseline".** Hand off as
  `needs_external_check`, anchored to the SOTA claim. A guess is worse than a hand-off.
- **Recency / existence guard.** Confirm a candidate "missing" baseline is real,
  same-benchmark, and **pre-dates** the submission before flagging; concurrent/
  post-dating work is a legitimate omission (FP), not a flag.
- **Asymmetry is the fairness signal.** Unequal budget / tuning / data, mismatched
  backbone/split/protocol, or a missing equal-budget ablation-as-baseline. A standard
  reference number quoted from a baseline's own paper is legitimate (high FP) — note
  the config delta, don't allege. Stated in text → level 0; config-only → level 2.
- **Small gap + thin evidence (no variance/seeds, or single-dataset-only) is a flag to
  CHECK, not proof.** Keep `HP-SIG-OVERLAP` honest: overlapping reported error bars =
  major; merely-absent variance / no seed count reported at all for a small gap =
  minor, FP high; a "consistently/across-the-board" claim resting on a single dataset =
  minor (major only if breadth is the headline), FP high if the claim is scoped to that
  benchmark; a large gap or a reported significance test suppresses it.
- **Delta cross-check, not double-count.** Re-verify only *cross-row* "improves over
  baseline by X%" arithmetic whose operands span a sentence + a table row; never
  re-emit a single-sentence delta (owned by `consistency-audit`'s deterministic pass).
  Baseline never re-runs `check_numeric_consistency.py` (it stamps consistency-audit).
- **Reviewer ≠ adjudicator.** The model proposes findings; `adjudicate_findings.py`
  decides the verdict. This skill emits findings only.
- **Cross-model, fresh thread per dimension/entry.** Reviewer is a different family
  (gpt-5.5 xhigh); completeness and fairness/significance/delta are separate fresh
  `mcp__codex__codex` threads; `codex-reply` is never used (absent from `allowed-tools`).
- **Observability honesty.** Config/budget asymmetry only the repo reveals gets
  `observability_level_required: 2` so a PDF-only run auto-demotes it. You cannot prove
  an undocumented budget gap from a PDF.
- **Stay in lane.** Generic text scope-overclaim → `consistency-audit`
  (`HP-SCOPE-INFLATE`); code/result fraud → `experiment-forensics` (L2); citation
  issues → `citation-forensics`; surface/AI-flavor → `presentation-signals`. This
  skill **never** emits an F-pattern.
- **Discrepancy, not accusation.** Output asks a reviewer to *check/ask*, never to
  reject; the tool audits comparison integrity, not authorship.
- **Detect-only.** Never edit the audited paper (reviewer sandbox is read-only).
- **Reproducible.** Same ledger + same findings → same verdict; the leaderboard facts
  (with URL + date) are traced so the completeness expectation is auditable.

## When NOT to use this skill

Read `reference/routing.md` ("When NOT to use this skill") before running if the request is outside baseline comparisons; it lists where each such request goes.

## Review tracing

Forensic policy — never silently skipped. The exact `RUNDIR` layout and the
reviewer-independence audit-trail rule for each `request.json` (only paths + ledger +
sourced external facts + checklist were sent — no digest, no pre-judgment) are
specified once in **Step 7**; follow it for every `mcp__codex__codex` call
(completeness, fairness, and any per-entry fan-out).
