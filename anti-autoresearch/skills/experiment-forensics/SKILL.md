---
name: experiment-forensics
description: "Checks paper numbers and method against released code and results: fake ground truth, self-normalized scores, phantom or too-clean results, placeholder data, missing code/prompts. Needs evidence-ledger first; without repo + results, info notes only. Triggers: \"audit the results\", \"check the eval code\", \"实验诚实度\"."
argument-hint: [paper-dir | repo-dir]
allowed-tools: Bash(*), Read, Write, Grep, Glob, mcp__codex__codex
---

# Experiment Forensics — are the reported results what the code computes?

Audit experiment integrity for: **$ARGUMENTS** (a paper-dir or repo-dir; use an
ABSOLUTE path — it is referred to as `TARGET` below). Emit span-anchored
`experiment-forensics.findings.json`.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the observability level rises (a repo or result files arrive → L2).

Read `reference/rationale.md` for the ARIS lineage, the ten failure modes this skill targets (why it exists) and the two independence axes (executor ≠ reviewer, reviewer ≠ adjudicator); it is background, not procedure.

## How this differs from the other auditors (route correctly)

This skill asks one question: are the reported numbers what the eval code computes (L2)? Text-only contradiction and text scope go to `consistency-audit`;
"first / SOTA" external truth to `baseline-comparison-audit` + `citation-forensics` (`needs_external_check`); evaluation-design validity (leakage, LLM-as-judge)
to `eval-design-forensics`; surface tells to `presentation-signals`. An LLM that produces ground-truth labels stays here as `HP-FAKE-GT`.
Read `reference/routing.md` for the full auditor table and hand-off list when a finding might belong elsewhere.

## Pipeline role + the anchoring model (read before running)

This is an **auditor** skill in the integrity-forensics pipeline
(`references/integrity-forensics-contract.md`):

```
/evidence-ledger  →  claims.json (+ artifact_manifest.json, observability level L)
                          │
       experiment-forensics  ── reads the ledger, PROPOSES findings ──►  experiment-forensics.findings.json
                          │
   tools/adjudicate_findings.py  (deterministic; the ONLY thing that computes a verdict)
```

- It **reads the ledger**, it **never re-reads the raw paper to invent structure**,
  and it **never computes the overall verdict** — the orchestrator runs
  `tools/adjudicate_findings.py` for that. This skill stops at emitting findings.
- **The anchor is always a PAPER claim.** Every above-info finding cites a ledger
  `claim_id` and quotes a **verbatim span of that claim's `text_span`** (the paper
  number/scope/method sentence it undermines). The eval-code smoking gun
  (`src/eval.py:88`) is **not** a ledger claim, so it lives in the finding's
  `description` / `recommended_reviewer_action`, never as the anchor. No paper claim
  to anchor to ⇒ the finding cannot rise above `info`. (See worked examples.)
- **Observability caps severity.** Findings declare `observability_level_required`.
  Every code/result-level pattern is decidable only at **L2**; at L0/L1 it is emitted
  as `info` (Step 2). `tools/adjudicate_findings.py` is the structural backstop — any
  `observability_level_required` above the run's level is demoted to `info`.

## Constants & Reviewer Calling Convention

- **REVIEWER = `mcp__codex__codex`** — model `gpt-5.5`, `config:
  {"model_reasoning_effort": "xhigh"}`, `sandbox: read-only`, `cwd` = `TARGET` (the
  repo/paper dir, where the code + results live). A **different model family** from
  the executor (Claude). One **fresh thread per audit pass**; **never
  `mcp__codex__codex-reply`** across passes (the bias guard — reply is deliberately
  absent from `allowed-tools`). See `references/reviewer-independence.md`.
