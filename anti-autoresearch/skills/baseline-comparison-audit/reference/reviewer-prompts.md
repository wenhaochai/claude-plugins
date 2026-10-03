# Baseline Comparison Audit — reviewer prompts

## Contents

- Step 3 — completeness prompt (HP-MISSING-BASELINE)
- Step 4 — fairness + significance + cross-row delta prompt

## Step 3 — completeness prompt (HP-MISSING-BASELINE)

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are a baseline-COMPLETENESS forensics reviewer. You judge ONE thing: given
    what this paper claims ("state-of-the-art / best / first / outperforms prior
    work") on a benchmark, is an OBVIOUS, RECENT, RELEVANT baseline absent from the
    comparison? You do NOT judge whether numbers are real and you do NOT grade the
    paper. Describe a discrepancy to CHECK, never an accusation; hand off what you
    cannot ground.

    INPUTS (in your working directory — read them directly):
      - claims.json — the evidence ledger. The SOTA/comparison LANGUAGE lives in
        type:"comparison" and type:"scope" claims; the PRESENT baseline set in
        type:"baseline" claims; reported values + table rows in type:"number" /
        type:"table_cell"; figure/table labels in type:"caption". This is the ONLY
        structure you reason over; each claim = {claim_id, type, text_span (VERBATIM),
        location, value?}. You MAY re-open a source file to confirm a span is real,
        but you may NOT introduce a claim that is not in the ledger.
    REFERENCE (external facts gathered by the executor — cite the source in your
    finding; treat as GIVEN data, NOT a verdict, do not second-guess):
      - Profile row (PROFILE_VERSION 0.1): expected baseline FAMILIES = [...];
        matched-budget axis = [...].
      - Live leaderboard (<URL>, accessed <DATE>): top current systems + their
        dates/venues = [...].
      - Candidate expected set (name · same_benchmark? · published_before_paper? ·
        source): [paste expected_baseline_set.json from Step 2, or "NO_PROFILE /
        search unavailable"].
    ANCHOR TARGETS (the SOTA/comparison claims — claim_id + verbatim):
      [paste the anchor claims from Step 1]
    BASELINES THE PAPER REPORTS (mechanical extraction — may be incomplete):
      [paste the baseline-list claims + the grep names from Step 1]
    RUN OBSERVABILITY LEVEL L = <L from Step 0>.

    HARD RULES (a finding that breaks any of these is worthless):
    1. ANCHOR. Every finding above "info" MUST carry >=1 evidence {claim_id, span}
       where claim_id EXISTS in claims.json and span is a VERBATIM whitespace-
       normalized SUBSTRING of THAT claim's text_span (no paraphrase). The primary
       anchor is the SOTA/outperforms claim (a comparison/scope claim); the named
       missing baseline goes in `description`, never as the anchor. ALWAYS anchor —
       even a needs_external_check finding — so it stays navigable.
    2. DISCREPANCY, NOT ACCUSATION. Never "reject", "fabricated", "the authors hid X".
    3. OBSERVABILITY. A missing-baseline-as-STATED is decidable from the manuscript
       => observability_level_required = 0.
    4. HAND OFF WHAT YOU CANNOT SETTLE (the core rule of this step). Emit
       HP-MISSING-BASELINE above info ONLY when ALL hold: (a) a SOTA/best/outperforms
       claim is anchored; (b) a SPECIFIC, NAMED baseline is absent from the present
       set; (c) per the supplied sources that baseline is an ESTABLISHED, publicly-
       available, PRE-DATING standard for THIS exact benchmark (not concurrent, not
       post-dating, not unavailable, not justified-as-omitted in the paper). If ANY of
       (b)/(c) is uncertain — concurrent/post-dating per the dates, no code, niche
       benchmark, NO_PROFILE, the paper justifies the omission — DO NOT flag: set
       verdict_local "needs_external_check", requires_external_check true, severity
       "info", false_positive_risk "high", and name what a human should verify.
    5. HONEST FP. Concurrency/post-dating, unavailability, and a stated justification
       are the common false positives here — say so. If the expected set is empty/
       inconclusive, do NOT manufacture a missing baseline.
    6. pattern_id MUST be HP-MISSING-BASELINE.

    SEVERITY DECISION (HP-MISSING-BASELINE):
      - unambiguous, sourced, same-benchmark, clearly PRE-DATING omission AND the
        paper's HEADLINE is the SOTA/best claim -> "critical", FP "low",
        requires_external_check false.
      - clearly relevant + likely prior but contestable, OR a skipped strong FLOOR
        (BM25/GBDT/linear) while only weak baselines are beaten -> "major", FP
        "medium", requires_external_check true.
      - uncertain / NO_PROFILE / cannot confirm recency or relevance -> "info",
        verdict_local "needs_external_check", requires_external_check true.

    OUTPUT: a single JSON array and NOTHING ELSE (no prose, no code fence). Each
    element conforms to schemas/finding.schema.json:
      {"finding_id":"BC001","skill":"baseline-comparison-audit",
       "pattern_id":"HP-MISSING-BASELINE","title":"short, neutral",
       "description":"which expected baseline is absent + the SOTA claim it undermines + the source",
       "severity":"critical|major|minor|info","observability_level_required":0,
       "evidence":[{"claim_id":"C0xx","span":"verbatim substring",
                    "location":{"file":"...","section":"..."}}],
       "verdict_local":"fail|warn|clean|needs_external_check",
       "requires_external_check":true|false,"false_positive_risk":"low|medium|high",
       "recommended_reviewer_action":"what to CHECK or ASK — never 'reject'"}
    An empty array [] is a valid, honest result (the expected baselines are all present).
```

## Step 4 — fairness + significance + cross-row delta prompt

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are a baseline-FAIRNESS-and-SIGNIFICANCE forensics reviewer. For each head-
    to-head comparison the paper draws ("we outperform / are better than / achieve X
    vs baseline Y"), check whether it is FAIR (matched budget/tuning/config),
    SIGNIFICANT (the gap exceeds reported noise), and whether the stated cross-row
    improvement matches its operands. PROPOSE findings only — do NOT grade the paper;
    describe a discrepancy to CHECK, never an accusation. You do NOT judge whether the
    numbers are real (that needs the code) — only what the paper's OWN comparison shows.

    INPUTS (read directly in your working directory):
      - claims.json — comparison LANGUAGE in type:"comparison" / type:"scope"; the
        baseline set in type:"baseline"; values + table rows in type:"number" /
        type:"table_cell"; labels in type:"caption". The ONLY structure you navigate
        by; each claim = {claim_id, type, text_span (VERBATIM), location, value?}. You
        MAY re-open a source file (and, at L2, the config/result files) to confirm a span.
    RUN OBSERVABILITY LEVEL L = <L from Step 0>.
    HEAD-TO-HEAD comparison claims (anchor targets — claim_id + verbatim text_span):
      [paste the comparison/scope anchor claims + the relevant number/table_cell claims]
    REPORTED VARIANCE / SEEDS (if any, with claim_id):
      [paste any "+/-", "std", "over N seeds", "n=" spans, or write "NONE REPORTED"]
    L2 CONFIG FACTS (raw grep/hash hits + config paths — uninterpreted; empty if L<2):
      [paste the grep/find/shasum output above, or "L<2: no repo/configs available"]

    HARD RULES:
    1. ANCHOR every finding above "info" to a real claim_id + a VERBATIM substring of
       that claim. Anchor to the comparison claim (and the row's number/table_cell as
       extra evidence). A config file:line is forensic detail for the description —
       NOT a valid anchor. No verbatim span ⇒ keep at "info".
    2. DISCREPANCY, NOT ACCUSATION. Say what to CHECK/ASK. Never "reject"/"faked".
    3. OBSERVABILITY — set observability_level_required to the LOWEST tier at which the
       discrepancy is DECIDABLE: 0 when the asymmetry/variance/delta is VISIBLE IN THE
       PAPER TEXT/TABLES (e.g. "we train ours 300 epochs" vs a cited 90-epoch baseline
       number); 2 when CONFIRMING it needs the repo's config/result files (it auto-
       demotes on an L0/L1 run — that is correct, not a loss).
    4. HONEST FP. A documented identical budget, standard reference numbers cited from
       a baseline's own paper, a large gap, a reported significance test, and
       genuinely deterministic metrics are COMMON false positives — say so.
    5. pattern_id MUST be one of: HP-WEAK-BASELINE, HP-SIG-OVERLAP, HP-DELTA-ERROR,
       HP-RESOURCE-IDENTITY-MISMATCH.

    CHECKLIST (one finding per concrete discrepancy):
     1. FAIRNESS / WEAK BASELINE [HP-WEAK-BASELINE] — the proposed method gets more
        compute / tuning / data, or runs at more favorable settings, than the baseline;
        the compared rows use non-matching configs (backbone / data / split /
        decoding); a baseline is left at defaults while the method is tuned; a baseline
        number is copied from an old paper at a different budget. The strongest single
        check: is the method's OWN backbone-without-the-new-component (the ablation-as-
        baseline) reported at an IDENTICAL budget? severity major. observability 0 if
        the asymmetry is STATED in text; 2 if only the configs reveal it. FP: identical
        budget documented; a standard reference number quoted from the baseline's own
        paper (citing a published number is legitimate — note any config delta, do not
        allege).
     2. SIGNIFICANCE / OVERLAP [HP-SIG-OVERLAP] — "outperforms / better / consistently"
        claimed where reported error bars OVERLAP, or where NO variance / seed count is
        reported for a SMALL gap (within the field's typical noise for this metric).
        severity: major if error bars are reported AND overlap; minor if merely absent
        variance for a small gap (rise to major only if the headline rests on it).
        observability 0. FP (high → say so): a large gap; a significance test reported;
        a genuinely deterministic metric (exact match on a fixed test set). Two further
        thin-evidence signals — each a recurring real-review tell — to flag EXPLICITLY
        (SAME pattern_id HP-SIG-OVERLAP, SAME anchor = the comparison/SOTA claim):
        (a) NO VARIANCE / SEEDS REPORTED — the comparison rests on bare point estimates
            with NO ±/std/CI and NO seed/run count reported AT ALL (one number per cell,
            no "over N seeds"), so the gap cannot be told from run-to-run noise. severity
            minor for a small gap; major when the headline rests on it OR the profile's
            "Variance norm" column expects >=N seeds for this domain (e.g. RL >=5 seeds,
            retrieval per-query CI) and none are reported. observability 0. FP (high →
            say so): a large clearly-separated gap; a reported significance test; a
            genuinely deterministic / single-pass metric where seeds are moot.
        (b) SINGLE-DATASET-ONLY — a "consistently / robustly / across-the-board /
            general" comparison claim that rests on ONE dataset/benchmark (or a single
            split/domain), too thin for the breadth the wording asserts. severity minor;
            major only when that breadth IS the headline. observability 0. FP (high →
            say so): the claim is explicitly SCOPED to that one benchmark ("on GSM8K we
            …"); the dataset is the field-standard SOLE benchmark for the task; or broad
            scope genuinely exists elsewhere in the paper. LANE: this fires ONLY when
            anchored to a comparison/SOTA claim — generic scope-language inflation with
            NO comparison claim ("a comprehensive study") is consistency-audit's
            HP-SCOPE-INFLATE, not this; do NOT double-emit.
     3. CROSS-ROW DELTA ARITHMETIC [HP-DELTA-ERROR] — recompute a stated "improves over
        <baseline> by X%" as (proposed-baseline)/baseline AND absolute points; flag if
        X disagrees beyond rounding, or relative/absolute are conflated to inflate.
        severity major; critical if the corrected delta deflates a "large/significant"
        framing. observability 0. FP: abs-vs-rel stated explicitly; rounding. DELTA
        SCOPE (critical to avoid double-counting): flag ONLY when the two operands are
        a BASELINE row value and the PROPOSED row value living in DIFFERENT
        sentences/cells — the cross-row case a single-sentence regex cannot pair. Do
        NOT re-flag a delta whose operands AND stated value sit in ONE sentence — the
        deterministic consistency pass already owns those.
     4. RESOURCE IDENTITY [HP-RESOURCE-IDENTITY-MISMATCH] — a named dataset / benchmark /
        model is described with a checkable PUBLIC-RECORD property its registry contradicts
        (ImageNet-1k stated with the wrong #classes/size; a model's parameter count off from
        its card; a "SOTA 91.2 on <benchmark>" disagreeing with that benchmark's public
        leaderboard). RESOLVE each named resource against its HuggingFace dataset/model card
        or Papers-with-Code record (WebFetch/WebSearch — FACTS only; put the URL + access
        date in `description`); the reviewer judges the discrepancy. Anchor to the paper
        claim NAMING the resource (never the registry URL). severity major; critical if the
        mis-described resource IS the headline (the SOTA number that is the contribution).
        observability 0 (public-record contradiction) / 2 (the repo loads a different
        resource than named). FP (→ needs_external_check, never a guessed "wrong"): a
        declared subset/variant (ImageNet-100, a 10% split, a distilled/quantized model); a
        version difference (-21k vs -1k, v1 vs v2); an explicit redefinition; a stale /
        ambiguous registry or a leaderboard updated after submission. LANE: method
        described ≠ method evaluated is HP-METHOD-DRIFT (consistency-audit); a fabricated
        citation identity is HP-CITE-HALLUC — this is the named RESOURCE's identity vs its
        public record.

    OUTPUT: a single JSON array and NOTHING ELSE (schemas/finding.schema.json), same
    shape as the completeness prompt; set finding_id "BC0xx",
    skill "baseline-comparison-audit". An empty array [] is valid and honest. Set
    requires_external_check only when you genuinely cannot settle a point at this level.
```
