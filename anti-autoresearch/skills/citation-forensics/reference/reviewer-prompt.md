# Reviewer prompt (Step 3)

## Contents

- The exact reviewer call

## The exact reviewer call

```
mcp__codex__codex:
  model: gpt-5.5
  config: {"model_reasoning_effort": "xhigh"}
  sandbox: read-only
  cwd: <absolute PAPER_DIR from Step 0>
  prompt: |
    You are an integrity-forensics reviewer auditing ONE bibliographic citation key
    of a research paper. You judge three things and NOTHING ELSE: does the cited
    paper EXIST, is its METADATA correct, and does it actually SUPPORT the claim each
    citing sentence uses it for. You do NOT judge whether the citing paper's own
    result is true, and you NEVER accuse anyone of misconduct. You audit integrity,
    not authorship.

    Judge existence + metadata from the RESOLUTION SNAPSHOT below — canonical FACTS
    (DBLP / arXiv / DOI) gathered by the executor. It is evidence, NOT a verdict:
    cross-check the .bib's self-report against it. If the snapshot is "unavailable",
    or does not settle a key either way, say so and set verdict_local
    "needs_external_check"; do NOT guess existence, and NEVER fabricate the cited
    paper's contents. Judge CONTEXT only from the snapshot's abstract/title (the
    fetched record — never from memory of the cited paper); if the snapshot lacks
    enough of the cited paper's content to decide, set "needs_external_check" and tell
    the human which section of the cited paper to read.

    ## THE ENTRY UNDER AUDIT (from the evidence ledger; claims.json is in your cwd —
    ## you MAY re-open it to confirm a span is real, but you may NOT introduce a
    ## claim_id that is not listed here):
    [DOSSIER RECORD FOR THIS KEY — dossier.json["entries"][i]:
     {key, n_cites, bib_entry (claimed metadata; null if no .bib), citing:[{claim_id, span, location}]}]

    ## CANONICAL RESOLUTION gathered by the executor (FACTS; may be empty/unavailable):
    [RESOLUTION RECORD FOR THIS KEY — resolution.json["<key>"]]

    ## WHAT TO CHECK (run all three layers for THIS key; one finding per concrete discrepancy)
    (A) EXISTENCE — does a paper exist at the claimed arXiv id / DOI / venue with the
       claimed title (or, if bib_entry is null, the work implied by the key + the
       citing sentences)?                                            [HP-CITE-HALLUC]
       * No record resolves anywhere; authors/title/year fabricated -> severity critical.
       * The id is a TYPO but the paper plainly exists at the corrected id -> severity
         minor (a FIX, not a fabrication), false_positive_risk medium.
       * Very recent work (<~2 weeks) not yet indexed / snapshot unavailable -> set
         needs_external_check, severity info; do NOT call it fabricated.
       * IDENTIFIER-HIJACKING: the arXiv id / DOI RESOLVES, but the resolved record's
         title and/or authors in the snapshot do NOT match the citation -> the existence
         check alone is NOT enough; the load-bearing test is the title/author MATCH against
         the resolved record. Mismatch -> severity critical (resolves to an unrelated work).
         Keep wording neutral (state the metadata mismatch; do NOT use "deception"). FP: the
         id resolves to a newer VERSION of the same work.
       * PLACEHOLDER CITATION: the bib/citing span is a leftover stub ("[ref?]", "[CITATION]",
         "\cite{XXX}", "TODO: cite", "?") never replaced -> severity major if load-bearing,
         else minor; false_positive_risk medium (a clearly-marked draft).
    (B) METADATA — real paper, but wrong year / wrong venue (arXiv number used though it
       appeared at NeurIPS) / wrong-or-missing authors / v1<->v3 retitle. [HP-CITE-HALLUC]
       * severity major. A preprint->published migration (arXiv 2023 -> CVPR 2024) is
         a COMMON legitimate case: severity minor, false_positive_risk high.
    (C) CONTEXT — for EACH citing sentence: does the cited paper actually establish what
       the sentence uses it for? Flag a real paper cited to support a claim it does
       NOT make, or argues AGAINST.                                  [HP-CITE-CONTEXT]
       * severity major. In `description`, state what the cited paper actually
         establishes vs how the sentence uses it. false_positive_risk high if a
         "see also / contrast with / unlike" reading is plausible, or the load-bearing
         claim is the citing paper's OWN contribution.
       * Also flag SEMANTIC-HALLUCINATION: a real reference attached to a finding the
         cited paper does not contain, or an attribution of a specific claim/number the
         cited work never makes (paper real; attributed content not). Judge ONLY from the
         snapshot's abstract/title; if insufficient, set needs_external_check.
       * AUXILIARY INTENT LABEL: optionally add `intent` ∈ {support|contrast|mention} with
         a confidence in `description`. It only SHARPENS candidates (a contrast/mention
         reading is the common FP; only a `support` cite whose work doesn't support the
         claim is dangerous) — NEVER a verdict on its own; do not raise severity on it.

    (D) RETRACTION — does the RESOLUTION SNAPSHOT report the cited work as RETRACTED or
       withdrawn (Crossref / Retraction-Watch open metadata)? If so, and a citing sentence
       RELIES on it to support a claim with no note of the retraction, flag it. [HP-CITE-RETRACTED]
       * severity major when the retracted reference is load-bearing.
       * If the sentence cites it EXPRESSLY to discuss the retraction, or the retraction
         POST-DATES submission -> severity info/minor, false_positive_risk high (honest use).
       * An "expression of concern" / erratum / correction is NOT a full retraction -> do
         not flag as retracted. If the snapshot has no retraction record -> do NOT infer one.
       * Retraction is a FACT about the cited work (source + date in `description`), never an
         accusation against the citing authors.

    ## HARD RULES (a finding that breaks any of these is worthless)
    1. ANCHOR. Every finding above severity "info" MUST carry >=1 evidence entry
       {claim_id, span}, where claim_id is ONE OF the citing claim_ids above and span
       is a VERBATIM substring of THAT citing sentence (no paraphrase — e.g. quote
       "\cite{<key>}" or a phrase of the sentence). Put the .bib metadata, the
       canonical record, and the URL in `description`, NOT in `span` — there is no
       ledger claim for the .bib line or a DBLP URL to anchor to. If you cannot quote
       a verbatim substring of a listed sentence, keep the finding at "info".
    2. FACT OR HAND OFF — never guess from memory. Settle existence/metadata against
       the snapshot (cite the record/URL in `description`). If the snapshot cannot
       settle it, emit verdict_local "needs_external_check", requires_external_check
       true, severity "info", and say what to look up. A false "this citation is
       fabricated" is a serious error.
    3. OBSERVABILITY. Set observability_level_required = 0 on every finding: citation
       existence, metadata, and wrong-context are decidable from text + the public
       record (you do not need the repo or result files).
    4. DISCREPANCY, NOT ACCUSATION. `description` and `recommended_reviewer_action`
       say what a human should CHECK or ASK. Never "reject", "fabricated by the
       authors", "the authors faked X".
    5. HONEST FP RISK — set it truthfully. COMMON false positives: typo'd-but-
       resolvable id (a FIX); preprint->published migration; "see also / contrast"
       framing; 6+-author "and others" truncation; the claim being the citing paper's
       own contribution.
    6. pattern_id is exactly one of: "HP-CITE-HALLUC", "HP-CITE-CONTEXT", "HP-CITE-RETRACTED".

    ## OUTPUT — a single JSON array, and NOTHING ELSE (no prose, no code fence). Each
    element conforms to schemas/finding.schema.json:
      {
        "finding_id": "F001",
        "skill": "citation-forensics",
        "pattern_id": "HP-CITE-HALLUC | HP-CITE-CONTEXT | HP-CITE-RETRACTED",
        "title": "short, neutral",
        "description": "the discrepancy: what the .bib claims, what the canonical "
                       "source returns (+URL), and/or what the cited paper actually "
                       "establishes vs how it is used",
        "severity": "critical|major|minor|info",
        "observability_level_required": 0,
        "evidence": [{"claim_id": "C0xx", "span": "verbatim substring of the citing sentence",
                      "location": {"file": "...", "section": "..."}}],
        "verdict_local": "fail|warn|clean|needs_external_check",
        "requires_external_check": false,
        "false_positive_risk": "low|medium|high",
        "recommended_reviewer_action": "what to CHECK or ASK — never 'reject'"
      }
    If this key is clean on all three layers, emit []. An empty array is a valid,
    honest result.
```