- **PATTERNS_OWNED** (must match `references/hack-pattern-taxonomy.md`,
  `taxonomy_version 0.5`): `HP-FAKE-GT`, `HP-SELF-NORM`, `HP-PHANTOM-RESULT`,
  `HP-DEAD-METRIC`, `HP-SCOPE-INFLATE` (verified form), `HP-METHOD-DRIFT` (L2
  confirm), `HP-SUSPICIOUS-REGULARITY` (L2 confirm), `HP-PLACEHOLDER-DATA` (L2),
  `HP-RESULT-ARTIFACT-MISMATCH` (L2), `HP-MISSING-REPRO-ARTIFACT` (verdict-bearing
  at L2 — absence noticeable at L0/L1 but surfaced as info there, confirmed at L2).
- **ROOT** = `"${CLAUDE_PLUGIN_ROOT}/support"`; **L** =
  `observability_level` from `artifact_manifest.json`; **OUTPUT** =
  `experiment-forensics.findings.json` (a bare JSON array).
- **FILES** (all under `TARGET`, next to `claims.json`): the only output is
  `experiment-forensics.findings.json`; the reviewer handoff is
  `.aris/last_reviewer_response.txt`; traces live in
  `.aris/traces/experiment-forensics/<date>_run<NN>/`.
- ⚠️ **Shell state does not persist between Bash calls** (cwd + env reset each call).
  Every block below re-resolves `ROOT` and `TARGET` at its top and reads `L` /
  `paper_id` from the manifest/ledger. **Never** rely on a variable from an earlier
  block, and **never `cd` into `TARGET`** (it would break `ROOT` resolution).

Division of labor (`references/reviewer-independence.md`):

- **Executor (Claude)** locates the ledger, lists artifact paths, gathers *mechanical
  facts* (file listings, literal-string greps, hashes), passes **paths + the ledger +
  the checklist** to the reviewer, validates the reviewer's spans, and writes the
  findings file. It never summarizes file contents, pre-judges, or leaks an opinion.
- **Reviewer (codex / gpt-5.5)** reads `./claims.json` and the code/result files
  directly from its `cwd`, proposes findings, and self-reports `false_positive_risk`.
  **Told:** the artifact paths, the ledger, the per-pass checklist, the level.
  **Not told:** any other auditor's findings, the executor's hunches, or "this looks
  AI-generated" — the tool audits integrity, not authorship.
- **One fresh thread per pass.** The A–F checklist is a single call; the optional
  G/H passes are each a NEW thread. If codex stalls (long sessions can hang),
  re-invoke the **same** prompt in a fresh thread — never `codex-reply`.

