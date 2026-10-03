---
name: anti-autoresearch
description: "Full integrity forensic sweep of a paper (dir, PDF or arXiv id), especially autoresearch/AI-Scientist output: evidence ledger, all auditors, report with a deterministic verdict. Detect-only; audits integrity, not authorship. Triggers: \"integrity audit this paper\", \"forensic review\", \"audit a submission\", \"审一篇投稿的诚信\"."
argument-hint: [paper-dir | pdf-path | arxiv-id]
allowed-tools: Bash(*), Read, Write, Grep, Glob, Skill, WebSearch, WebFetch, mcp__codex__codex, mcp__mcp-dblp__search, mcp__mcp-dblp__fuzzy_title_search, mcp__mcp-dblp__get_venue_info
---

# /anti-autoresearch — the orchestrator

Run a full substantive-integrity forensic pass on **$ARGUMENTS** and hand a human
reviewer / area chair an evidence-first Integrity Forensics Report.

> 🔒 **External cadence: the verdict is not a poll.** The pipeline is the
> verdict-producing path — its output changes only when the **paper / repo / ledger**
> changes, not with the clock. **Do not** wrap `/anti-autoresearch` (or any auditor
> sub-skill) in `/loop` / `/schedule` / `CronCreate` to "re-check". A heartbeat may
> only *wait on* the **external** steps that precede the verdict (an arXiv download, a
> citation web lookup) — never re-fire the adjudicated verdict, and never "decide the
> paper is fine now." Re-run the sweep when the inputs change; that is the only honest
> trigger.

Read `reference/rationale.md` for background: why this orchestrator exists and how it is the outward-facing dual of ARIS.

## Pipeline role (what this run does, and never does)

The one-page stage diagram (ingest → ledger → auditors → memos → adjudicate → present) is in `reference/pipeline-diagram.md`.

- **Auditors propose; the adjudicator decides.** No auditor (and not this orchestrator)
  ever computes `overall_verdict`; only `tools/adjudicate_findings.py` does, by fixed
  rules (`references/reviewer-independence.md` Layer 2; `DESIGN.md` §3).
- **Detect-only.** No step ever edits the audited paper or repo. This is a third-party
  forensics tool, never a co-author (no `Edit` is granted; the reviewer sandbox is
  `read-only`).
- **Observability caps everything.** L0 (PDF-only) / L1 (source) **cannot** assert
  code/result-level fraud — those need L2 (repo + results). The adjudicator demotes any
  finding above the run's level (`references/observability-levels.md`; `DESIGN.md` §4).

## Constants & conventions

```
REVIEWER_MODEL     = gpt-5.5  (via mcp__codex__codex) — a DIFFERENT model family from the executor (Claude)
REVIEWER_REASONING = xhigh    — always; the effort knob never lowers reviewer quality
REVIEWER_SANDBOX   = read-only — detect-only; the reviewer never mutates the paper
THREAD_POLICY      = FRESH mcp__codex__codex per dimension / per cited key; NEVER codex-reply across them
                     (codex-reply is deliberately NOT in allowed-tools — the bias guard)
RUN_THREADS        = serial   — one codex thread at a time; concurrent codex MCP calls can hang
LEDGER_VERSION     = 0.1       (stamped by tools/build_claim_ledger.py)
TAXONOMY_VERSION   = 0.5       (references/hack-pattern-taxonomy.md; 46 integrity patterns A–H + 13 AIS impressions + 2 ADV advisory; stamped into every report)
OBSERVABILITY      = derived   L0 (pdf/text) · L1 (latex, no results) · L2 (repo + results); L3 NEVER (no reproduction)
ADJUDICATOR        = deterministic-rules-v0   (tools/adjudicate_findings.py — the ONLY verdict source)
DETECT_ONLY        = true · EMITS_VERDICT = true (computed by code, not by a model)
REAL TOOLS (resolve ROOT="${CLAUDE_PLUGIN_ROOT}/support"):
   tools/build_manifest.py · tools/build_claim_ledger.py · tools/check_numeric_consistency.py
   · tools/check_presentation.py · tools/adjudicate_findings.py   (confirm flags with --help; never invent flags)
OUTPUTS (in PAPER_DIR) — artifact_manifest.json · claims.json · <skill>.findings.json (+ *.deterministic.findings.json)
   · adversarial-case-builder.memo.md · report.json · REPORT.md · .aris/traces/<skill>/<date>_run<NN>/
```

