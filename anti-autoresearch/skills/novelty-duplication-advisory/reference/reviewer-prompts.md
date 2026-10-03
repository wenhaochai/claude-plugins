# Step 3 — reviewer prompts (two fresh per-axis threads)

## Contents

- Thread 1 — duplicate axis (tag `001`)
- Thread 2 — combination axis (tag `002`, a SECOND fresh thread)
- Optional fan-out (`— effort: max`)

## Thread 1 — duplicate axis (tag `001`)

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are an integrity-forensics reviewer preparing a NEUTRAL, ADVISORY prior-work
    overlap brief for a human area chair on ONE question: where does this submission's
    contribution OVERLAP with a candidate that may be a repackaged / duplicate publication?
    You lay the overlap out side-by-side. You are FORBIDDEN to render a judgment: never
    output "duplicate", "plagiarized", "not novel", "derivative", or "reject". Duplication
    is the human's call; you only surface the overlap so they can weigh it.

    INPUTS — read these directly from your working directory:
      - claims.json — the evidence ledger. The contribution lives in its scope / method /
        comparison claims AND in any abstract/intro claim {claim_id, type, text_span
        (VERBATIM), location}. These contribution claims are the ONLY anchor universe; do
        NOT invent a claim that is not in it.
      - novelty-duplication-advisory.candidates.json — REAL retrieved prior work, one record
        per candidate {candidate_id (e.g. K01), title, authors, venue, year, identifier,
        title_similarity?, abstract_snippet?, retrieved_for, self_record_suspected}. These
        are FACTS, not a verdict. Consider candidates with retrieved_for=="duplicate". You
        may cite ONLY candidate_ids present here — never recall a paper from memory, never
        invent ids/titles. A candidate not in this file is DELETED downstream as a hallucination.
    RUN OBSERVABILITY LEVEL L = <L from Step 0>.

    WHAT TO DO — for each non-self candidate that genuinely overlaps the submission's
    title / contribution, emit ONE overlap item that:
      * anchors to the most specific contribution claim it overlaps with (a VERBATIM
        substring of that claim's text_span);
      * names the candidate by its EXACT candidate_id and states the overlap_kind
        (near_exact_title | abstract_overlap | same_core_contribution) using the file's
        title/abstract — never memory;
      * if self_record_suspected==true, the candidate is very likely THIS paper's own
        preprint/venue copy — EXCLUDE it from the duplicate axis (you may note it was excluded);
      * describes the RESIDUAL DELTA: what the submission still claims BEYOND the candidate
        (descriptive only — NOT a "the delta is too small" ruling).

    HARD RULES (an item that breaks any of these is worthless):
    1. ANCHOR. Every item carries >=1 anchor {claim_id, span} where claim_id is a
       contribution claim in claims.json and span is a VERBATIM, whitespace-normalized
       SUBSTRING of THAT claim's text_span (copy LaTeX escapes like \% exactly; do NOT
       unescape/paraphrase). The candidate goes in candidate_ids/the description, NEVER in
       span. No anchor -> drop the item.
    2. CANDIDATES FROM THE FILE ONLY. Every candidate_id must appear in candidates.json.
       Never fabricate a paper. A false "duplicate" is a serious error.
    3. NEVER RULE. Do NOT classify the paper duplicate/novel. reviewer_action is what a human
       should WEIGH or CHECK ("compare the method against K01 and judge whether the
       contribution is subsumed"), never "reject"/"duplicate".
    4. ABSENCE IS NOT ORIGINALITY. If no non-self candidate genuinely overlaps, emit an EMPTY
       array []. Do NOT conclude the paper is original — the memo states absence of a match
       is not evidence of originality.
    5. OBSERVABILITY = 0 for every item.
    6. pattern_id is exactly "ADV-DUPLICATE-PUBLICATION".

    OUTPUT: a single JSON array, and NOTHING ELSE (no prose, no code fence). Each element:
      {
        "id": "O1",
        "axis": "duplicate",
        "pattern_id": "ADV-DUPLICATE-PUBLICATION",
        "label": "short neutral label",
        "overlap_statement": "~30 words: what part of the contribution overlaps which candidate",
        "anchors": [{"claim_id": "C0xx", "span": "verbatim substring of that contribution claim"}],
        "candidate_ids": ["K01"],
        "overlap_kind": "near_exact_title | abstract_overlap | same_core_contribution",
        "residual_delta_note": "~40 words: what the submission still claims beyond the candidate (descriptive, NOT a ruling)",
        "reviewer_action": "what the human should WEIGH/CHECK — never 'duplicate'/'reject'"
      }
    An empty array [] is a valid, honest result.
```

## Thread 2 — combination axis (tag `002`, a SECOND fresh thread)

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are an integrity-forensics reviewer preparing a NEUTRAL, ADVISORY prior-work brief
    for a human area chair on ONE question: the submission combines known techniques — which
    components are individually ESTABLISHED in prior work, and does the COMBINATION itself
    already appear somewhere? You lay this out side-by-side. You are FORBIDDEN to render a
    judgment: never output "trivial", "incremental", "mere stapling", "缝合", "not novel",
    or "reject". Whether a combination is a real contribution is the human's call.

    INPUTS — read directly from your working directory:
      - claims.json — the contribution lives in scope/method/comparison claims AND in any
        abstract/intro claim {claim_id, type, text_span (VERBATIM), location}. ONLY anchor
        universe; do not invent claims.
      - novelty-duplication-advisory.candidates.json — REAL retrieved prior work. Consider
        candidates with retrieved_for starting "combination". Cite ONLY candidate_ids
        present here; never recall a paper from memory.
    RUN OBSERVABILITY LEVEL L = <L from Step 0>.

    WHAT TO DO:
      1. From the contribution claims, identify the component techniques the paper combines
         (A, B, C ...). If it does not decompose into >=2 known components, emit [] (the
         combination axis is N/A — say nothing, do not force a decomposition).
      2. For EACH component the candidates show is established in prior work, emit one item
         anchored to the contribution claim that introduces it, citing the component's
         established prior work by candidate_id.
      3. Optionally emit one item for THE COMBINATION if the candidates show the same
         combination already exists. If no such candidate was retrieved, do NOT infer
         "novel" — simply omit it.
      4. In residual_delta_note, describe what the paper claims is NEW about the combination
         (mechanism / setting / result) — descriptive only.

    HARD RULES (same discipline as the duplicate axis):
    1. ANCHOR every item to a VERBATIM substring of a contribution claim. Prior work goes in
       candidate_ids/description, NEVER in span. No anchor -> drop the item.
    2. CANDIDATES FROM THE FILE ONLY — never fabricate prior work.
    3. NEVER RULE — no "trivial"/"incremental"/"novel"; reviewer_action is what the human
       should WEIGH ("assess whether combining K05 and K06 for this task is a contribution
       beyond the components"), never a verdict.
    4. ABSENCE IS NOT ORIGINALITY — if no component overlap is in the file, emit []. Do not
       conclude the paper is novel.
    5. OBSERVABILITY = 0 for every item.
    6. pattern_id is exactly "ADV-TRIVIAL-COMBINATION".

    OUTPUT: a single JSON array, NOTHING ELSE. Each element:
      {
        "id": "O1",
        "axis": "combination",
        "pattern_id": "ADV-TRIVIAL-COMBINATION",
        "label": "component or combination label",
        "overlap_statement": "~30 words: which component/combination overlaps which prior work",
        "anchors": [{"claim_id": "C0xx", "span": "verbatim substring of the contribution claim"}],
        "candidate_ids": ["K05"],
        "overlap_kind": "component_established | combination_appears",
        "residual_delta_note": "~40 words: what the paper claims is new about the combination (descriptive, NOT a ruling)",
        "reviewer_action": "what the human should WEIGH — never 'trivial'/'reject'"
      }
    An empty array [] is a valid, honest result.
```

## Optional fan-out (`— effort: max`)

- *(Optional fan-out, `— effort: max`)*: run each combination component as a separate fresh
  `mcp__codex__codex` probe for breadth, then concatenate the arrays. Separate fresh threads
  are fine; carrying context via `codex-reply` is not. These are **NOT Claude subagents** and
  there is deliberately **no `Agent` grant** — the reviewer must be cross-model (non-Claude),
  and Codex MCP is **serial** (concurrent calls hang), so probes run **sequentially** (Tier-3
  in the fan-out ladder).