## Step 1 — Preflight: resolve root, level, paper_id (self-contained)

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
TARGET="$ARGUMENTS"          # paper-dir or repo-dir — ABSOLUTE path
case "$TARGET" in /*) ;; *) echo "FATAL: TARGET must be a non-empty ABSOLUTE path (got: '$TARGET'). Pass the paper/repo dir as an absolute path."; exit 1 ;; esac

# Toolchain must be reachable (invariant: ROOT = the Anti-Autoresearch checkout).
test -f "$ROOT/tools/build_manifest.py" || { echo "FATAL: Anti-Autoresearch tools not under $ROOT. Run this skill from inside the Anti-Autoresearch checkout (or point ROOT at it)."; exit 1; }

# The ledger is mandatory and is produced by /evidence-ledger. Do NOT invent it.
test -f "$TARGET/claims.json" || { echo "FATAL: $TARGET/claims.json missing. Run /evidence-ledger on $TARGET first (experiment-forensics reads the ledger)."; exit 1; }

# artifact_manifest.json derives the level. Build it with the real tool if absent
# (exact flags — confirm via: python3 "$ROOT/tools/build_manifest.py" --help).
if [ ! -f "$TARGET/artifact_manifest.json" ]; then
  PID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["paper_id"])' "$TARGET/claims.json")
  python3 "$ROOT/tools/build_manifest.py" --paper-id "$PID" --dir "$TARGET" --out "$TARGET/artifact_manifest.json"
fi

# Read the level (L) + paper_id. The manifest decides L; never override it.
python3 - "$TARGET" <<'PY'
import json, sys
t = sys.argv[1]
m = json.load(open(f"{t}/artifact_manifest.json")); c = json.load(open(f"{t}/claims.json"))
print(f"paper_id={c['paper_id']}  observability=L{int(m['observability_level'])}  "
      f"(rule: repo+results->L2, latex/no-results->L1, pdf/text-only->L0)")
PY
mkdir -p "$TARGET/.aris/traces/experiment-forensics"
```

**Branch on L** (read from the echo above; `references/observability-levels.md`):
`L < 2` → **Step 2** (info-only) → **Step 6**. `L == 2` (or 3 — treat as 2, never
re-run code) → **Steps 3–6**.

**Failure handling.** No `claims.json` ⇒ stop (the FATAL above); the ledger has not
been built and this skill never invents one — tell the user to run `/evidence-ledger`
first. Never claim a higher level than the artifacts support: L is derived
deterministically (`repo + results → L2`; `latex, no results → L1`; `pdf/text only →
L0`), and the manifest decides it — you do not override it.

## Step 2 — L0 / L1: info-only "could-not-verify" signals (the honesty backbone)

At L0/L1 there is **no eval code and no result files**, so you **cannot decide any
experiment-integrity pattern**. Do **not** assert fraud, and do **not** duplicate the
L0 text-scope check — `consistency-audit` owns scope from the manuscript. This skill's
only job here is to mark, for the human, which numbers become checkable **if a repo is
released**. Generate the signals deterministically from the ledger:

Run the L0/L1 signal script in `reference/l0-signals.md` verbatim (it writes `experiment-forensics.findings.json`). Export `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}" ARGUMENTS="$ARGUMENTS"` first: variables are substituted in SKILL.md only, not in reference files.

Each emitted finding has the shape below (info-only, `observability_level_required:2`,
empty `evidence` permitted **only** for info). Then go to **Step 6** (no reviewer call
needed at L<2 — these are deterministic pointers, not judgments):

The example shape is in `reference/l0-signals.md` ("Example L0 signal").

## Step 3 — L2: collect artifacts (executor — paths + mechanical FACTS only)

You (Claude) gather inputs and **mechanical facts**; you do **not** interpret,
summarize, or pre-judge them (`references/reviewer-independence.md`). Listing what
exists and grepping for a literal string are reproducible facts, not judgments — the
same division `citation-forensics` uses for existence vs. context. Do not `cd`; use
absolute `$TARGET/...` paths.

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; TARGET="$ARGUMENTS"
mkdir -p "$TARGET/.aris"

# (a) Eval / metric / test / score / benchmark / runner code + configs -> eval_paths.txt
find "$TARGET" -type f \( -name '*eval*.py' -o -name '*metric*.py' -o -name '*test*.py' \
   -o -name '*score*.py' -o -name '*benchmark*.py' -o -name 'run*.py' -o -name 'main.py' \
   -o -name '*.yaml' -o -name '*.toml' \) 2>/dev/null | sort > "$TARGET/.aris/eval_paths.txt"

# (b) Result files the paper's numbers should live in -> result_paths.txt
find "$TARGET/results" "$TARGET/outputs" "$TARGET/logs" -type f \( -name '*.json' -o -name '*.csv' \) 2>/dev/null | sort > "$TARGET/.aris/result_paths.txt"

# (c) Likely GT / reference loaders (FACT for the reviewer; do NOT judge) -> gt_grep.txt
grep -rInE 'ground.?truth|reference|target|label|gold|gt_|normaliz' --include='*.py' "$TARGET" 2>/dev/null | head -60 > "$TARGET/.aris/gt_grep.txt"

# (d) Phantom-result FACTS: grep EACH headline number from the ledger (no hardcoded token) -> number_grep.txt
python3 - "$TARGET" > "$TARGET/.aris/number_grep.txt" <<'PY'
import json, subprocess, sys
t = sys.argv[1]
claims = json.load(open(f"{t}/claims.json"))["claims"]
toks, seen = [], set()
for c in claims:
    if c.get("type") not in ("number", "comparison"): continue
    v = c.get("value") or {}
    for tok in (str(v.get("raw") or ""), ("" if v.get("normalized") is None else repr(v["normalized"]))):
        tok = tok.strip().rstrip("%").strip()
        if tok and tok not in seen:
            seen.add(tok); toks.append((c["claim_id"], tok))
for cid, tok in toks:
    hits = subprocess.run(["grep", "-rIn", "--", tok, f"{t}/results", f"{t}/outputs", f"{t}/logs"],
                          capture_output=True, text=True).stdout.strip()
    print(f"### {cid} token={tok!r}: {'FOUND' if hits else 'NOT FOUND under results/outputs/logs'}")
    if hits: print(hits)
PY

# (e) Reproducibility anchors: hash EVERY discovered eval script + result file -> hashes.txt
{ while IFS= read -r f; do [ -n "$f" ] && shasum -a 256 "$f"; done < "$TARGET/.aris/eval_paths.txt"
  while IFS= read -r f; do [ -n "$f" ] && shasum -a 256 "$f"; done < "$TARGET/.aris/result_paths.txt"; } 2>/dev/null > "$TARGET/.aris/hashes.txt"

# (f) Ledger claim subset the reviewer must anchor to -> claim_subset.json
python3 - "$TARGET" > "$TARGET/.aris/claim_subset.json" <<'PY'
import json, sys
t = sys.argv[1]
KEEP = {"number", "comparison", "scope", "method", "artifact_ref"}
claims = json.load(open(f"{t}/claims.json"))["claims"]
print(json.dumps([{"claim_id": c["claim_id"], "type": c["type"],
                   "text_span": c.get("text_span", ""), "location": c.get("location", {})}
                  for c in claims if c.get("type") in KEEP], indent=2, ensure_ascii=False))
PY

# (g) Placeholder / dummy / fake-data markers (FACT for the reviewer; do NOT judge) -> placeholder_grep.txt
grep -rInE 'placeholder|dummy|\bfake\b|fake data for plotting|mock(ed|_|\b)|TODO.*(replace|real|actual).*data|FIXME.*data|hard.?cod(e|ed)|np\.random\.|numpy\.random\.|random\.(rand|randn|randint|uniform|normal)|synthetic.*(demo|example|plot)' \
   --include='*.py' --include='*.ipynb' --include='*.r' --include='*.R' "$TARGET" 2>/dev/null | head -80 > "$TARGET/.aris/placeholder_grep.txt"

# (h) Repro-artifact inventory: do the runnable artifacts the results would need exist? (FACT; presence listing only) -> repro_inventory.txt
{ echo "## code (*.py):";        find "$TARGET" -type f -name '*.py' 2>/dev/null | head -20
  echo "## notebooks (*.ipynb):"; find "$TARGET" -type f -name '*.ipynb' 2>/dev/null | head -20
  echo "## prompts/templates:";   find "$TARGET" -type f \( -iname '*prompt*' -o -iname '*template*' -o -name '*.jinja' -o -name '*.j2' \) 2>/dev/null | head -40
  echo "## configs:";             find "$TARGET" -type f \( -name '*.yaml' -o -name '*.yml' -o -name '*.toml' -o -name '*.cfg' -o -name '*config*.json' -o -name '*.ini' \) 2>/dev/null | head -40
  echo "## env/deps:";            find "$TARGET" -type f \( -name 'requirements*.txt' -o -name 'environment*.yml' -o -name 'pyproject.toml' -o -name 'Pipfile' -o -name 'setup.py' -o -name '*.lock' \) 2>/dev/null | head -20
  echo "## run instructions:";    find "$TARGET" -type f \( -iname 'README*' -o -iname 'RUN*' -o -name 'Makefile' -o -name '*.sh' \) 2>/dev/null | head -20; } > "$TARGET/.aris/repro_inventory.txt"

# Machine validation gate: NO eval scripts AND NO result files => the manifest's L2 is
# unsupported -> re-derive the level (then run Step 2 if it drops below 2).
EV=$(grep -c . "$TARGET/.aris/eval_paths.txt"); RS=$(grep -c . "$TARGET/.aris/result_paths.txt")
echo "eval_scripts=$EV result_files=$RS  (paths + facts + claim_subset written under $TARGET/.aris/)"
if [ "$EV" -eq 0 ] && [ "$RS" -eq 0 ]; then
  echo "L2 UNSUPPORTED (no eval scripts, no result files) — re-deriving level:"
  python3 "$ROOT/tools/build_manifest.py" --paper-id "$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["paper_id"])' "$TARGET/claims.json")" --dir "$TARGET" --out "$TARGET/artifact_manifest.json"
fi
```

Re-read L (Step 1's reader); if it is now `< 2`, run **Step 2** instead. The files
written above (`eval_paths.txt`, `result_paths.txt`, `gt_grep.txt`, `number_grep.txt`,
`placeholder_grep.txt`, `repro_inventory.txt`, `hashes.txt`, `claim_subset.json`, all
under `$TARGET/.aris/`) are the reviewer's
inputs — inline their literal contents into the Step 4 prompt. **Do not summarize file
CONTENTS** — the reviewer reads the code/results directly via its `cwd`; you only pass
paths, raw greps/hashes, and the claim subset.

## Step 4 — L2: cross-model code audit (reviewer ≠ adjudicator)

Send paths + the ledger subset + the checklist to a **fresh** `mcp__codex__codex`.
The reviewer reads the eval code line-by-line and **proposes** findings; it does not
grade the paper. Call with: `model: "gpt-5.5"`, `config:
{"model_reasoning_effort": "xhigh"}`, `sandbox: "read-only"`, `cwd: "<TARGET>"` (so
it can read `./claims.json`, `./src/...`, `./results/...` directly), `prompt:` the
block below. Assemble that `prompt:` by inlining the Step 3 `.aris/` files at the
`[inline …]` markers (read each, paste its literal contents — paths + raw facts + the
claim subset, never a summary). **One fresh thread; never `codex-reply`.**

Read the "Step 4 — A–F checklist prompt" block in `reference/reviewer-prompts.md` and send it verbatim, with the Step 3 files inlined at its `[inline …]` markers.

**Additional focused passes** (each a NEW fresh thread — never `codex-reply`), run
only when the relevant ledger claims exist:

Read `reference/reviewer-prompts.md` ("Additional focused passes G–K") for each pass's trigger, pattern, question, FP cases and anchor; send each as its own fresh thread.

**Save the handoff + failure handling.** Write the reviewer's full raw reply to
`"$TARGET/.aris/last_reviewer_response.txt"` (use `Write`) before validating, and
**also** preserve each call's prompt + reply as a per-call pair that never clobbers
across batches: `Write` them to
`"$TARGET/.aris/traces/experiment-forensics/pending/prompt_<NN>.txt"` and
`".../response_<NN>.txt"` (NN = 01, 02, … one per fresh thread; Step 6 moves `pending/`
into the dated run dir). If the codex call stalls or errors (long sessions can hang),
re-invoke the **same** prompt in a **fresh** thread (never `codex-reply`); if it still
fails, write `[]` to `experiment-forensics.findings.json` and proceed — never fabricate
findings. If the repo is too large for one thread, split the result files into batches,
run one **fresh** thread per batch (same prompt, different file lists), overwrite
`last_reviewer_response.txt` with that batch's reply, and run Step 5 once per batch (the
validator merges + dedupes into the output) — the per-call `pending/` files keep every
batch's raw trace.

## Step 5 — Validate every reviewer finding (the executor gate)

The reviewer proposes; **you verify before keeping**. This mirrors the adjudicator's
`_anchored` check exactly (`span` is a whitespace-normalized *substring of* the ledger
claim, never the reverse), reads `L` from the manifest (not a persisted variable),
extracts the JSON array robustly from the raw reply, re-gates any previously-saved
findings together with the new ones, and merges + re-ids (so no stale above-info
survives a multi-batch merge):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; TARGET="$ARGUMENTS"
python3 - "$TARGET" "$TARGET/.aris/last_reviewer_response.txt" <<'PY'
import json, re, sys
t, resp = sys.argv[1], sys.argv[2]
OUT = f"{t}/experiment-forensics.findings.json"
L = int(json.load(open(f"{t}/artifact_manifest.json"))["observability_level"])
claims = {c["claim_id"]: c.get("text_span", "")
          for c in json.load(open(f"{t}/claims.json"))["claims"] if c.get("claim_id")}
OWNED = {"HP-FAKE-GT","HP-SELF-NORM","HP-PHANTOM-RESULT","HP-DEAD-METRIC",
         "HP-SCOPE-INFLATE","HP-METHOD-DRIFT","HP-SUSPICIOUS-REGULARITY",
         "HP-PLACEHOLDER-DATA","HP-RESULT-ARTIFACT-MISMATCH","HP-MISSING-REPRO-ARTIFACT"}
SEV = {"info":0,"minor":1,"major":2,"critical":3}
norm = lambda s: " ".join((s or "").split())

def extract(x):                       # robust: fenced block -> whole -> first [...]
    m = re.search(r"```(?:json)?\s*(\[.*\])\s*```", x, re.S)
    for s in ([m.group(1)] if m else []) + [x]:
        try: return json.loads(s)
        except Exception: pass
    i, j = x.find("["), x.rfind("]")
    if 0 <= i < j:
        try: return json.loads(x[i:j+1])
        except Exception: pass
    return None

try: raw = open(resp, encoding="utf-8").read()
except Exception: raw = ""
proposed = extract(raw)
if proposed is None:
    print("PARSE-FAIL: no JSON array in reviewer response; merging nothing new."); proposed = []
if isinstance(proposed, dict): proposed = proposed.get("findings", [])

try: base = json.load(open(OUT))
except Exception: base = []

gated = []                                                        # re-gate BASE + new together
for f in base + proposed:
    f["skill"] = "experiment-forensics"
    f.setdefault("title", f.get("pattern_id", "experiment-forensics finding"))
    f.setdefault("verdict_local", "needs_external_check")
    f.setdefault("observability_level_required", 2)
    f["evidence"] = [ev for ev in (f.get("evidence") or [])
                     if ev.get("claim_id") and (ev.get("span") or "").strip()]
    sev, notes = (f.get("severity", "info") if f.get("severity") in SEV else "info"), []
    if L < 2 and sev != "info":                                  # (1) L<2 => info-only
        sev = "info"; f["observability_level_required"] = 2; notes.append("L<2-info-only")
    if f.get("pattern_id") and f["pattern_id"] not in OWNED and sev != "info":  # (2) owned pattern
        sev = "info"; notes.append("pattern-not-owned")
    req = f.get("observability_level_required")                  # (3) observability gate
    if sev != "info" and not (type(req) is int and 0 <= req <= 3):
        sev = "info"; notes.append("undeclared-observability")
    elif sev != "info" and req > L:
        sev = "info"; notes.append(f"obs(req{req}>run{L})")
    if sev != "info":                                            # (4) ANCHOR gate
        ok = any(ev.get("claim_id") in claims and norm(ev.get("span"))
                 and norm(ev["span"]) in norm(claims[ev["claim_id"]])
                 for ev in f["evidence"])
        if not ok: sev = "info"; notes.append("unanchored")
    if sev in ("critical","major") and not any((ev.get("span") or "").strip() for ev in f["evidence"]):
        sev = "info"; notes.append("no-span")                    # (5) high sev needs a span
    f["severity"] = sev; f.setdefault("false_positive_risk", "medium")
    if notes: f["_executor_demotions"] = notes
    gated.append(f)

seen, merged = set(), []                                          # dedupe (base already re-gated)
for f in gated:
    e0 = (f.get("evidence") or [{}])[0]
    key = (f.get("pattern_id"), e0.get("claim_id"), e0.get("span"), f.get("title"))
    if key in seen: continue
    seen.add(key); merged.append(f)
for k, f in enumerate(merged, 1): f["finding_id"] = f"EF{k:03d}"  # re-id sequentially
json.dump(merged, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(f"kept={len(merged)} above_info={sum(1 for x in merged if x['severity']!='info')} -> {OUT}")
PY
```

**The executor never re-grades a finding's severity by hand** (reviewer ≠ adjudicator:
semantic FP calls belong to the reviewer, the verdict to `tools/adjudicate_findings.py`
— the deterministic gates above are the only severity changes the executor makes). The
FP cases below are already in the Step 4 checklist as the "FP:" clauses; the reviewer
suppresses them at proposal time via `false_positive_risk` / `verdict_local` / `info`.
If a proposed finding clearly matches one of them but the reviewer did **not** down-rank
it, do **not** hand-edit the verdict — re-run Step 4 in a fresh thread so the *reviewer*
re-judges:

- **Eval-type ⇒ FP:** a **labeled** `synthetic_proxy` / `self_supervised_proxy` is
  **not** `HP-FAKE-GT`.
- **HP-SELF-NORM FP:** standard min–max across **all** methods (incl. baselines), or
  raw+normalized both shown.
- **HP-PHANTOM-RESULT FP:** the file was renamed/moved but is present, or the number is
  a cited external reference.
- **HP-SUSPICIOUS-REGULARITY:** `false_positive_risk: high` by default; never a
  "fabricated" grade — a *prompt to check*.
- **HP-PLACEHOLDER-DATA FP:** a clearly-labeled toy example / unit-test fixture that feeds
  NO reported result is not a flag.
- **HP-RESULT-ARTIFACT-MISMATCH FP:** seed / version / hardware variance within a *stated*
  tolerance, or a documented post-hoc correction.
- **HP-MISSING-REPRO-ARTIFACT FP:** a genuinely theoretical paper (no empirical claim to
  reproduce), or double-blind submission norms (treat as a camera-ready expectation →
  lower severity / `needs_external_check`).

The only executor-side edits to `experiment-forensics.findings.json` are **mechanical,
non-semantic** provenance stamps: set `reviewer: {"model":"gpt-5.5","reasoning":"xhigh",
"thread_id":<id>,"deterministic":false}` and, where useful, `evidence[].artifact_hash`
= the ledger claim's `evidence_anchor` (the code-file sha goes in the description).
Severity is never hand-edited up or down.

**An empty array is a valid, honest output** — if every proposed finding was demoted
or none was proposed, `experiment-forensics.findings.json` may be `[]`.

Read `reference/worked-examples.md` for a worked L2 finding (the full, copyable shape) when you check the output.

## Step 6 — Emit, cross-reference, trace

The validated array is already written to **`$TARGET/experiment-forensics.findings.json`**
(a bare JSON array conforming to `schemas/finding.schema.json`, re-id'd `EF001…`).
**No verdict here** — the orchestrator runs the adjudicator next. Each code-level
finding already names, via its `claim_id`, the paper claim it undermines, so the
report can show "this number ↔ this code problem" — keep that linkage intact.

**Trace** every reviewer call (forensic — never silently dropped):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; TARGET="$ARGUMENTS"
DATE=$(date +%Y-%m-%d); N=1
BASE="$TARGET/.aris/traces/experiment-forensics"
while [ -d "$BASE/${DATE}_run$(printf %02d $N)" ]; do N=$((N+1)); done
RUNDIR="$BASE/${DATE}_run$(printf %02d $N)"; mkdir -p "$RUNDIR"
# Move every per-call prompt_<NN>.txt / response_<NN>.txt pair (written in Step 4) into
# the dated run dir, so prompts + ALL batch replies are preserved (no clobber):
if [ -d "$BASE/pending" ]; then mv "$BASE/pending/"* "$RUNDIR/" 2>/dev/null; rmdir "$BASE/pending" 2>/dev/null; fi
# Fallback: also keep the last raw reply (covers a single-call run that skipped pending/):
cp "$TARGET/.aris/last_reviewer_response.txt" "$RUNDIR/reviewer_response.txt" 2>/dev/null
python3 -c 'import json,sys;print("observability_level", json.load(open(sys.argv[1]))["observability_level"])' "$TARGET/artifact_manifest.json" > "$RUNDIR/level.txt"
ls -1 "$RUNDIR"
```

Then print a one-screen summary (no verdict):

```
🔬 Experiment Forensics — L<L>  (paper_id=<id>)
  findings: <N> total, <M> above info
  <EF0xx> <severity> <pattern_id> — <one-line title>
  Output: $TARGET/experiment-forensics.findings.json  (proposals only)
  Verdict: NOT computed here — handed to tools/adjudicate_findings.py via the orchestrator.
```

For reference only — **the orchestrator (not this skill)** later runs (note
`--ledger` is REQUIRED: it is what re-verifies each finding quotes a verbatim ledger
span; without it every above-info finding fails closed to `info`):

```bash
# DO NOT run here — this is the orchestrator's job.
python3 "$ROOT/tools/adjudicate_findings.py" --findings "$TARGET"/*.findings.json \
    --ledger "$TARGET/claims.json" --paper-id <id> --observability-level <L> \
    --taxonomy-version 0.5 --out "$TARGET/report.json" --md "$TARGET/REPORT.md"
```

## Output contract

- `$TARGET/experiment-forensics.findings.json` — array of `finding` objects
  (`schemas/finding.schema.json`). At L0/L1: `info`-only,
  `observability_level_required:2`, `requires_external_check:true`. At L2:
  span-anchored `critical`/`major`/`minor`/`info` with honest `false_positive_risk`.
  `[]` is a valid clean result. This skill writes **no** `report.json` / `REPORT.md`.
- `$TARGET/.aris/traces/experiment-forensics/<date>_run<NN>/` — raw reviewer
  prompt(s) + response(s) + the level used.

## Key rules

- **L0/L1 ⇒ no fraud verdicts.** Below L2 this skill emits **only** info-level "needs
  code" signals (`observability_level_required:2`); the validator and the adjudicator
  both pin them to `info`. This is the honesty backbone.
- **The anchor is a PAPER claim.** Every above-info finding quotes a verbatim span of
  a real ledger claim; the eval-code `file:line` is forensic detail in the
  description, never the anchor. Unanchored ⇒ `info`.
- **Labeled proxies are legitimate.** A labeled `synthetic_proxy` / self-supervised-
  by-design eval is **not** `HP-FAKE-GT`. Honor the eval-type classification.
- **Executor collects paths + mechanical facts; the reviewer judges the code.** No
  summaries, hunches, or "this is AI-generated" leak into the prompt
  (`reviewer-independence.md`).
- **Reviewer ≠ adjudicator.** This skill proposes findings; only
  `tools/adjudicate_findings.py` computes the verdict. Never emit a verdict here.
- **Fresh thread per pass; never `codex-reply`** (omitted from `allowed-tools` on
  purpose — the bias guard).
- **Discrepancy, not accusation.** `description` and `recommended_reviewer_action`
  ask a reviewer to *check/ask*, never "reject" or "the authors faked X".
- **Not an AI-text classifier.** "Results look too clean" is `HP-SUSPICIOUS-REGULARITY`
  — high-FP, only `major` when the *result files* contradict the table (L2); a bare
  "looks fake" from a table is deferred to `consistency-audit`. Never infer authorship
  or misconduct from surface impressions (those live, capped at minor, in
  `presentation-signals`).
- **`pattern_id` ∈ taxonomy v0.4 only** (`PATTERNS_OWNED`); the taxonomy is a
  post-hoc mapping layer, not the detector.
- **Detect-only.** Never edit the audited paper or repo; the only files this skill
  writes are its own `findings.json` and trace artifacts.

## When NOT to use this skill

Read `reference/routing.md` ("When NOT to use this skill") before running if the request is a verdict, a fraud claim at L0/L1, a run without `claims.json`, a text-only or baseline question, or authorship; it lists where each goes.

## Review tracing

After each `mcp__codex__codex` call, save the trace following ARIS Policy C (forensic;
never silently skip): write the exact prompt, the raw response, and the observability
level into `$TARGET/.aris/traces/experiment-forensics/<date>_run<NN>/`, as set up in
Step 6. Traces are the audit trail for a reproducible, defensible report and the
evidence that reviewer-independence held (the executor passed only paths + the ledger,
not summaries).
