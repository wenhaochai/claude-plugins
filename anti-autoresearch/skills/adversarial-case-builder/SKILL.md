---
name: adversarial-case-builder
description: "Builds the strongest rejection argument only from the evidence ledger and other auditors' findings, then tests each point; the paper may survive. Memo-only, no verdict weight (the adjudicator decides); run last. Triggers: \"strongest objection\", \"rejection memo\", \"kill argument\", \"最强拒稿点\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, mcp__codex__codex
---

# Adversarial Case Builder — the strongest *evidence-bound* objection

Build the single strongest evidence-bound case to reject **$ARGUMENTS**, then defend
it point-by-point. Emit `adversarial-case-builder.memo.md`. Run **LAST**, AFTER
`/evidence-ledger` (so `claims.json` exists) and AFTER the auditor skills (so the
merged `*.findings.json` exist).

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the ledger, the auditors' findings or the paper change.

> Adapted from ARIS `kill-argument`, with **one deliberate downgrade: memo-only.** In
> a forensics pipeline the headline-attack is most useful as a *synthesis of
> already-anchored evidence*, not a free-floating LLM critique — that free-floating
> mode is exactly the "LLM slop grading LLM slop" failure this repo exists to refuse.
> So here every attack point must cite an existing ledger `claim_id` or `finding_id`,
> and the skill never emits verdict-bearing findings: `tools/adjudicate_findings.py`
> lists `adversarial-case-builder` in `MEMO_ONLY_SKILLS` and caps anything from it at
> `info`. The deterministic adjudicator owns the verdict; this skill owns the memo.

Read `reference/rationale.md` for why this skill exists (the committed single-paragraph rejection a balanced auditor list never writes, fenced to anchored evidence).

## Core principle

**MEMO-ONLY · evidence-bound · two fresh cross-model threads · reviewer ≠ adjudicator
· honest-null.** The reviewer **proposes** an attack and a defense; the executor
**validates** that every kept point is anchored to a real ledger claim (verbatim
span) or a real sibling finding; the deterministic `tools/adjudicate_findings.py`
**owns the verdict** and caps this skill at `info` (`references/integrity-forensics-contract.md`
rules 1–2, 7–8; `references/reviewer-independence.md` Layer 2). This skill computes
**no verdict** — by design.

> **Deliberate exception to "no prior-dimension findings."** Reviewer-independence
> normally forbids leaking the executor's hunches and forbids one fresh per-dimension
> audit seeing another's conclusions. This skill is the explicit **synthesis stage**:
> the anchored, machine-validated findings *are* its input. It still receives only
> structured artifacts — `claims.json` + the `*.findings.json` files — never a
> Claude-authored digest or opinion about the paper, so the spirit of the rule (no
> executor judgment leaks into the reviewer) holds.

## How this differs from the other auditors (route correctly)

This skill detects nothing new and has no verdict weight (memo-only, capped at `info`, any level).
It narrates the worst case the existing anchored evidence supports and stress-tests it. A *new*
discrepancy belongs to its owning auditor (code/result fraud → `experiment-forensics` at L2;
existence/context → `citation-forensics`; "SOTA/first" → `baseline-comparison-audit`), not here.
Read `reference/routing.md` for the full auditor table.

Read `reference/aris-lineage.md` for how this skill differs from its parent ARIS `kill-argument` (evidence-bound citations, no verdict, honest null, runs last).

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL      = gpt-5.5            # different family from executor (Claude)
REVIEWER_REASONING  = xhigh             # always; effort never lowers reviewer quality
REVIEWER_SANDBOX    = read-only         # detect-only; never mutate the paper
REVIEWER_CWD        = <paper-dir>       # so it reads claims.json + *.findings.json directly
THREAD_POLICY       = TWO fresh mcp__codex__codex calls (Thread 1 attack, Thread 2 defense);
                      NEVER mcp__codex__codex-reply, and NEVER carry Thread 1's codex history into Thread 2
