---
name: proof-derivation-forensics
description: "Detect-only check that a third party's written proofs and derivations establish their theorems: gaps, circularity, invalid steps, symbol drift, smuggled assumptions. Needs the evidence ledger; verdicts need LaTeX source (PDF-only: info). Triggers: \"check this proof\", \"audit the math\", \"证明审计\", \"推导有没有漏洞\"."
argument-hint: [paper-dir | claims.json]
allowed-tools: Bash(*), Read, Write, mcp__codex__codex
---

# Proof & Derivation Forensics — does the written proof hold?

Audit family **G (proof & derivation integrity)** for: **$ARGUMENTS** (requires
`claims.json` from `/evidence-ledger`). A fresh cross-model reviewer reads each
theorem/proof and proposes span-anchored findings; this skill writes
`proof-derivation-forensics.findings.json`. The deterministic adjudicator — not this
skill — computes the verdict.

> 🔒 **Run once per input change; never wrap in `/loop`, `/schedule` or `CronCreate`** (`${CLAUDE_PLUGIN_ROOT}/support/references/run-cadence.md`). Re-run only when the paper or the ledger changes.

> Broken math is the single most-cited "obviously machine-written" tell in real
> reviews ("过不去的步骤用文字糊弄", "车轱辘话复述当证明", "关键公式符号用反"). Unlike the
> surface signals of family F, family-G flaws are **substantive** and **can be
> critical**: a theorem whose proof is circular, skips a load-bearing obligation, or
> takes an invalid step **does not support its claim**. And — crucially — proof
> validity is decidable from the *written* proof: we never need the code or results,
> so family G is **verdict-bearing at L1** (the LaTeX source) and can still reach
> HARD_FLAGS with no repo — but needs that source, because PDF-extracted math is
> unreliable; at an L0 (PDF-only) run a family-G flaw surfaces as `info` only. Adapted from ARIS
> `proof-checker` (per-obligation ledger + 20-category taxonomy + counterexample red
> team) and `formula-derivation` (identity/proposition/approximation/interpretation
> step typing), **reframed from "fix my own proof" to "audit a third party's proof,
> detect-only."** There is no fixing here and no authorship verdict — only "the step
> shown does not hold," with the exact line quoted.

Read `reference/rationale.md` for why family G exists, an example of each flaw, and the honest recall bound (why a pure-symbol step covered by no ledger claim stays at `info`).

## Core principle