**Overrides** (pass after `—`): `effort: balanced` (default) | `max` (auditors fan the
checklist into more fresh threads for breadth) · `enrich: true` (default; the ledger's
additive semantic pass) | `false` · `human checkpoint: false` (default) | `true` (pause
after Step 1 to confirm L, and before Step 5). Example:
`/anti-autoresearch ~/papers/submission — effort: max, human checkpoint: true`.

> ⚠️ **Shell state does not persist between Bash calls** (cwd + env reset each call).
> Every block below re-derives `ROOT` and `PAPER_DIR` at its top and reads `L` /
> `PAPER_ID` from `claims.json` (the authoritative source after Step 1). Never rely on a
> variable set in an earlier block, and never `cd` into the paper dir. Keep `PAPER_DIR`
> **space-free** (simplest way to stay safe across the inline `*.tex` / `*.findings.json` globs).

## Execution modes & the Reviewer Calling Convention

**Pick the mode automatically — both produce the *identical* file set, and Step 4 (the
verdict) is byte-deterministic given those files + the ledger.**

- **Delegation (default — if the `Skill` tool is available):** invoke `/evidence-ledger`,
  the six auditors, and the two advisory memos (`/adversarial-case-builder` +
  `/novelty-duplication-advisory`). Each sub-skill runs its own
  deterministic tools + its exact codex reviewer prompt + its own anchor validation, and
  writes its `<skill>.findings.json`. The orchestrator validates the emitted files and
  adjudicates. This mirrors ARIS `/research-pipeline` delegating all GPT review to
  `/auto-review-loop` rather than prompting GPT itself.
- **Inline (fallback — only shell + Read/Write + codex MCP):** run the deterministic
  tools yourself with the exact commands below; for each cross-model dimension open a
  **fresh** `mcp__codex__codex` thread, send the **verbatim** reviewer-prompt block —
  the fenced `prompt:` / checklist in `skills/<dim>/reference/reviewer-prompt*.md`
  where that file exists, else in the sub-skill's `## Step … — Cross-model …` section of
  `skills/<dim>/SKILL.md` (Read it — the single source of truth; fill its
  `[...]` inputs from `claims.json`), save the raw reply, then run the **shared anchor gate**
  (Step 2) to produce the validated `<dim>.findings.json`.

The orchestrator's job is to guarantee the *envelope* and the *independence invariants*
every reviewer call obeys:

- **Envelope (every auditor instantiates this exact shape):**
  ```text
  mcp__codex__codex:
    model: gpt-5.5
    config: {"model_reasoning_effort": "xhigh"}
    sandbox: read-only
    cwd: <absolute PAPER_DIR>          # so the reviewer reads claims.json + sources directly
    prompt: |
      <the auditor's per-dimension checklist + the SIX HARD RULES below>
  ```
- **The executor passes only structured inputs** — paths + the ledger (`claims.json`) +
  the per-dimension checklist + the run level `L`. It **never** summarizes the paper,
  pre-judges, leaks a hunch, or whispers "this is probably AI-generated"
  (`references/reviewer-independence.md` Layer 1; the tool is agnostic to authorship).
- **Six hard rules the orchestrator requires in every auditor's prompt** (a finding that
  breaks one is structurally worthless): **(1) ANCHOR** — every above-`info` finding
  carries ≥1 `evidence{claim_id, span}` where `claim_id` exists in `claims.json` and
  `span` is a *verbatim, whitespace-normalized substring of that claim's `text_span`*
  (`span in claim`, never `claim in span`); **(2) DISCREPANCY, NOT ACCUSATION** —
  describe what to *check/ask*, never "reject"/"fabricated"; **(3) OBSERVABILITY** — set
  `observability_level_required` to the lowest tier at which the discrepancy is decidable
  (code/result confirmation ⇒ `2`); **(4) HONEST FP RISK** — set `false_positive_risk`
  truthfully (legit "best config", labeled pilots, rounding, deterministic metrics are
  common FPs); **(5) HAND OFF EXTERNAL CLAIMS** — "first / SOTA" the text cannot settle ⇒
  `verdict_local: needs_external_check` + `requires_external_check: true`; **(6)
  pattern_id ∈ taxonomy v0.4 only**.
- **Reviewer ≠ adjudicator.** The reviewer *proposes* findings; only
  `tools/adjudicate_findings.py` *decides* the verdict (Layer 2). The model is demoted
  from judge to evidence-extractor.