CONCURRENCY         = serial            # Codex MCP hangs on concurrent calls — Thread 2 waits for Thread 1
ATTACK_LENGTH       = ~200 words (NEVER exceed 250); ONE committed argument, not a list
DEFENSE_POINTS      = 3-7 atomic anchored points (empty array under honest-null)
CLASSIFICATION      = already_addressed | partially_addressed | unresolved
ANCHOR_UNIVERSE     = ledger claim_ids (claims.json) + finding_ids (sibling *.findings.json, skill-prefixed)
DISPOSITION         = kill_constructed | partial_case | honest_null   # informational, NOT the report verdict
TAXONOMY_VERSION    = 0.5               # references/hack-pattern-taxonomy.md
MEMO_FILE           = adversarial-case-builder.memo.md          # canonical output (fed to --memo)
FINDINGS_FILE       = adversarial-case-builder.findings.json    # info-only mirror (or []), capped at info
TRACE_POLICY        = forensic (never silently dropped)
TRACE_DIR           = .aris/traces/adversarial-case-builder/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** owns none of the judgment: it locates the ledger + the merged
  findings, passes **paths + the ledger + the findings (+ the attack memo to Thread 2)**
  to each reviewer, validates every anchor the reviewers return, and renders the memo.
  It never summarizes the paper, pre-judges, or leaks an opinion into a prompt
  (`references/reviewer-independence.md`).
- **Reviewer (codex / gpt-5.5, xhigh, read-only)** reads `claims.json` + the
  `*.findings.json` from its `cwd`, writes the attack (Thread 1) and the defense
  (Thread 2), and self-reports honestly. It is the case-builder, **not** the judge.
- **Two fresh threads, no `codex-reply`.** Attack and Defense are independent
  `mcp__codex__codex` calls; Thread 2 receives the attack memo as **text**, never
  Thread 1's codex context (the bias guard). `codex-reply` is intentionally absent
  from `allowed-tools`.

---

## Step 0 — Preconditions: locate the ledger + the upstream findings, read the level

This skill reasons over the **ledger** + the **other auditors' findings** — never the
raw PDF. Resolve them and read the observability level **L** and `paper_id` (each Bash
block is self-contained — shell state does not persist between calls, so re-derive
paths every time):

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
    sys.exit("NO_LEDGER: claims.json not found. Run /evidence-ledger FIRST, then the "
             "auditor skills, THEN this skill (it synthesizes their output, run LAST).")
d = json.load(open(p, encoding="utf-8")); D = os.path.dirname(os.path.abspath(p)) or "."
sib = [os.path.basename(f) for f in sorted(glob.glob(os.path.join(D, "*.findings.json")))
       if not os.path.basename(f).startswith("adversarial-case-builder")]
