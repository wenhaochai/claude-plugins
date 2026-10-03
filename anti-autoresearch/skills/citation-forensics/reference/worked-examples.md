# Worked examples (Step 3 reference output)

**Reference output — what good findings look like** (the shape the validator keeps):

```json
// HP-CITE-CONTEXT (major) — the dangerous case: real paper, wrong claim
{
  "finding_id": "F001", "skill": "citation-forensics", "pattern_id": "HP-CITE-CONTEXT",
  "title": "Self-refinement work cited for the opposite of what it shows",
  "description": "The sentence cites \\cite{madaan2023selfrefine} to support that self-feedback yields correlated errors. The cited paper (Self-Refine, NeurIPS 2023; DBLP https://dblp.org/... confirms title/venue/authors; abstract in resolution.json) demonstrates that iterative self-feedback IMPROVES outputs — it does not establish correlated self-feedback errors. The citation supports a claim the cited work does not make.",
  "severity": "major", "observability_level_required": 0,
  "evidence": [{"claim_id": "C042", "span": "\\cite{madaan2023selfrefine}",
                "location": {"file": "sections/2.overview.tex", "section": "method"}}],
  "verdict_local": "fail", "false_positive_risk": "medium",
  "recommended_reviewer_action": "Re-read Self-Refine §1; ask which result supports 'correlated errors', or re-attribute the claim to a paper that establishes it."
}
// HP-CITE-HALLUC (critical) — no canonical record resolves
{
  "finding_id": "F002", "skill": "citation-forensics", "pattern_id": "HP-CITE-HALLUC",
  "title": "No paper resolves at the claimed arXiv id / title",
  "description": "\\cite{kim2024neuralcompress} claims arXiv:2407.99999 with authors {Kim, Park}. resolution.json: arXiv:2407.99999 does not resolve; DBLP fuzzy+boolean return no paper with this title and author set. The reference appears to have no canonical record.",
  "severity": "critical", "observability_level_required": 0,
  "evidence": [{"claim_id": "C051", "span": "\\cite{kim2024neuralcompress}",
                "location": {"file": "sections/6.related.tex", "section": "related"}}],
  "verdict_local": "fail", "false_positive_risk": "low",
  "recommended_reviewer_action": "Ask the authors for a resolvable arXiv id / DOI; verify it exists before relying on the surrounding claim."
}
```
> Contrast (NOT critical): a typo'd-but-resolvable id (`2407.9999` → real `2407.09999`)
> is a **FIX** → `severity: minor`/`info`, `false_positive_risk: low`,
> `recommended_reviewer_action: "correct the arXiv id"`. A preprint→venue migration
> (arXiv 2023 → CVPR 2024) is metadata drift at most (`major` only if the wrong record
> is load-bearing), never `critical`.