- **Fresh thread per dimension, serial.** A new `mcp__codex__codex` call per auditor (and
  per cited key inside `citation-forensics`); **never** `codex-reply` carrying one
  dimension's conclusions into another (the bias guard). Keep the calls **serial** —
  concurrent codex threads can hang; fan-out buys *breadth of dimensions*, not
  parallelism. On a stall, re-invoke the *identical* prompt in a fresh thread (never
  `codex-reply`); if it still fails, write `[]` and continue — a dead reviewer must never
  become a fabricated finding.

## Re-entrancy: resuming a partial / re-run sweep

The pipeline is a **pure function of `PAPER_DIR`'s contents** — every step writes a
predictable file, so a crashed or repeated run resumes by *probing what already exists*.
There is no run-state file and no "accepted vs done" gate, because **Step 4 recomputes
the verdict deterministically** from whatever findings are present every time. Probe
completeness *and staleness* before redoing work:

Run the probe script in `reference/step-scripts.md` (section "Re-entrancy probe"); per step it prints present/ok, `todo`, or a ⚠ STALE ledger.

Rule: a **stale ledger forces a full rebuild** (Step 1 → re-fan Step 2 → re-adjudicate)
— stale findings anchored to an old ledger are worse than none. If the ledger is fresh,
skip Step 1 and only re-run the auditors marked `todo`. Always re-run Step 4 (cheap,
deterministic, the only verdict source). Re-running from scratch is always safe — same
inputs → same outputs.

---

## Step 0 — Ingest: resolve the input to a working dir

Turn `$ARGUMENTS` (a directory, a PDF, or an arXiv id) into a single **working
directory** (`PAPER_DIR`) that contains the best source the level allows. Prefer LaTeX
(stable `file:line` spans → L1) over PDF text (best-effort → L0); leave any `code/` +
`results/` in place so the manifest can derive L2.

Run the ingest script in `reference/step-scripts.md` (section "Step 0 — ingest") with `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}" ARGUMENTS="$ARGUMENTS"` exported first (the reference file is not substituted); it sets and prints `PAPER_DIR` and lists the sources and L2 candidates it found.

**Validation gate.** `PAPER_DIR` must now contain **anchorable text** — at least one
`*.tex` or `*.txt`. A bare `*.pdf` is **not** enough: the ledger builders accept only
`--latex` / `--pdf-text`, so Step 0 must have extracted `paper.txt`. If extraction failed
or no source is present, **stop** and report exactly what was searched — there is nothing
to anchor spans against, so there can be no ledger (see Failure handling below).

**Failure handling.**
- *No `pdftotext`* → fall back to `mutool draw -F txt in.pdf out.txt` or
  `pip install pdfminer.six && pdf2txt.py in.pdf > out.txt`. If text extraction is
  impossible, you cannot build an L0 ledger from a PDF — ask the user for the LaTeX.
- *arXiv unreachable* (network gated / proxy needed) → say so and ask the user to drop
  the source or PDF into a local dir, then re-invoke with that **paper-dir**. Never
  fabricate a ledger from an absent paper. (A heartbeat *may* wait on this download — a
  pre-verdict external step — but only the sweep, run once the source lands, produces the
  verdict.)
- *arXiv `.tex` extracted but no obvious `main.tex`* → fine; `/evidence-ledger` globs
  `*.tex`. (`PAPER_ID` is set authoritatively by the ledger in Step 1 — do not hand-pick
  it here.)

## Step 1 — Build the evidence ledger (always first; the spine)

Delegate to `/evidence-ledger`, which runs the real deterministic tools
(`tools/build_manifest.py` → `artifact_manifest.json` + observability level **L**;
`tools/build_claim_ledger.py` → `claims.json`) and, by default, one additive
span-anchored semantic-enrichment pass. Everything downstream reads these two files.

```
/evidence-ledger "<PAPER_DIR>"            # add "— enrich: false" to ship the deterministic backbone alone
```

Then read **L** and **PAPER_ID** back from the ledger — it is the source of truth for
every later block (re-derive, never persist):

Run the read-back script in `reference/step-scripts.md` (section "Step 1 — read-back"); it prints `PAPER_ID`, `L`, the claim count and claim-type histogram, and asserts ledger level = manifest level.

**Validation gate.**
- `claims.json` exists and `claims` is non-empty. **Zero claims on a paper that visibly
  has numbers/citations** means the ingest source was wrong (e.g. a PDF with no usable
  text, or a dir with no `.tex`/`.txt`) → fix Step 0 and re-run `/evidence-ledger`.
- The ledger's `observability_level` **matches the artifacts present** (a PDF-only run
  MUST be `L=0`; never hand a higher level to anything because a repo "exists somewhere
  else"). The level is the honesty contract for the whole run — carry this `L` forward;
  it caps every finding's severity in Step 4.