print("LEDGER         =", os.path.abspath(p))
print("PAPER_DIR      =", D)
print("PAPER_ID       =", d.get("paper_id", "?"))
print("RUN_LEVEL_L    =", d.get("observability_level", 0))
print("CLAIMS         =", len(d.get("claims", [])))
print("FINDINGS_FILES =", sib if sib else "(none — auditors have not run)")
PY
```

**Failure handling.**
- `NO_LEDGER` printed → **stop**. Tell the user to run `/evidence-ledger` (then the
  auditor skills) first — this skill is the **last** step and never re-reads the raw
  PDF to invent structure (contract rule 1).
- `FINDINGS_FILES = (none …)` → **strongly prefer to stop and run the auditors first.**
  With no findings the attack may cite only ledger `claim_id`s, and this skill must NOT
  *originate* a substantive objection from a lone claim (that is detection + a
  `needs_external_check` the auditors own — not synthesis). If you proceed anyway,
  `honest_null` is the expected, correct outcome; do not manufacture a kill from claims
  alone.
- Carry `PAPER_DIR`, `PAPER_ID`, `RUN_LEVEL_L (=L)`, the absolute `LEDGER`, and the
  `FINDINGS_FILES` list forward — every later step needs them.

Create the trace directory now (forensic; written before any reviewer call):

```bash
PAPER_DIR="<abs PAPER_DIR from Step 0>"
DATE=$(date +%F); N=1
while [ -d "$PAPER_DIR/.aris/traces/adversarial-case-builder/${DATE}_run$(printf %02d $N)" ]; do N=$((N+1)); done
TRACE="$PAPER_DIR/.aris/traces/adversarial-case-builder/${DATE}_run$(printf %02d $N)"
mkdir -p "$TRACE"; echo "TRACE = $TRACE"
```

Write `"$TRACE/run.meta.json"` (via **Write**) =
`{"skill":"adversarial-case-builder","paper_id":"<PAPER_ID>","run_level_L":<L>,"findings_files":[…],"generated_at":"<UTC ISO-8601>"}`.

## Step 1 — Attack (Thread 1, fresh codex, evidence-bound ~200 words)

Open a **fresh** `mcp__codex__codex` thread (NOT `codex-reply`). The reviewer reads
`claims.json` + the sibling `*.findings.json` from its `cwd` and writes the single
strongest rejection paragraph — every accusation anchored inline. Substitute the
`<…>` placeholders from Step 0 and send EXACTLY:

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are a senior NeurIPS/ICLR/ICML area chair writing the SINGLE STRONGEST case to
    reject this paper. This is an EVIDENCE-BOUND adversarial pass inside an
    integrity-forensics pipeline: you do NOT roam the paper to invent objections — you
    build the rejection ONLY from evidence that other auditors already anchored.

    INPUTS — read these directly from your working directory:
      - claims.json — the evidence ledger: every checkable claim, span-anchored
        {claim_id (e.g. C012), type, text_span (VERBATIM source text), location, value?}.
        This is the authoritative structure; do not invent claims that are not in it.
      - the other auditors' confirmed findings (read each; do NOT read
        adversarial-case-builder.findings.json):
        <paste the FINDINGS_FILES list from Step 0, one filename per line>
        Each finding = {finding_id (e.g. F003), skill, severity, false_positive_risk,
        observability_level_required, evidence:[{claim_id, span}], pattern_id?}.
    RUN OBSERVABILITY LEVEL L = <L from Step 0>.

    HARD RULES — a memo that breaks any of these is worthless:
    1. EVIDENCE-BOUND. EVERY accusation must cite >=1 EXISTING id inline, in square
       brackets right after the sentence it supports: a ledger claim [C012], or a
       finding [F003] (use the skill-qualified form [citation-forensics:F003] when a
       bare id could be ambiguous across files). You may NOT introduce an accusation
       not anchored to a real claim_id / finding_id. Uncited rhetoric is DELETED
       downstream — do not waste words on it.
    2. QUOTE FOR CLAIMS. A point that cites a claim_id must rest on a VERBATIM
       substring of that claim's text_span (no paraphrase). A point that cites a
       finding INHERITS that finding's severity and observability ceiling.
    3. OBSERVABILITY CEILING — DO NOT UPGRADE EVIDENCE. A cited finding marked
       minor / high false_positive_risk, or whose observability_level_required exceeds
       L (e.g. a code/result-level signal on an L0/L1 run), CANNOT be turned into a
       decisive kill. Build the strongest case the GRADED evidence licenses — not the
       case you wish you had.
    4. DISCREPANCY, NOT MISCONDUCT. Argue the headline is UNSUPPORTED / OVERCLAIMED /
       INTERNALLY INCONSISTENT on the anchored evidence. Do NOT allege fabrication or
       write "the authors faked X". This is a merits rejection, not an accusation.
    5. COMMIT. ~200 words (NEVER exceed 250). ONE coherent line of attack — select and
       fuse at most the two most damaging axes; do NOT enumerate a balanced list, do
       NOT hedge ("the authors might respond" — the defense gets the next pass).
    6. HONEST NULL IS A VALID OUTPUT. If the anchored evidence does NOT license a
       strong rejection (the only anchored findings are minor / high-FP / info, or
       every decisive one auto-demotes at L), SAY SO plainly in <=120 words: "the
       anchored evidence does not support a strong rejection because …". Do NOT
       manufacture a kill from weak evidence — an honest null is the correct, expected
       answer in that case.

    OUTPUT: just the memo text — the ~200-word committed rejection WITH inline [id]
    anchors, OR the honest-null paragraph. Nothing else (no JSON, no preamble, no code
    fence).
```