**Ledger-anchored, span-verified, decide-from-the-written-proof, reviewer≠adjudicator.**
There is **no deterministic tool** for family G (no arithmetic backbone like
consistency-audit's `check_numeric_consistency.py`) — proof validity is a semantic
judgment. So this skill runs exactly one substantive pass:

- a **fresh cross-model** reviewer pass that reads each theorem + its proof + an
  **extraction-only obligation scaffold** (Step 1) and proposes one finding per
  *undischarged obligation / invalid step / drift / smuggle / circularity*.

Every above-`info` finding conforms to `schemas/finding.schema.json` and **cites a
ledger `claim_id` + a verbatim span** (`references/integrity-forensics-contract.md`
rules 1–2). The model **proposes**; `tools/adjudicate_findings.py` **decides**
(`references/reviewer-independence.md` Layer 2). This skill computes **no verdict**,
and **never edits** the audited paper. We never write "fabricated" or "faked" — we
write, with the line quoted, *the step shown does not hold / the obligation is not
discharged / the symbol's meaning drifted*.

## How this differs from the other auditors (route correctly)

This skill owns only proof-internal validity (family G, decided from the L1 LaTeX source). Abstract-vs-theorem scope drift and results arithmetic → `consistency-audit`; citation existence/context → `citation-forensics`; code/result fraud → `experiment-forensics` (L2); external "first/SOTA" → `needs_external_check`.
Read `reference/routing.md` for the full auditor table and the do-not-raise-here list.

## Constants & Reviewer Calling Convention

```
REVIEWER_MODEL          = gpt-5.5                  # different family from executor (Claude)
REVIEWER_REASONING      = xhigh                    # always; effort never lowers reviewer quality
REVIEWER_SANDBOX        = read-only                # detect-only; never mutate the paper
REVIEWER_CWD            = <paper-dir>              # so it can read claims.json + the proof sources directly
THREAD_POLICY           = fresh mcp__codex__codex per run (and per fan-out theorem group);
                          NEVER mcp__codex__codex-reply
TAXONOMY_VERSION        = 0.5                      # references/hack-pattern-taxonomy.md
OWNED_PATTERNS          = HP-PROOF-OBLIGATION-GAP · HP-PROOF-CIRCULARITY ·
                          HP-DERIVATION-INVALID · HP-SYMBOL-SEMANTIC-DRIFT ·
                          HP-ASSUMPTION-SMUGGLE · HP-UNDEFINED-NOTATION   # family G; emit ONLY these
OBLIGATION_SCAFFOLD     = <TRACE_DIR>/obligation-ledger.md   # Step 1 — EXTRACTION ONLY,
                          not a verdict, NOT claims.json, NOT the anchor substrate
FINDINGS                = proof-derivation-forensics.findings.json   # Step 3 — the ONLY
                          findings file (no deterministic tool exists for family G)
TRACE_POLICY            = forensic (never silently dropped)
TRACE_DIR               = .aris/traces/proof-derivation-forensics/<YYYY-MM-DD>_run<NN>/
```

- **Executor (Claude)** builds nothing of the judgment: it locates the ledger,
  extracts the obligation scaffold (structure only, **never validity**), pre-computes
  the per-theorem anchor candidates, passes **paths + the ledger + the scaffold + the
  checklist** to the reviewer, validates the reviewer's spans, and writes the findings
  file. It never summarizes the proof, pre-judges soundness, or leaks an opinion into
  the prompt (`reviewer-independence.md`).
- **Reviewer (codex / gpt-5.5)** reads `claims.json`, the obligation scaffold, and the
  proof sources; proposes findings; self-reports `false_positive_risk`. It is the
  evidence-extractor / candidate-explainer, **not the judge**.
- **Fresh thread per run.** If you fan out by theorem for breadth, each theorem is a
  **new** `mcp__codex__codex` call — never `codex-reply` carrying one theorem's
  conclusions into another (the bias guard). `codex-reply` is intentionally absent
  from `allowed-tools`.

---

## Step 0 — Preconditions: locate the ledger, read the level, confirm proofs exist

The ledger is the **only** structure this skill anchors to. Resolve it, read the
observability level **L**, `paper_id`, the claim count, the source files, and whether
the paper contains any proof/theorem/derivation to audit (each Bash block is
self-contained — shell state does not persist between calls, so re-derive paths every
step):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
# $ARGUMENTS is a paper-dir OR a claims.json path:
LEDGER="$ARGUMENTS"; [ -d "$LEDGER" ] && LEDGER="$LEDGER/claims.json"
# Only the NO-ARGUMENT case defaults to the CWD ledger. An EXPLICIT argument that
# resolves to a missing claims.json must NOT silently fall back to $(pwd) — that
# could audit the wrong paper; let the NO_LEDGER check below fire instead.
[ -z "$ARGUMENTS" ] && LEDGER="$(pwd)/claims.json"
python3 - "$LEDGER" <<'PY'
import json, sys, os, re
p = sys.argv[1]
if not os.path.isfile(p):
    sys.exit("NO_LEDGER: claims.json not found. Run /evidence-ledger FIRST "
             "(it writes artifact_manifest.json + claims.json).")
d = json.load(open(p, encoding="utf-8"))
paper_dir = os.path.dirname(os.path.abspath(p)) or "."
print("LEDGER       =", os.path.abspath(p))
print("PAPER_DIR    =", paper_dir)
print("PAPER_ID     =", d.get("paper_id", "?"))
print("RUN_LEVEL_L  =", d.get("observability_level", 0))
print("CLAIMS       =", len(d.get("claims", [])))
# Does the paper contain proofs/theorems/derivations to audit?
TH  = re.compile(r"\\begin\{(theorem|lemma|proposition|corollary|claim|conjecture|"
                 r"proof|definition|assumption)\*?\}", re.I)
EQ  = re.compile(r"\\begin\{(equation|align|gather|multline|eqnarray)\*?\}|\\\[", re.I)
TXT = re.compile(r"\b(Theorem|Lemma|Proposition|Corollary|Proof|Q\.?E\.?D\.?)\b")
srcs, hits = [], 0
for s in d.get("source_files", []):
    sp = s.get("path", ""); kind = s.get("kind", "")
    cand = sp if os.path.isabs(sp) else os.path.join(paper_dir, sp)
    if not os.path.isfile(cand): cand = sp
    srcs.append((cand, kind))
    try: t = open(cand, encoding="utf-8", errors="replace").read()
    except OSError: continue
    hits += (len(TH.findall(t)) + len(EQ.findall(t))) if kind == "latex" else len(TXT.findall(t))
print("SOURCE_FILES =", " ; ".join(c for c, _ in srcs) or "(none)")
print("HAS_PROOFS   =", ("yes" if hits > 0 else "no"), f"(markers={hits})")
PY
```

**Carry forward** the absolute `LEDGER` / `PAPER_DIR`, the `SOURCE_FILES`, plus `L`
and `PAPER_ID`, into every step below.

**Failure / edge handling.**
- **`NO_LEDGER`** → stop and tell the user to run `/evidence-ledger` first. This skill
  never re-reads the raw PDF and invents its own structure (contract rule 1).
- **`HAS_PROOFS = no`** (no theorem/lemma/proof/derivation markers) → there is nothing
  for family G to audit (the proof analog of `NOT_APPLICABLE`). Write the empty
  findings file directly — `printf '[]\n' > "$(dirname "$LEDGER")/proof-derivation-forensics.findings.json"` —
  record a trace note (Step 5), and stop. **Silent skip is forbidden**; an empty array
  is a valid, non-silent output the adjudicator reads as "this dimension found
  nothing." Do **not** call the reviewer.
- **`CLAIMS == 0`** → the ledger has no spans to anchor to even if proofs exist; write
  the empty findings file as above, note it in the trace, and stop.
- **`RUN_LEVEL_L == 0`** (PDF-text only) → proceed, but **recall is reduced**: equation
  and theorem-statement spans are poorly captured, so obligation/assumption findings
  that need the LaTeX source to confirm an obligation is undischarged anywhere will
  carry `observability_level_required: 1` and auto-demote to `info` (honest — you can
  suspect from PDF text, you cannot confirm). Family G is at full strength at **L1**.
- **`RUN_LEVEL_L == 2`** → proof checks run identically (they are textual/semantic);
  the extra L2 power (paper-number↔result-file) belongs to `/experiment-forensics`.

## Step 1 — Build the proof-obligation scaffold (EXTRACTION ONLY — never a verdict)

Create this run's trace dir, then extract — for each theorem/lemma/proposition and
its proof — the obligations the theorem creates, **without judging whether any is
discharged**. This adapts `proof-checker`'s Phase 0.5 ledger and `formula-derivation`'s
step typing, under one hard rule:

> **The scaffold EXTRACTS, it does not ADJUDICATE.** Inventorying obligations, typing
> symbols, restating quantifiers, and tagging a step `identity / proposition /
> approximation / interpretation` is *structural extraction*. Whether a step is
> *valid* — whether an obligation is actually discharged — is a correctness verdict
> reserved for the cross-model reviewer (Step 2) and the adjudicator (Step 6). The
> executor records the obligation and a **location pointer** to where the paper claims
> to discharge it (`file:line`) — never its own judgment that the discharge is sound.
> "UNCITED" means *the paper cites no discharge location*, NOT *the executor checked
> the math and it fails*. (See `acceptance-gate.md`: the loop may self-verify that the
> scaffold is **complete**, never that the proofs are **correct**.) The scaffold is
> **not** `claims.json` and **not** the anchor substrate — findings still anchor to
> ledger claims in Step 3.

```bash
LEDGER="<abs path to claims.json from Step 0>"; D="$(dirname "$LEDGER")"
TBASE="$D/.aris/traces/proof-derivation-forensics/$(date +%F)"
NN=1; while [ -e "${TBASE}_run$(printf '%02d' "$NN")" ]; do NN=$((NN+1)); done
TRACE_DIR="${TBASE}_run$(printf '%02d' "$NN")"; mkdir -p "$TRACE_DIR"
echo "TRACE_DIR = $TRACE_DIR"   # carry this absolute path into Steps 2 and 5
```

Use **Read** to open each file in `SOURCE_FILES` and locate every
`\begin{theorem|lemma|proposition|corollary|claim|conjecture}` … `\end{...}` block and
its matching `\begin{proof}` … `\end{proof}` (or the derivation paragraphs that play
that role). For each, extract the entries below.

**Anchor candidates (the bridge to Step 3's gate).** For each theorem, list the
ledger `claim_id`s whose `text_span` overlaps the theorem+proof line window — these are
the *only* places a finding on that theorem can ground. Run (per theorem block):

```bash
LEDGER="<abs path to claims.json>"; FILE="<source file of this theorem>"
START="<thm block start line>"; END="<proof block end line>"
python3 - "$LEDGER" "$FILE" "$START" "$END" <<'PY'
import json, os, sys
ledger, f, a, b = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
d = json.load(open(ledger, encoding="utf-8"))
base = os.path.basename(f)
for c in d.get("claims", []):
    loc = c.get("location", {}) or {}
    ln = loc.get("line")
    same = base == os.path.basename(loc.get("file", "") or "")
    if same and isinstance(ln, int) and a - 2 <= ln <= b + 2:
        prev = " ".join((c.get("text_span", "") or "").split())[:90]
        print(f'{c["claim_id"]:>6}  {c.get("type",""):<10}  L{ln}  "{prev}"')
PY
```

Then **Write** the scaffold to `$TRACE_DIR/obligation-ledger.md` using this template
(one block per theorem; record pointers, never verdicts):

```md
# Proof-Obligation Scaffold — <PAPER_ID>   (EXTRACTION ONLY — NO validity verdict)
> Structures the reviewer's per-obligation pass. NOT claims.json, NOT the anchor
> substrate, contains NO "proved / sound / valid" judgments. Soundness is the Step-2
> reviewer's call; the verdict is the Step-6 adjudicator's.

## T1 — <theorem name / \label{...}>   [<file>:<line-range>]
- Statement (verbatim): "<exact theorem statement>"
- Canonical quantified form: ∀… ∃… s.t. …      (or: UNCLEAR — needs disambiguation)
- Stated hypotheses: H1 …; H2 …
- Typed symbols: κ: scalar ∈(0,1), dep (d,Σ); u*: vector ∈ℝ^d; B: matrix, sym PSD …
- Headline-dependent?: yes/no   (does the abstract / main claim rest on T1?)
- Proof location: <file>:<line-range>
- Obligations (every nontrivial step; tag identity|proposition|approximation|interpretation;
  record claimed discharge location — a pointer, NOT a validity judgment):
    - O1 [proposition]   "<step text>"   — claimed discharge: <file>:<line> | UNCITED
    - O2 [identity]      "<step text>"   — …
    - O3 [approximation] "<step text>"   — enters at <line>; later used as exact? pointer
    - O4 [interpretation]"<prose step>"  — presented as derivation? pointer
- Imported results applied: <\cite{} / named thm> @ <line>
  — hypotheses to verify at point of use: …
- Anchor-candidate claim_ids (from the helper above): C0xx, C0yy, …   (statement: C0xx)
```

**Breadth for a large multi-theorem paper (no `Agent` grant).** Scaffold
*construction* is pure structural extraction — walk the theorems **sequentially**.
This skill **spawns nothing**: `allowed-tools` grants no `Agent` (matching the other
Anti-Autoresearch auditors, which thread codex calls rather than fork subagents), so
there is no executor-side fan-out here. Breadth, when you want it, happens on the
**reviewer** side — issue one fresh `mcp__codex__codex` call per theorem in Step 2
(never `codex-reply`). Either way the extraction **never adjudicates**, and you must
**merge all theorem blocks into one scaffold before** looking for a cross-theorem
dependency **cycle** (semantic circularity for `HP-PROOF-CIRCULARITY`): a per-theorem
view misses exactly the cross-theorem cycles this skill exists to catch.

## Step 2 — Cross-model per-obligation review (reviewer ≠ adjudicator)

Open a **fresh** `mcp__codex__codex` thread (the Reviewer Calling Convention above)
and send it the checklist. The reviewer reads `claims.json`, the scaffold, and the
proof sources from its `cwd`; it judges from the **full proof**, but **every finding
must anchor to a ledger `claim_id`** — an anchor candidate from the scaffold whose
`text_span` verbatim-contains the failing fragment. Send EXACTLY (substitute the
absolute `PAPER_DIR`, the `L` value, and the scaffold path from Steps 0–1):

The exact `mcp__codex__codex` call (envelope, hard rules, six-item checklist, output schema) is in `reference/reviewer-prompt.md`. Read it and send it verbatim with the substitutions above.

Immediately persist the reviewer's raw response with the **Write** tool to
`$TRACE_DIR/001-proof-review.response.md` (the dir from Step 1) before parsing. It is
the forensic record and the input Step 3 reads. (Write the other trace files now or in
Step 5 — see Step 5 for the exact set.)

**Failure handling.**
- *MCP stall / hang* (common in long sessions): re-invoke the **identical** prompt as a
  **fresh** `mcp__codex__codex` call (gpt-5.5, xhigh) — never `codex-reply`.
- *Reviewer returns prose, not a JSON array*: the Step 3 validator already extracts the
  outermost `[...]`; if there is none, re-ask once with "Output ONLY the JSON array,
  nothing else." Do not hand-author findings on the reviewer's behalf.
- *Many theorems / `— effort: max`*: fan out — issue one **separate fresh**
  `mcp__codex__codex` call per theorem (each gets only that theorem's scaffold block +
  its anchor candidates), and concatenate the arrays before Step 3. Fresh threads are
  fine; carrying context across them via `codex-reply` is not (the bias guard).

## Step 3 — Validate + anchor (the anti-hallucination gate)

The executor enforces the ANCHOR gate **before** keeping anything — exactly the rule
`tools/adjudicate_findings.py` re-applies, so nothing you keep gets silently rejected
downstream. The span must be a verbatim, whitespace-normalized **substring of** the
cited claim (`span in base`, never `base in span` — appending hallucinated text to a
real claim must fail). This validator also keeps the output **strictly family-G**:

Run the validator script in `reference/validate-anchor.md` (set `LEDGER`, `PROPOSED` = the saved raw response, `OUT` as shown there), with `CLAUDE_PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT}"` exported first; it writes `proof-derivation-forensics.findings.json`.

