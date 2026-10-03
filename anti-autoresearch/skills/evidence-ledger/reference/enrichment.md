# Evidence Ledger — Step 3 enrichment mapping and reviewer prompt

## Contents

- Content mapping (no new `type` vocabulary)
- Reviewer prompt

## Content mapping (no new `type` vocabulary)

**No new `type` vocabulary — broadened *content* on the existing schema types.** Every
new span rides on a `claims.schema.json` `type` the deterministic layer and Step 4
already allow, so the anti-hallucination gate is unchanged and `claims.json` stays
schema-valid. The mapping — *what new content the enrichment surfaces → which existing
`type` carries it → which family/pattern anchors to it*:

| New span the enrichment surfaces | Carrying `type` | Anchors for (family · pattern) |
|----------------------------------|:---------------:|--------------------------------|
| theorem / lemma / proposition **statement** (incl. its stated assumptions) | `scope` | B · `HP-THEOREM-SCOPE-DRIFT` · G · `HP-PROOF-OBLIGATION-GAP` |
| stated **assumption / hypothesis** (standalone) | `scope` | G · `HP-ASSUMPTION-SMUGGLE` |
| **definition** of a symbol / operator / construct | `method` | G · `HP-SYMBOL-SEMANTIC-DRIFT` |
| **proof step / derivation transition** (symbolic) | `method` | G · `HP-DERIVATION-INVALID`, `HP-PROOF-CIRCULARITY` |
| **formula / equation** (symbolic, non-numeric) | `method` | G · `HP-DERIVATION-INVALID`, `HP-SYMBOL-SEMANTIC-DRIFT` |
| load-bearing **conclusion** (causal / equivalence / relational) | `comparison` | B · `HP-CAUSAL-EVIDENCE-LEAP` |
| the **motivation / problem-framing** span | `scope` | B · `HP-ARGUMENT-CHAIN-BREAK` |
| **reproducibility-artifact reference** (code / prompt / config present or "will release") | `artifact_ref` | D · `HP-MISSING-REPRO-ARTIFACT` |

> These are **anchors, not findings.** The ledger never says a proof is circular, an
> assumption is smuggled, a chain is broken, or an artifact is missing — it only
> captures the verbatim span so the family-B/D/G reviewer has a `claim_id` to quote.
> The judgment stays in the auditor; the verdict stays in
> `tools/adjudicate_findings.py`. Family-G recall is highest at **L1**: equation and
> theorem-statement spans carry stable line numbers, which lets
> `proof-derivation-forensics` scaffold per-theorem anchor candidates by line window —
> so the prompt below asks the reviewer to include `line` whenever it extracts from
> LaTeX.

## Reviewer prompt

```text
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <PAPER_DIR>
  prompt: |
    You are an ADDITIVE claim extractor for an evidence ledger. You are NOT a
    reviewer and NOT a judge: do not assess correctness, do not propose findings, do
    not assign severity or any verdict. Your ONLY job is to surface SEMANTIC claims a
    regex pass misses, each anchored to a VERBATIM span of a real source file.

    Source files (use these EXACT path strings in location.file):
    [list the paths from claims.json -> source_files[].path]

    The deterministic ledger already extracted these (do NOT duplicate them):
    [paste the claim_id + text_span list from claims.json]

    ADD claims ONLY of these SEVEN schema types (numbers and table cells are already
    covered by the deterministic layer — do NOT emit `number` or `table_cell`, and do
    NOT invent any new type string). Each type's CONTENT is broadened below to carry the
    proof/derivation + structure spans the v0.4 family-B/D/G auditors anchor to:
      - method      : the sentence(s) that DEFINE the proposed method / its key
                      conditions (e.g. "no test-time labels", backbone, training data);
                      ALSO a formal **definition** of a symbol/operator/construct, a
                      **proof step / derivation transition**, or a **formula/equation**
                      stated symbolically (for family G — copy the math VERBATIM,
                      including every \command, subscript, superscript, and delimiter).
      - scope       : an explicit scope/generality/limitation sentence the regex missed;
                      ALSO a **theorem/lemma/proposition statement** (you MUST include
                      its stated assumptions/hypotheses in the span, not just the
                      conclusion), a standalone **stated assumption**, or the
                      **motivation / problem-framing** sentence the intro rests on
                      (for families B and G).
      - baseline    : the sentence or list naming the baselines compared against.
      - comparison  : a sentence ASSERTING a comparison ("our method outperforms X") —
                      the framing, not the numbers; ALSO a load-bearing **conclusion**
                      that asserts a causal / equivalence / "therefore" relation
                      ("A correlates with B, therefore A causes B") for family B.
      - citation    : a sentence whose citation is load-bearing for a specific claim.
      - caption     : a table/figure caption the extractor missed.
      - artifact_ref: a reference to a named result file / table / appendix item; ALSO a
                      **reproducibility-artifact reference** — code/repo/prompt/config
                      the paper ships or promises ("code at github.com/…", "we will
                      release", "prompts in App. C", "hyperparameters in Table 5") —
                      for family D. Capture the EXACT sentence; do NOT judge whether the
                      artifact is sufficient, present, or fake.

    HARD RULES (a violation gets your item silently dropped by the merger):
      - Use ONLY the seven types above. A new/unknown type string is dropped.
      - text_span MUST be copied CHARACTER-FOR-CHARACTER from the named file
        (including LaTeX markup like \cite{...}, \%, \le, \alpha, $...$). If unsure it
        is verbatim, OMIT it. Do NOT unescape, re-LaTeX, normalize, or "tidy" math.
      - NEVER introduce, alter, or "tidy" a number. Do NOT emit a `value` field.
      - For a theorem (`scope`), the span MUST include the stated assumptions, not just
        the claim. For an assumption anchor, prefer the span stating the hypotheses.
      - For a conclusion (`comparison`), include the inferential connective
        ("therefore"/"thus"/"hence"/"so") so the causal/equivalence leap is in the span.
      - For an artifact_ref, capture the presence/promise sentence verbatim; the ledger
        records that the reference EXISTS, it NEVER rules the artifact missing or fake.
      - Prefer to include `line` when the source is LaTeX, so the proof/structure
        auditors can scaffold per-theorem anchor candidates by line window.
      - location.file MUST be one of the source paths above.

    Output ONLY a strict JSON array (no prose, no markdown fence) of objects:
      {"type":"<one of the seven types>","text_span":"<verbatim>",
       "location":{"file":"<one of the listed paths>","line":<int — include when LaTeX>,
                   "section":"abstract|intro|method|experiments|theorem|proof|appendix|..."}}
    Output [] if you find nothing new.
```