**Persist immediately, then carry forward.** Save the raw response verbatim to
`"$TRACE/001-attack.response.md"` (**Write**); also write `"$TRACE/001-attack.request.json"`
(the exact prompt + paths sent — the independence audit trail) and
`"$TRACE/001-attack.meta.json"` (`{"model":"gpt-5.5","reasoning":"xhigh","thread_id":"<id>","sandbox":"read-only"}`).
Keep `threadId` as `attack_thread_id`; do **NOT** pass it to Thread 2.

**Failure handling.**
- *MCP stall / hang* (common in long sessions): re-invoke the **identical** prompt as
  a **fresh** `mcp__codex__codex` call (gpt-5.5, xhigh) — never `codex-reply`.
- *Empty response*: re-ask once. If still empty, record `status: ERROR` in the memo
  header and stop — do not hand-author an attack.

### Step 1.5 (optional, `— effort: beast`): multi-axis attack fan-out

**Default OFF.** The deliverable is one *committed* paragraph; forcing a single
commitment yields sharper feedback than a balanced list. Fan-out widens the
**evidence** the commitment draws on, never the commitment itself (mirrors ARIS
`fan-out-pattern.md`: fan out the evidence, not the verdict — and here there is no
verdict at all). Under `beast`: run up to six axes (headline-number / method-scope /
baseline / citation / experiment / scope-evidence) as **separate fresh
`mcp__codex__codex` probes**, each asked for its strongest ~120-word *anchored* thrust
on that axis alone; then a final fresh-codex synthesis **commits to one ~200-word
anchored paragraph** (the Step-1 output). These are **NOT Claude subagents** and there
is deliberately **no `Agent` grant** — the adversary must be cross-model (non-Claude),
and Codex MCP is **serial** (concurrent calls hang), so the probes run **sequentially**
(Tier-3 in the fan-out ladder). This is exactly why `allowed-tools` lists no `Agent`:
this skill spawns nothing; it threads codex calls. Record each probe's `threadId` and
the synthesis `threadId` in the trace; only the committed attack feeds Step 2.

## Step 2 — Defense (Thread 2, fresh codex, decompose + classify)

