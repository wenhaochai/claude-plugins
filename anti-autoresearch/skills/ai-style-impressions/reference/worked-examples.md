# AI Writing-Style Impressions — worked examples

**Worked impression — `AIS-LLM-PHRASE-TICS` (anchored → kept, but ZERO verdict weight):**

```json
{
  "finding_id": "F001",
  "skill": "ai-style-impressions",
  "pattern_id": "AIS-LLM-PHRASE-TICS",
  "title": "Recurrent 'it is worth noting' / however-therefore phrasing",
  "description": "The cited scope sentence opens with 'It is worth noting that' and the surrounding text repeatedly chains 'however … therefore … moreover' — a common LLM phrasing tic that lowers information density. This is a STYLE IMPRESSION with ZERO verdict weight: not a factual/integrity inconsistency, not evidence of AI authorship, and no probability is implied.",
  "severity": "minor",
  "observability_level_required": 0,
  "evidence": [{"claim_id": "C012",
                "span": "It is worth noting that our method generalizes across settings",
                "location": {"file": "paper.txt", "section": "introduction"}}],
  "verdict_local": "warn",
  "false_positive_risk": "high",
  "not_integrity_finding": true,
  "fp_case": "Honest LLM-assisted drafting, non-native English, and many house styles use exactly these transitions; this is not a tell of AI authorship.",
  "recommended_reviewer_action": "Glance at whether the phrasing tics make the section read padded; an impression only — not misconduct, not an authorship judgment."
}
```

**Worked non-finding — single em-dash (REFUSED, not emitted):** the reviewer is tempted
to flag one em-dash in a sentence. This is on the **refuse-list** (a standalone
single-punctuation tell is never a pattern) — it is **not** emitted, not even as `info`.
A style impression is about a *located, repeated, named* observation; one character is
not one. **We are not an AI-text classifier.**

**Worked routing — `AIS-INVENTED-CODENAME` vs `HP-PHANTOM-RESULT`:** the reviewer sees
"Experiment Set Gamma" in a results table with no definition. If it is merely an
undefined, generation-flavored label, it is an `AIS-INVENTED-CODENAME` impression (zero
weight). But if that codename's row reports a number with **no backing results file**,
that is a substantive integrity problem — **drop the AIS impression and route it** to
`experiment-forensics` (`HP-PHANTOM-RESULT` / `HP-MISSING-REPRO-ARTIFACT`, family D, at
L2). The style track never carries the substantive accusation.