- `— human checkpoint: true` → present `L`, the claim-type histogram, and the source
  list, and pause for confirmation before fanning out.

**Failure handling.** If `/evidence-ledger` is unavailable, build the ledger directly with the commands in `reference/fallbacks.md` (section "Step 1 without /evidence-ledger"), with `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"` exported first.

## Step 2 — Fan out the six auditors (breadth; the verdict is NOT decided here)

Decide which auditors apply **from the ledger's claim types**, then run each applicable
skill. Each reads `claims.json`, opens a **fresh codex thread per dimension** (a
different model family from the executor), proposes span-anchored findings, validates its
own spans, and writes `<skill>.findings.json` (the deterministic auditors also write
`<skill>.deterministic.findings.json`). The orchestrator only *sequences* these calls and
enforces the Reviewer Calling Convention above — it authors no finding.

Run the decision script in `reference/step-scripts.md` (section "Step 2 — auditor decision"); it prints which optional auditors and the novelty memo apply (`has_cite`, `has_cmp`, `has_proof`, `has_contrib`).

Run the applicable skills (pass `PAPER_DIR` so each locates the ledger). **Keep the
reviewer calls serial.** Each row's `Writes` column is the exact filename the Step-4 glob
expects; the `Owns` column is the taxonomy-v0.4 patterns that skill may emit:

| Skill | Run when | Writes | Owns (pattern_ids, taxonomy v0.4) |
|-------|----------|--------|-----------------------------------|
| `/consistency-audit "<PAPER_DIR>"` | **always** (flagship; L0-decidable) | `consistency-audit.deterministic.findings.json` (+ semantic `consistency-audit.findings.json`) | HP-NUM-INFLATE, HP-DELTA-ERROR, HP-AGG-DRIFT, HP-DENOM-DRIFT, HP-UNIT-DIR-MISMATCH, HP-CAPTION-MISMATCH, HP-APPENDIX-CONTRA, HP-METHOD-DRIFT, HP-ABLATION-ATTRIB, HP-SCOPE-INFLATE, HP-THEOREM-SCOPE-DRIFT, HP-SUSPICIOUS-REGULARITY(L0→info), HP-ARGUMENT-CHAIN-BREAK, HP-CAUSAL-EVIDENCE-LEAP, HP-ACRONYM-DRIFT, HP-GRANULARITY-IMPOSSIBLE, HP-VARIANCE-IMPOSSIBLE, HP-STAT-INCONSISTENCY |
| `/citation-forensics "<PAPER_DIR>"` | ≥1 `citation` claim | `citation-forensics.findings.json` | HP-CITE-HALLUC, HP-CITE-CONTEXT, HP-CITE-RETRACTED |
| `/baseline-comparison-audit "<PAPER_DIR>"` | ≥1 comparison/SOTA scope claim | `baseline-comparison-audit.findings.json` | HP-MISSING-BASELINE, HP-WEAK-BASELINE, HP-SIG-OVERLAP, HP-DELTA-ERROR(cross-claim), HP-RESOURCE-IDENTITY-MISMATCH |
| `/experiment-forensics "<PAPER_DIR>"` | **always** (depth scales with L) | `experiment-forensics.findings.json` | HP-FAKE-GT, HP-SELF-NORM, HP-PHANTOM-RESULT, HP-DEAD-METRIC, HP-SCOPE-INFLATE(verified), HP-METHOD-DRIFT(L2), HP-SUSPICIOUS-REGULARITY(L2), HP-PLACEHOLDER-DATA(L2), HP-RESULT-ARTIFACT-MISMATCH(L2), HP-MISSING-REPRO-ARTIFACT(L2) |
| `/presentation-signals "<PAPER_DIR>"` | **always** (AUXILIARY, capped at `minor`) | `presentation-signals.deterministic.findings.json` (+ semantic `presentation-signals.findings.json`) | HP-DUP-TABLE, HP-PIPELINE-ARTIFACT, HP-THIN-FLOAT, HP-LLM-FIGURE, HP-PAGE-PADDING |
| `/proof-derivation-forensics "<PAPER_DIR>"` | ≥1 theorem/proof/derivation claim (self-guards: writes `[]` if `HAS_PROOFS=no`) | `proof-derivation-forensics.findings.json` | HP-PROOF-OBLIGATION-GAP, HP-PROOF-CIRCULARITY, HP-DERIVATION-INVALID, HP-SYMBOL-SEMANTIC-DRIFT, HP-ASSUMPTION-SMUGGLE, HP-UNDEFINED-NOTATION |
| `/eval-design-forensics "<PAPER_DIR>"` | ≥1 comparison/eval claim (family H, L0/L1 stated-tells; dim=evaluation) | `eval-design-forensics.findings.json` | HP-EVAL-LEAKAGE, HP-JUDGE-VALIDITY, HP-SELECTIVE-REPORTING |
| `/ai-style-impressions "<PAPER_DIR>"` | **always** (AIS track · NOT integrity · **zero verdict weight** · separate report section) | `ai-style-impressions.deterministic.findings.json` (+ semantic `ai-style-impressions.findings.json`) | AIS-NARRATIVE-ARC-BREAK, AIS-LLM-PHRASE-TICS, AIS-DEFENSIVE-HEDGE, AIS-JARGON-STUFF, AIS-INVENTED-CODENAME, AIS-CLAUSE-FORMULA-WALL, AIS-GRATUITOUS-PSEUDOCODE, AIS-BULLET-LIST-OVERUSE, AIS-BOLD-MODULE-SPAM, AIS-RESTATE-OVERCLAIM, AIS-FOCUS-DRIFT, AIS-SINGLE-STYLE-FIGURES, AIS-APPENDIX-DUMPING-GROUND |