Open a **second, independent** fresh `mcp__codex__codex` thread (still NOT
`codex-reply`). Paste the attack memo from Step 1 verbatim into the marked slot. Send
EXACTLY:

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are an INDEPENDENT defense reviewer — a checker, NOT the adjudicator
    (deterministic code owns the verdict). A hostile reviewer wrote the
    rejection memo below, citing claim_ids / finding_ids. Read it point-by-point
    against the SAME anchored evidence and rule, honestly, how much of the case
    actually STANDS. You are NOT the paper's defender and NOT the attacker — you check
    whether each ANCHORED accusation holds up on the evidence.

    INPUTS — read directly from your working directory:
      - claims.json — the evidence ledger (claim_id -> VERBATIM text_span).
      - the other auditors' confirmed findings (do NOT read
        adversarial-case-builder.findings.json):
        <paste the FINDINGS_FILES list from Step 0, one filename per line>
    RUN OBSERVABILITY LEVEL L = <L from Step 0>.

    ## The hostile reviewer's rejection memo (the "attack")
    <paste the attack memo VERBATIM from Thread 1, with its inline [id] anchors>

    ## Your task
    Decompose the attack into its atomic rejection points (3-7). If the attack
    concluded the evidence does NOT support a rejection (honest null), return an EMPTY
    array []. For EACH point:
      - record the anchor id(s) it cites (claim_id and/or finding_id);
      - VERIFY the anchor actually supports the point. If the attack over-reads a
        minor / high-FP / observability-demoted finding into something decisive, or
        cites a claim that does not say what the attack claims, say so and classify the
        point already_addressed — the evidence does not license it;
      - classify it:
          already_addressed   — the anchored evidence does NOT sustain this objection
                                (over-read, demoted at L, FP-prone, or the
                                ledger/findings already account for it);
          partially_addressed — a real but bounded issue; not by itself decisive;
          unresolved          — the anchored evidence genuinely leaves the headline
                                unsupported and nothing in the ledger/findings rescues it.
      - OBSERVABILITY: if a point is decidable only at L2 (needs code/results) and
        L < 2, you CANNOT call it refuted OR proven from text. Do NOT classify it
        unresolved (at L<2 the evidence cannot leave the headline "unsupported");
        classify it partially_addressed, set observability_level_required = 2, and
        frame reviewer_action as "verify at L2" — never as an assertion of fabrication.
      - AUTHOR-CHOSEN POSITIONS (a deliberate scope choice, a labelled pilot, a stated
        omission): classify partially_addressed with a note that the position is
        intentional, AND say whether it is sustainable under the attack. Do NOT
        auto-grade already_addressed merely because it is intentional.

    HONESTY: do not inflate to unresolved without a real anchor; do not minimize a
    genuinely evidence-backed objection. Discrepancy-framing only — reviewer_action is
    what a human should CHECK or ASK, never "reject" / "fabricated".

    OUTPUT: a single JSON array and NOTHING ELSE (no prose, no code fence). Each
    element EXACTLY these keys:
      {
        "id": "P1",
        "label": "short label",
        "attack_claim": "the specific accusation, ~30 words",
        "anchors": [{"ref": "C012", "span": "verbatim substring of C012"},
                    {"ref": "citation-forensics:F003"}],
        "classification": "already_addressed | partially_addressed | unresolved",
        "residual_severity": "critical | major | minor",
        "observability_level_required": 0,
        "defense_evidence": "~40 words: does the anchored evidence sustain this point?",
        "reviewer_action": "what a human should CHECK or ASK — never 'reject'"
      }