**Scope of this gate: anchoring + schema hygiene + family-G enforcement** — verbatim-span
anchoring, enum coercion, non-G pattern rejection, observability fallback, and
cross-model provenance — so every kept finding is well-formed, honestly anchored, and
in this skill's lane. It does **not** compute the verdict, the FP-risk cap, or the
observability *downgrade* against the run level; those belong to
`tools/adjudicate_findings.py`, the single decider. Note this skill applies **no
critical-floor** (unlike consistency-audit's `HP-SUSPICIOUS-REGULARITY`): family-G
flaws legitimately reach `critical`, so the reviewer's honest `severity` + `false_positive_risk`
are preserved verbatim and the adjudicator's FP cap does the rest.

**Failure handling.** A `JSONDecodeError` means the reviewer output was malformed →
re-run Step 2 with the strict-JSON reminder. If a finding loses all evidence, it is
*kept as info* (never silently dropped — the forensic record stays).

## Step 4 — Emit (one file)

Step 3 wrote `proof-derivation-forensics.findings.json` (validated family-G findings).
This is the **only** findings file for this skill — there is no deterministic
companion (no arithmetic tool exists for family G; proof validity is semantic). If the
reviewer found nothing (or `HAS_PROOFS = no` / `CLAIMS == 0`), the file is `[]` — write
it anyway. **Silent skip is forbidden**: the orchestrator and the standalone
adjudicate command both expect the file to exist at a predictable path. The id
namespace is `F###`, disjoint from every other skill's, so the orchestrator's glob
concatenates it exactly once.

## Step 5 — Trace (forensic; never silently dropped)

You created `$TRACE_DIR` in Step 1
(`.aris/traces/proof-derivation-forensics/<date>_run<NN>/`, `NN` from `01`). This repo
ships no `save_trace.sh`, so use the **Write** tool to write these files into it (the
`response.md` and `obligation-ledger.md` were already saved in Steps 1–2):

```
$TRACE_DIR/
  run.meta.json                  # {skill, paper_id, run_level_L, taxonomy_version:"0.5", has_proofs, generated_at}
  obligation-ledger.md           # Step 1 — the EXTRACTION-ONLY scaffold (no verdicts)
  001-proof-review.request.json  # the exact prompt sent (paths + scaffold + checklist, no proof summaries)
  001-proof-review.response.md   # the FULL raw reviewer response (input to Step 3)
  001-proof-review.meta.json     # {model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}
```

For a per-theorem fan-out, write `00N-proof-review.{request.json,response.md,meta.json}`
per theorem call (one triple per fresh thread). The `request.json` is the independence
audit trail — it must show the executor sent only **paths + the scaffold + the
checklist**, never a digest or pre-judgment of the proof. Paste the actual codex
`thread_id` into each per-call `.meta.json`.

## Step 6 — Hand off, or adjudicate standalone

Within `/anti-autoresearch`, stop here: the orchestrator globs every `*.findings.json`,
runs the adjudicator over the union of all skills' findings, and emits `REPORT.md` +
`report.json`. When running this skill **alone**, you may produce the report yourself —
`--ledger` is **required** (it re-verifies each finding quotes a real ledger span; the
adjudicator will not run without it, and its anchor gate is itself fail-closed — an
above-info finding it cannot anchor is demoted to `info`):

```bash
ROOT="${CLAUDE_PLUGIN_ROOT}/support"
LEDGER="<abs path to claims.json>"; D="$(dirname "$LEDGER")"
python3 "$ROOT/tools/adjudicate_findings.py" \
    --findings "$D/proof-derivation-forensics.findings.json" \
    --ledger "$LEDGER" \
    --paper-id "<PAPER_ID>" --observability-level <L> --taxonomy-version 0.5 \
    --out "$D/report.json" --md "$D/REPORT.md"
```

The adjudicator applies, in order: ANCHOR → OBSERVABILITY → FP-RISK → MEMO → SURFACE
gates, then computes `overall_verdict` ∈ {CLEAN_GIVEN_EVIDENCE, SOFT_FLAGS,
HARD_FLAGS}. This skill is **verdict-bearing** (`dimension: proof`) and is neither
memo-only nor surface-only, so a span-anchored **critical** family-G finding that is
decidable at `L` (e.g. a circular proof, or an invalid step the headline depends on)
**reaches HARD_FLAGS** — with `false_positive_risk: low`, since the FP-RISK gate caps
high→minor and medium→major. No model is in the final decision. Treat a single-skill
report as a PREVIEW — the paper's verdict comes from the orchestrator over all
dimensions.

## Output contract

This skill **always** writes, into the ledger's directory:

- `proof-derivation-forensics.findings.json` — Step 3/4, a JSON array
  (`schemas/finding.schema.json`); validated family-G findings (or `[]`). Each
  above-info finding carries `evidence[].claim_id` + a verbatim `span`,
  `observability_level_required: 1` (family-G is verdict-bearing at L1), a `pattern_id`
  ∈ the five owned patterns, and `reviewer.deterministic: false`.
- `.aris/traces/proof-derivation-forensics/<date>_run<NN>/` — Steps 1/2/5: the
  extraction-only `obligation-ledger.md` and the raw reviewer call(s).

It writes **no verdict and no report** of its own — `report.json` / `REPORT.md` come
only from `tools/adjudicate_findings.py` (Step 6 / the orchestrator). The
human-readable rendering is the orchestrator's job, not this skill's.

## Key rules

- **Decide from the written proof.** Validity of written mathematics is decidable from
  the LaTeX source (L1) — verdict-bearing at L1, never needing code or results; an L0
  PDF-only read surfaces `info` only, because PDF-extracted math is unreliable. We assert
  *the step shown does not hold / the obligation is not discharged*, never *fabricated* /
  *faked* / *reject*. The tool is agnostic to authorship — it audits the argument, not provenance.
- **No span → no severity.** Every `critical`/`major`/`minor` finding must quote a
  verbatim substring of a real ledger claim. Enforced by the executor (Step 3) and
  again by the adjudicator; unanchored findings are demoted to `info`, never deleted.
- **Span direction + escapes.** Anchoring is `span in claim.text_span`
  (whitespace-normalized **only**), never the reverse. Quote LaTeX escapes (`\le`,
  `\%`, `\alpha`) exactly; un-escaping breaks the match.
- **Recall is bounded by the ledger; that is honest, not a bug.** The extractor has no
  theorem/proof spans — a pure-symbol step covered by no `number`/`scope`/`citation`
  claim cannot rise above `info`. Step 1's anchor-candidate list tells the reviewer
  where it can ground; uncovered steps stay `info`. Recall is materially higher at L1.
- **Family G only.** Emit only the five owned patterns. Abstract-vs-theorem scope →
  consistency-audit + adversarial-case-builder; citation existence/context →
  citation-forensics; results arithmetic → consistency-audit; code/result fraud →
  experiment-forensics. The Step-3 validator drops any non-G `pattern_id`.
- **Critical is earned, not floored.** Family-G findings legitimately reach `critical`
  (circular proof; invalid step / smuggle / inverted symbol the headline depends on) —
  but only with `false_positive_risk: low` and `observability_level_required ≤ L`.
  Counterexample-first: try to break the step before grading it.
- **Reviewer ≠ adjudicator.** The model proposes findings; `adjudicate_findings.py`
  decides the verdict. This skill emits findings only.
- **Cross-model, fresh thread.** Reviewer is a different family (gpt-5.5 xhigh); every
  run — and every fan-out theorem — is a new `mcp__codex__codex` thread; `codex-reply`
  is never used (the bias guard).
- **Scaffold extracts, never adjudicates.** The obligation ledger records obligations +
  location pointers only; soundness is the reviewer's call, the verdict the
  adjudicator's. The scaffold is not `claims.json` and not the anchor substrate.
- **Detect-only.** Never edit the audited paper (reviewer sandbox is read-only; `Edit`
  is absent from `allowed-tools`). There is no fix loop — that is `proof-checker`'s
  job, on your own paper, not this third-party forensic tool's.
- **Reproducible.** Same ledger + same findings → same verdict, no model in the loop.

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **The paper has no proofs/theorems/derivations** (`HAS_PROOFS = no`) → nothing for
  family G to audit; write `[]` and stop (the proof analog of `NOT_APPLICABLE`).
- **You want to FIX a proof, or it's your OWN paper** → use ARIS `/proof-checker`
  (verify-and-fix, re-review rounds, audit report). This skill is detect-only third-party
  forensics: it proposes findings and never edits.
- **The mismatch is abstract/title generality vs a narrow theorem** →
  `/consistency-audit` owns `HP-THEOREM-SCOPE-DRIFT`; the headline framing →
  `/adversarial-case-builder`. Emit only the proof-internal smuggle here.
- **You need citation existence / wrong-context** → `/citation-forensics` (this skill
  only checks whether a cited theorem's *hypotheses* were discharged at the point of
  use).
- **You need results-table arithmetic / aggregation / number coherence** →
  `/consistency-audit`.
- **You need code/result-level fraud** (fake GT, self-normalization, phantom numbers)
  → `/experiment-forensics` at **L2**; family G is decided at L1 and never reaches for code.
- **You want an "is this AI-written math" verdict** → out of scope. We assert a step
  does not hold, not who or what wrote it; surface hints live in
  `/presentation-signals` (auxiliary, capped at minor).
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the paper or ledger changes (see the fence at the top).

## Review tracing (`.aris/traces/proof-derivation-forensics/<date>_run<NN>/`)

Every run leaves a forensic trail under
`.aris/traces/proof-derivation-forensics/<YYYY-MM-DD>_run<NN>/` (`NN` from `01`,
incremented per run/day — created in Step 1):

| File | Written | Content |
|------|---------|---------|
| `run.meta.json` | Step 5 | `{skill, paper_id, run_level_L, taxonomy_version:"0.5", has_proofs, generated_at}` |
| `obligation-ledger.md` | Step 1 | the extraction-only obligation scaffold (statements, typed symbols, obligations, anchor candidates) — **no validity verdicts** |
| `00N-proof-review.request.json` | Step 5 | the exact prompt sent to the reviewer (paths + scaffold + checklist, no proof summary / no pre-judgment) — the **independence audit trail** |
| `00N-proof-review.response.md` | Step 2 | the FULL raw reviewer response (the input Step 3 parsed) |
| `00N-proof-review.meta.json` | Step 5 | `{model:"gpt-5.5", reasoning:"xhigh", thread_id, sandbox:"read-only"}` |

`N` is `001` for a single review, or one triple per theorem under fan-out. Traces are
**never silently dropped**: they let a human re-audit that the reviewer saw only
paths + the scaffold + the checklist (not a digest of the proof), that each finding's
span is a verbatim ledger substring, and that the verdict is reproducible from the
saved findings + the adjudicator alone.