Notes the orchestrator must honor:
- **experiment-forensics always runs**, but at **L0/L1 it emits only info-level
  "could-not-verify" signals** (`observability_level_required: 2`) — never a fraud flag
  from a PDF. Its full line-by-line code audit only fires at **L2**; the eval `file:line`
  is description detail, the **anchor is the paper claim**.
- **presentation-signals is auxiliary**: every finding is `false_positive_risk: high` and
  the adjudicator **caps it at `minor`** (by `SURFACE_ONLY_SKILLS` AND by `SURFACE_PATTERNS`
  `pattern_id`), so the surface dimension can contribute at most `SOFT_FLAGS`, never
  `HARD_FLAGS`. It is **not** an AI-text classifier (`references/hack-pattern-taxonomy.md`
  §F). Most papers ⇒ `[]`.
- **proof-derivation-forensics is verdict-bearing** (`dimension: proof`), but unlike the L2
  code dimensions it **decides from the LaTeX proof source (L1)** — a span-anchored
  **critical** family-G flaw (a circular proof; an invalid step / smuggled assumption /
  inverted symbol the headline theorem depends on) **can reach `HARD_FLAGS` with no repo or
  results**, but needs the **L1 source**: PDF-extracted math is unreliable, so at an L0
  (PDF-only) run family-G findings surface as `info` only. There is **no deterministic companion** (proof validity is semantic), so it
  writes the single `proof-derivation-forensics.findings.json`. It **self-guards**: if the
  paper has no theorem/proof/derivation markers (`HAS_PROOFS=no`) it writes `[]` and never
  calls the reviewer — so running it unconditionally is safe; the decision block only gates
  it for budget. It emits **only the five family-G patterns**; abstract-vs-theorem scope
  drift stays with consistency-audit (`HP-THEOREM-SCOPE-DRIFT`), not here
  (`references/hack-pattern-taxonomy.md` §G).
- A skill that finds nothing — or an optional auditor that does not apply — still writes
  `[]` to its predictable path. **Silent skip is forbidden** (so the run records that the
  dimension ran and was clean, not silently absent): `echo '[]' > "$PAPER_DIR/citation-forensics.findings.json"`.
- **No double-counting.** Each auditor writes its own filename, so the `*.findings.json`
  glob enumerates each file exactly once; the deterministic and semantic passes stay in
  *separate* files. (Finding-id prefixes: `NUM###`/`HL###` numeric, `PRES###`
  presentation, `EF###` experiment, `F###` other semantic. Ids may repeat across
  semantic files; that is cosmetic — the report keys on skill + file, not id.)

**Inline mode only.** When delegation is unavailable, turn each raw reviewer reply into a validated `<dim>.findings.json` with the shared anchor gate, and run the deterministic passes directly; both are in `reference/inline-mode.md`. Export `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"` first.

**Validation gate — files exist + parse, and every above-info finding is anchored.** This
independently re-checks invariant #3 (it mirrors the adjudicator; it is report-only here —
the adjudicator is the *binding* gate and fail-closes anything unanchored to `info`):

Run the anchor-sweep script in `reference/step-scripts.md` (section "Step 2 — anchor sweep").