```

**Persist immediately.** Save the raw response to `"$TRACE/002-defense.response.md"`
(**Write**), plus `"$TRACE/002-defense.request.json"` (the exact prompt sent — attack
memo + paths, no Claude digest) and `"$TRACE/002-defense.meta.json"` (same shape as
Step 1). Keep `defense_thread_id`.

**Failure handling.**
- *Returns prose, not a JSON array*: Step 3 extracts the outermost `[...]`. If there
  is none, re-ask once: "Output ONLY the JSON array, nothing else." Do not hand-author
  the decomposition.
- *MCP hang*: re-invoke the identical prompt as a fresh call; never `codex-reply`.

## Step 3 — Validate + anchor, then render the memo (the anti-slop gate)

Everything the reviewers proposed is now **validated deterministically** by the
executor (claim anchors require a verbatim span; finding anchors require the id to
exist in a sibling findings file). The adjudicator independently re-applies the full
gate stack (span-anchor → observability → FP → memo → surface) as the authoritative
verdict, so this memo can never out-rank it. A **claim anchor** is valid only if its `claim_id`
exists in the ledger AND its `span` is a verbatim, whitespace-normalized **substring
of** that claim (`span in text_span`, never the reverse — appending hallucinated text
to a real claim must fail). A **finding anchor** is valid if its id (bare `Fxxx` or
skill-qualified `skill:Fxxx`) exists in the sibling findings. A point with **no** valid
anchor is uncited rhetoric and is dropped from the load-bearing case. The
informational `disposition` (NOT a verdict) is `kill_constructed` only when an
*unresolved* point rests on a finding the upstream auditors already graded `critical`,
`false_positive_risk: low`, AND decidable at the run's level `L` — the evidence-bound
guarantee made literal. This single command writes both deliverables:

The command is the bash block in `reference/validate-and-render.md`; read it and run it verbatim with `LEDGER`, the attack and defense response paths from `$TRACE`, and the two thread ids. It writes `adversarial-case-builder.memo.md` and `adversarial-case-builder.findings.json` and prints the disposition.

**Scope of this gate:** anchor validation (verbatim-span for claims, id-existence for
findings), classification hygiene, uncited-rhetoric dropping, the informational
disposition, and rendering. It computes **no verdict** — the memo is informational and
the adjudicator decides.

**Failure handling.**
- `DEFENSE_PARSE_FAILED` → re-run Step 2 with the strict-JSON reminder, then re-run
  this command.
- *All attack citations dangling AND the attack made strong accusations* (not an
  honest null) → the reviewer hallucinated its anchors; re-run Step 1 once (it must
  cite real ids). Do not ship a confident memo built on nothing.
- All points `already_addressed` / dropped / empty defense → `disposition=honest_null`.
  This is a correct output; the memo says the paper survives. Do **not** re-run to
  force a kill.

## Step 4 — Trace (forensic; never silently dropped)

After the run, the trace dir from Step 0 must contain both reviewer calls (this repo
ships no `save_trace.sh`, so the files were written directly in Steps 0–2):

```
.aris/traces/adversarial-case-builder/<date>_run<NN>/
  run.meta.json                # {skill, paper_id, run_level_L, findings_files, generated_at}
  001-attack.request.json      # the exact prompt + paths sent (independence audit trail)
  001-attack.response.md       # FULL raw attack memo (input to Step 2 + the memo)
  001-attack.meta.json         # {model, reasoning, thread_id, sandbox}
  002-defense.request.json     # the exact prompt sent (attack memo pasted verbatim, paths only)
  002-defense.response.md      # FULL raw defense JSON (input to Step 3)
  002-defense.meta.json        # {model, reasoning, thread_id, sandbox}
  # (beast only) 0NN-axis-<name>.{request.json,response.md,meta.json} per probe + synthesis
```

Each `request.json` must show the executor sent only **paths + the ledger/findings (+
the attack memo for Thread 2)** — never a Claude-authored digest or opinion about the
paper (the reviewer-independence audit trail). The `response.md` files are the
immutable inputs that Step 3 consumes.

## Step 5 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, **stop here**: the orchestrator globs every
`*.findings.json`, runs the adjudicator, and passes this memo via
`--memo "$(cat adversarial-case-builder.memo.md)"`, where it renders under
*"Adversarial memo (informational — no verdict weight)"*. Running this skill **alone**
is unusual (it normally synthesizes the other auditors), but you may produce the
report yourself — `--ledger` is **required** (it anchors every above-info finding;
without it everything fails closed to `info`):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D"/*.findings.json \
    --ledger "$LEDGER" \
    --paper-id "<PAPER_ID>" --observability-level <L> --taxonomy-version 0.5 \
    --memo "$(cat "$D/adversarial-case-builder.memo.md")" \
    --out "$D/report.json" --md "$D/REPORT.md"
```

The adjudicator applies its gates in order (ANCHOR → OBSERVABILITY → FP-RISK → **MEMO**
→ SURFACE) and computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS,
HARD_FLAGS} from the **other** auditors' findings. The MEMO gate caps every
`adversarial-case-builder` finding at `info`, so this skill **cannot move the verdict**
— by design. No model is in the final decision.

## Output contract

This skill **always** writes, into the ledger's directory:

- `adversarial-case-builder.memo.md` — **canonical.** Attack (verbatim) + per-point
  adjudication + unresolved questions + honest-null/dropped sections + anchoring audit.
  Carries no verdict weight; fed to the adjudicator via `--memo`.
