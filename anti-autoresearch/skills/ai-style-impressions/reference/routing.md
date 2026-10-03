# AI Writing-Style Impressions — routing and the 13 AIS patterns

## Contents

- How this differs from the other auditors (route correctly)
- When NOT to use this skill

## How this differs from the other auditors (route correctly)

| Auditor | Question it answers | Verdict weight |
|---------|---------------------|----------------|
| **`ai-style-impressions`** (this) | **What AI writing-STYLE tells does a reviewer notice? Named, located, itemized impressions — NOT integrity** | **ZERO (forced to `info`, separate report section, excluded from `overall_verdict`)** |
| `presentation-signals` | Checkable *surface* tells (dup tables, thin/LLM figures, page padding, leftover pipeline strings) | capped at `minor` (`SOFT_FLAGS` at most) |
| `consistency-audit` | Does the paper contradict ITSELF / described method = evaluated method? | full |
| `experiment-forensics` | Are the reported numbers what the code computes? (fake GT, self-norm, phantom — L2) | full |
| `baseline-comparison-audit` | Right baselines present, tuned, "SOTA" earned? | full |
| `citation-forensics` | Do the cited papers exist + support the claim they are used for? | full |
| `eval-design-forensics` | Evaluation validity (leakage / judge bias / selective reporting)? | full |
| `proof-derivation-forensics` | Proof gaps / circularity / invalid steps / undefined notation? | full |
| `adversarial-case-builder` | Strongest evidence-bound rejection memo | ZERO (advisory memo) |

**Stay in lane.** This skill emits **only** the 13 `AIS-*` style patterns — nothing
else. An `AIS-*` impression is the *lowest-stakes* thing in the report by construction
(it carries no verdict weight at all); **never** use it to carry a substantive
accusation. When a style tell is actually a substantive integrity problem, **hand it
off** (do not encode it as an AIS impression):

| Pattern (`AIS-*`) | The style impression (gross cases only) | Not-necessarily-AI (high FP — the `fp_case`) | If it is actually SUBSTANTIVE → route to |
|-------------------|------------------------------------------|----------------------------------------------|------------------------------------------|
| `AIS-NARRATIVE-ARC-BREAK` | abrupt 1–2¶ intro / dump-like or vague abstract; no background→contribution→evidence arc | terse-but-clear abstract; non-native phrasing; field conventions | argument chain truly breaks → `HP-ARGUMENT-CHAIN-BREAK` (`consistency-audit`) |
| `AIS-LLM-PHRASE-TICS` | generic LLM tics overused ("it is worth noting" / "值得注意的是" / "意义在于", "not only…but also", chains of however/therefore/moreover, "therefore" mid-sentence, clichéd em-dash/semicolon, flowery empty adverbs like *elegantly* / *theoretically*) | honest LLM-assisted writing; non-native English; house style (**HUGE FP** — gross cases only) | **never routes** (pure style) |
| `AIS-DEFENSIVE-HEDGE` *(also Step 1)* | pervasive "we do not claim…" / "not X but rather Y" defensive framing instead of stating what was done | one scoping sentence; Limitations hedges are expected; **some venues penalize the ABSENCE of caveats** | a hedge reveals a real scope/eval limitation → `HP-SCOPE-INFLATE` (B) / `eval-design-forensics` (H) |
| `AIS-JARGON-STUFF` | dense term-stuffing where the surrounding argument carries no content | genuinely dense, correct technical writing (**very high FP**) | **never routes** |
| `AIS-INVENTED-CODENAME` | undefined internal-project-flavored run/experiment codename used as if defined (e.g. "Experiment Set Gamma") | legitimate named methods / benchmarks / release tags | points to a missing results file → `HP-MISSING-REPRO-ARTIFACT` / `HP-PHANTOM-RESULT` (D) |
| `AIS-CLAUSE-FORMULA-WALL` | fragmented "short clause then a wall of formulas"; formulas dumped without prose connective | dense-but-correct theory; field norms | a load-bearing symbol is actually UNDEFINED → `HP-UNDEFINED-NOTATION` (G) |
| `AIS-GRATUITOUS-PSEUDOCODE` | pseudocode/algorithm blocks that merely restate the prose / add no operational content | genuinely helpful algorithm listings | the algorithm CONTRADICTS the described method → `HP-METHOD-DRIFT` (`consistency-audit`) |
| `AIS-BULLET-LIST-OVERUSE` | prose organized as many bullets; sequential/progressive logic flattened into parallel-looking bullets | legitimate enumerations; checklists | **never routes** |
| `AIS-BOLD-MODULE-SPAM` | verbose module names with excessive bolding / acronym staging | reasonable emphasis; defined acronyms | the SAME module gets incompatible abbreviations → `HP-ACRONYM-DRIFT` (B, `consistency-audit`) |
| `AIS-RESTATE-OVERCLAIM` | rhetorical restatement loop — repeatedly re-asserting "we propose an X / we do an X" | legitimate signposting | the claim EXCEEDS the evidence → `HP-SCOPE-INFLATE` (B) / family H |
| `AIS-FOCUS-DRIFT` | high-level motivation suddenly pivots to a minor implementation detail / over-emphasizes an unnecessary requirement | modular paper with explicit cross-refs | the motivation→method→experiment chain substantively breaks → `HP-ARGUMENT-CHAIN-BREAK` (B) |
| `AIS-SINGLE-STYLE-FIGURES` | figures share a generic generated visual grammar / single-style AI illustrations | legitimate consistent house figure style; conceptual teasers | checkable figure-vs-content thinness stays `HP-LLM-FIGURE` / `HP-THIN-FLOAT` (family F, `presentation-signals`) |
| `AIS-APPENDIX-DUMPING-GROUND` | appendix reads like unintegrated trace / dumping; AI-trace heavy | legitimately long supplementary detail | CONTRADICTS the main text → `HP-APPENDIX-CONTRA` (B); exact assistant/template artifact → `HP-PIPELINE-ARTIFACT` (F); affects reported data → family D |

(The pure-style ids above migrated **out of** taxonomy §F into this zero-weight AIS
track in **v0.5**; see `DEPRECATED_STYLE_PATTERNS` in `tools/adjudicate_findings.py`,
which keeps the old §F ids as deprecated aliases forced to zero weight so a stale
`findings.json` can never push them to `SOFT_FLAGS`.)

## When NOT to use this skill

- **No `claims.json` yet** → run `/evidence-ledger` first; this skill never invents
  structure from the raw PDF.
- **You want an AI-text / "looks machine-written" / authorship verdict or score** → out
  of scope **by design**. AIS records style impressions, never provenance; for
  authorship detection use a dedicated tool (Pangram / GPTZero / Binoculars).
- **You found a real integrity problem** → route it to the owning auditor, not here:
  numeric/method self-contradiction → `/consistency-audit`; citation existence /
  wrong-context → `/citation-forensics`; "SOTA" / baseline integrity →
  `/baseline-comparison-audit`; code/result fraud (fake GT, self-norm, phantom) →
  `/experiment-forensics` at L2; proof gaps / undefined notation →
  `/proof-derivation-forensics`; evaluation validity → `/eval-design-forensics`;
  checkable surface tells (dup tables, thin/LLM figures, padding, pipeline strings) →
  `/presentation-signals`.
- **As the basis for a reject / accusation** → never. An AIS impression carries zero
  verdict weight; the strongest thing it can do is say "here is a located style tell a
  reviewer might react to — look closer, and route it if it is actually substantive."
- **On a timer** → never `/loop` / `/schedule` / `CronCreate` this skill; re-fire only
  when the paper or ledger changes (see the fence at the top).