**Failure handling.** A *missing* mandatory file → re-invoke that skill. A codex *stall*
inside a sub-skill → it re-invokes the identical prompt in a fresh thread (never
`codex-reply`); if it still fails it writes `[]` and the run continues. Unanchored
above-info findings are not a stop condition (the adjudicator demotes them); a *large*
count signals a thin ledger/source — note it in the report's limitations. Any
`pattern_id` present MUST be in `references/hack-pattern-taxonomy.md` (v0.4); never patch
findings by hand.

## Step 3 — Advisory memos (last; memo-only, no verdict weight)

After the auditors (so the ledger + the merged findings exist), run the two **advisory**
skills. Both are **memo-only**: the adjudicator lists each in `MEMO_ONLY_SKILLS` and its
MEMO gate pins any finding either emits to `info`, so neither can move the verdict — they
hand a human area chair context to weigh, nothing more.

**3a — Adversarial case builder.** Synthesize the single strongest *evidence-bound*
objection:

```
/adversarial-case-builder "<PAPER_DIR>"          # → adversarial-case-builder.memo.md
```

Every point in the memo must cite an existing ledger `claim_id` or finding `finding_id` —
no new uncited accusations. It is passed to the adjudicator via `--memo` and shown as
informational with **no verdict weight** (the `MEMO_ONLY_SKILLS` cap pins any
`adversarial-case-builder` finding to `info`, even if it also emits a `findings.json`). If
the anchored evidence does not support a strong rejection, the honest memo says the paper
survives.

**3b — Novelty & duplication advisory** (run if `has_contrib` from the Step-2 decision
block — ≥1 contribution claim). This is the **only** skill that reaches *outside* the
paper: it retrieves candidate prior work (DBLP fuzzy-title + boolean · WebSearch ·
WebFetch) from the paper's own title + contribution spans and lays the overlap
**side-by-side** for the two *advisory* taxonomy signals — `ADV-TRIVIAL-COMBINATION`
(standard A+B+C / 缝合) and `ADV-DUPLICATE-PUBLICATION` (repackaged submission):

```
/novelty-duplication-advisory "<PAPER_DIR>"      # → novelty-duplication-advisory.memo.md (+ info-only findings mirror)
```

It **never rules** "trivial" or "duplicate" (a reviewer judgment, not decidable at *any*
observability level), and **absence of a retrieved match is NOT evidence of originality**.
Unlike 3a it does **not** flow through `--memo` (the adjudicator has a single memo slot):
its human-facing `novelty-duplication-advisory.memo.md` is surfaced in Step 5, and it also
writes an **info-only `novelty-duplication-advisory.findings.json` mirror** that the Step-4
glob picks up and the `MEMO_ONLY_SKILLS` gate caps at `info` (recorded, never
verdict-bearing). With no contribution claim, or when retrieval surfaces nothing, it writes
an honest-null memo + `[]` — "no candidate overlap found" still says nothing about novelty.
It is the literature-facing complement to `citation-forensics`: that audits works the paper
**does** cite; this surfaces prior work it may **not** have cited at all.

Both memos are **non-blocking** — if either is skipped, Step 4 still runs (an empty
`--memo` for the adversarial case; an absent novelty mirror simply contributes nothing).

## Step 4 — Adjudicate (deterministic — this is the verdict)

The single decider. Pass every auditor's `*.findings.json` (the glob now also enumerates
the verdict-bearing `proof-derivation-forensics.findings.json` and the info-only
`novelty-duplication-advisory.findings.json` mirror — the latter capped at `info` by the
MEMO gate), the **required** ledger, the run level, the taxonomy version, and the
adversarial memo. `--ledger` is what re-verifies each
finding quotes a **verbatim ledger span**; argparse makes it mandatory — and without a
ledger every above-info finding **fails closed to `info`** (a missing ledger silently
neuters the audit), which is why it is non-optional here.

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"; PAPER_DIR="<from Step 0>"
L=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["observability_level"])' "$PAPER_DIR/claims.json")
PAPER_ID=$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1]))["paper_id"])' "$PAPER_DIR/claims.json")

# Build the findings list portably (no `mapfile` — macOS ships bash 3.2 without it).
# Defensive: never adjudicate a raw/intermediate *.proposed.findings.json, should a sub-skill ever stage one.
FINDINGS=()
for p in "$PAPER_DIR"/*.findings.json; do
  [ -f "$p" ] || continue
  case "$p" in *.proposed.findings.json) continue;; esac
  FINDINGS+=("$p")
done
[ ${#FINDINGS[@]} -gt 0 ] || { echo "FATAL: no findings files in $PAPER_DIR — did Step 2 run?"; exit 1; }
printf '  findings: %s\n' "${FINDINGS[@]##*/}"