- `adversarial-case-builder.findings.json` — **info-only** mirror (one entry per
  `unresolved` point; possibly `[]`), conforming to `schemas/finding.schema.json`,
  `"skill":"adversarial-case-builder"`, every entry `severity:"info"`. Written even
  when empty for predictable `*.findings.json` globbing; the adjudicator's MEMO gate
  makes it a no-op confirmation. It sets **no `pattern_id`** — this skill originates no
  detection; the patterns live on the findings it cites.
- `.aris/traces/adversarial-case-builder/<date>_run<NN>/` — both raw reviewer calls.

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 5 / the orchestrator).

## Key rules

- **No verdict — by design.** This skill never raises the report's verdict. The
  adjudicator's `MEMO_ONLY_SKILLS` gate caps it at `info`, and it is excluded from
  `dimension_verdicts`. The memo *informs*; the deterministic rules *decide*.
- **Evidence-bound.** Every attack point cites an existing `claim_id` / `finding_id`;
  claim citations carry a verbatim span. Step 3 deletes uncited rhetoric. `span in
  claim`, whitespace-normalized — never `claim in span`. This is exactly what separates
  the skill from generic LLM paper-bashing.
- **No upgrading evidence.** A finding's severity / FP-risk / observability ceiling are
  inherited, never raised. A minor / high-FP / observability-demoted finding cannot
  become a decisive kill — the informational `kill_constructed` heuristic requires an
  unresolved point resting on a finding the upstream auditor graded `critical` (FP low)
  and decidable at L; the adjudicator independently re-applies the full gate stack as
  the authoritative verdict.
- **Synthesis, not detection.** Raise no *new* discrepancy here — only synthesize what
  the ledger + the other auditors already anchored. New flags belong to the auditor
  that owns them.
- **Honest null.** If the anchored evidence is weak, the memo says the paper
  **survives** — it does not manufacture a kill. Expected output, not a failure.
- **Two fresh threads, serial, cross-model.** Attack and Defense are separate
  `mcp__codex__codex` calls (gpt-5.5 xhigh, read-only), never `codex-reply`, never
  concurrent. Reviewer ≠ executor ≠ adjudicator.
- **Observability honesty.** The memo cannot assert code/result-level fraud above the
  run level `L`; findings demoted by observability cannot be resurrected as a "kill"
  (`references/observability-levels.md`).
- **Discrepancy, not accusation.** Argue unsupported / overclaimed / inconsistent;
  questions are CHECK/ASK, never "reject" / "fabricated" / "the authors faked X".
- **Detect-only.** Never edit the audited paper; reviewer sandbox is read-only.
- **Reproducible.** Same ledger + same upstream findings + same reviewer outputs → same
  validated memo + same disposition.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **Auditors haven't run** → run `/consistency-audit` (and the others that apply)
  first; with no findings the case is claims-only and weak. This skill runs LAST.
- **You need to DETECT a new discrepancy** (a number contradiction, a bad citation, a
  missing baseline, code-level fraud) → use the owning detector (`consistency-audit` /
  `citation-forensics` / `baseline-comparison-audit` / `experiment-forensics`). This
  skill only *narrates* what they found.
- **You want a verdict from this skill** → impossible by design; it is capped at
  `info`. Read `REPORT.md`'s `overall_verdict` from the adjudicator instead.
- **You want an AI-text / "looks machine-written" verdict** → out of scope; surface
  hints live in `/presentation-signals` (auxiliary, capped at minor). This repo is
  **not** an AI-text classifier.
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the ledger / findings / paper change (see the fence at the top).

## Review tracing

Trace policy is **forensic** (never silently skipped) — see **Step 4** for the exact
layout: `run.meta.json` + per-call `NNN-<purpose>.{request.json,response.md,meta.json}`
for the attack, the defense, and (under `beast`) each axis probe + synthesis. Every
`request.json` must contain only the paths + ledger/findings (and, for Thread 2, the
attack memo text) that were sent — the reviewer-independence audit trail.