python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "${FINDINGS[@]}" \
    --ledger "$PAPER_DIR/claims.json" \
    --paper-id "$PAPER_ID" --observability-level "$L" --taxonomy-version 0.5 \
    --memo "$(cat "$PAPER_DIR/adversarial-case-builder.memo.md" 2>/dev/null)" \
    --limitation "Run observability level L$L — see references/observability-levels.md for what this tier can and cannot decide." \
    --out "$PAPER_DIR/report.json" --md "$PAPER_DIR/REPORT.md"
# prints e.g.: verdict=SOFT_FLAGS crit=0 maj=0 min=1 -> .../report.json, .../REPORT.md
```

Read `reference/adjudicator-gates.md` for what `--observability-level` / `--limitation` do, the gate order (ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE) and the verdict rule; read it when interpreting counts or a demotion.

**Validation gate.** Confirm the report is well-formed:

Run the report check in `reference/step-scripts.md` (section "Step 4 — report check").

**The verdict is reproducible: same findings + same `L` → same verdict, with no model in
the final decision.**

## Step 5 — Present

Show the human `REPORT.md`. **Lead with the verdict + the observability level**, then the
evidence-first table, then detail, then the advisory memos (adversarial + novelty/
duplication), then — always — the limitations (what could *not* be checked at this level):

```bash
PAPER_DIR="<from Step 0>"; sed -n '1,60p' "$PAPER_DIR/REPORT.md"
```

Present in this shape (fill from `report.json` / `REPORT.md`):

```
🔬 Integrity Forensics — <PAPER_ID>
   Verdict: <CLEAN_GIVEN_EVIDENCE | SOFT_FLAGS | HARD_FLAGS>   Observability: L<L>   Taxonomy: v0.4
   Findings above info: critical <n> · major <n> · minor <n>   (demoted: obs <n>, unanchored <n>)
   Top flags: <ID> <severity> <pattern_id> — <one-line, where>
   Could NOT check at L<L>: <one line from limitations — e.g. "code/result-level patterns need L2">
   Advisory (no verdict weight): adversarial objection + novelty/duplication overlap — <PAPER_DIR>/novelty-duplication-advisory.memo.md
   Report: <PAPER_DIR>/REPORT.md   ·   Machine-readable: <PAPER_DIR>/report.json
   This is decision support for a human reviewer/AC — it flags discrepancies to investigate, not misconduct.
```

State plainly, in the user's words, what the level did and did not permit: e.g. *"L0 run
— I checked internal self-consistency, arithmetic, citation existence/context, and stated
scope/baselines; I could NOT verify code/result-level integrity (fake GT,
self-normalization, phantom results) — that needs the repo + result files (L2)."*
`CLEAN_GIVEN_EVIDENCE` means **"nothing checkable at L<L> is broken,"** NOT "the paper is
honest." `human_review_required` is always `true`.

`— human checkpoint: true` → pause here for the user before treating the run as closed.

Then write the orchestrator's run trace with the script in `reference/review-tracing.md`.

## Deterministic-only fallback (no model in the loop)

When no cross-model reviewer is available (offline / no codex), follow `reference/fallbacks.md` (section "Deterministic-only fallback"): with `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"` exported first; deterministic tools only, and the report's limitations must say the semantic / code-level dimensions were not run. Then write the orchestrator's run trace with the script in `reference/review-tracing.md`, as Step 5 does.

## Output contract

A completed run leaves, in `PAPER_DIR` (we never edit the paper itself):

- `artifact_manifest.json` (`schemas/artifact_manifest.schema.json`) — observable inputs
  (hashed) + the derived observability level.
- `claims.json` (`schemas/claims.schema.json`) — the span-anchored, hashed evidence
  ledger every auditor read.
- `<skill>.findings.json` for each auditor that ran, plus `*.deterministic.findings.json`
  for the consistency and presentation deterministic passes. Each conforms to
  `schemas/finding.schema.json`; `[]` is a valid, honest result, and every optional
  auditor's file is present even when empty.
- `adversarial-case-builder.memo.md` — the evidence-bound objection memo (informational).
- `novelty-duplication-advisory.memo.md` — the prior-work overlap advisory (informational,
  memo-only), present when the novelty advisory ran; alongside it the retrieval records
  `novelty-duplication-advisory.profile.json` / `.candidates.json` and the info-only
  `novelty-duplication-advisory.findings.json` mirror (capped at `info` by the MEMO gate).
- `report.json` (`schemas/report.schema.json`) + `REPORT.md` — the **only** files
  carrying `overall_verdict`, produced solely by `tools/adjudicate_findings.py`
  (`adjudicator: deterministic-rules-v0`, `human_review_required: true`).
- `.aris/traces/<skill>/<date>_run<NN>/` — each sub-skill's raw reviewer calls
  (forensic), plus this orchestrator's own run trace (see Review tracing).

The orchestrator itself **never** computes a verdict, **never** edits the audited paper,
and **never** hand-authors a finding — it ingests, sequences the skills, runs the
deterministic adjudicator, and presents.

## Key rules

- **Ledger first, always; auditors propose, only `adjudicate_findings.py` decides.** No
  auditor runs without `claims.json`, and no model is in the final decision; the verdict
  is reproducible (`references/reviewer-independence.md` Layer 2; `DESIGN.md` §3).
- **No span → no severity.** Every above-info finding must cite a ledger `claim_id` and
  quote a verbatim, whitespace-normalized substring of that claim (`span in claim`, never
  `claim in span`). The orchestrator's anchor sweep checks this; the adjudicator binds it
  (fail-closed to `info`). `--ledger` is therefore **mandatory** in Step 4.
- **Observability honesty.** Carry the ledger's `L` everywhere; it caps severity. L0/L1
  **cannot** assert code/result-level fraud — those auto-demote to `info` on a sub-L2
  run. Never present an L0 run as if it could see code; the report's limitations say what
  was unverifiable (`references/observability-levels.md`; `DESIGN.md` §4).
- **Cross-model, fresh thread per dimension.** Reviewer = gpt-5.5 xhigh (a different
  family from Claude); each auditor uses a new `mcp__codex__codex` thread and never
  `codex-reply` (deliberately absent from `allowed-tools` — the bias guard). The executor
  passes only paths + the ledger + the checklist, never a summary or a hunch.
- **Detect-only.** No step edits the audited paper or repo (no `Edit` granted; reviewer
  sandbox is `read-only`). Output describes a *discrepancy to check/ask*, never "reject"
  or "the authors faked X".
- **Surface signals stay weak.** `presentation-signals` is auxiliary, capped at `minor`
  (by skill and by `pattern_id`), default `false_positive_risk: high`. This repo is
  **not** an AI-text classifier — for authorship use a dedicated detector.
- **Proof decides from the source; novelty never decides.** `proof-derivation-forensics`
  is verdict-bearing (`dimension: proof`) and decides from the LaTeX proof source (L1) — a
  span-anchored **critical** family-G flaw reaches `HARD_FLAGS` with no repo/results, but
  needs the L1 source (PDF-extracted math is unreliable; an L0 PDF-only run → `info`); it
  emits only the five family-G patterns and self-guards to `[]` when no proof is present.
  `novelty-duplication-advisory` is **memo-only** (`MEMO_ONLY_SKILLS`, capped at `info`):
  it retrieves and *lays out* prior-work overlap but **never** rules trivial/duplicate, and
  absence of a retrieved match is **not** evidence of originality (the only auditor that
  consults an external corpus, which is exactly why it carries no verdict weight).
- **`pattern_id` ∈ taxonomy v0.4 only**; the taxonomy is a post-hoc mapping layer, not
  the detector (`references/hack-pattern-taxonomy.md`).
- **The adjudicator ingests validated findings only.** The `*.findings.json` glob feeds
  the adjudicator; defensively exclude any raw/intermediate `*.proposed.findings.json` a
  sub-skill might stage, so an unvalidated array can never reach the verdict.
- **Silent skip is forbidden.** A non-applicable / clean auditor still writes `[]`.
- **Large file handling.** If `Write` fails on size, retry with a Bash heredoc
  (`cat << 'EOF' > file`) — do not ask permission, just do it. This is only ever for
  **our own output files** in `PAPER_DIR`; detect-only still holds (never write/edit the
  audited sources).
- **Reproducible.** Same artifacts → same ledger → same findings → same verdict; re-run
  only when the inputs change (the cadence fence at the top).

## When NOT to use (and routing to standalone skills)

One dimension only → call that auditor directly; ledger only → `/evidence-ledger`; prior-work overlap only → `/novelty-duplication-advisory`.
Out of scope: AI-text / authorship verdicts, auto-fixing the paper, reproduction (L3), and running the verdict on a timer.
Read `reference/routing.md` for the full routing list.

## Run profile and review tracing

Read `reference/run-profile.md` for the per-stage reviewer-call budget when choosing `— effort: max` vs the deterministic-only fallback.
Read `reference/review-tracing.md` for the trace layout and the script that writes the orchestrator's `run.meta.json`.
