# Step 3 — worked findings and non-findings

**Worked finding — `HP-THIN-FLOAT` (anchored → survives as `minor`):**

```json
{
  "finding_id": "F001",
  "skill": "presentation-signals",
  "pattern_id": "HP-THIN-FLOAT",
  "title": "Broad empirical scope claimed with very few floats",
  "description": "The abstract claims a 'comprehensive empirical evaluation across diverse benchmarks', but the paper contains only 2 tables and 1 figure (ledger: 2 table sections, 1 caption claim). This is a surface signal only — a concise paper can be honest; it is NOT evidence the results are weak or fabricated. Route the substantive scope question to baseline-comparison-audit / consistency-audit.",
  "severity": "minor",
  "observability_level_required": 0,
  "evidence": [{"claim_id": "C003",
                "span": "comprehensive empirical evaluation across diverse benchmarks",
                "location": {"file": "paper.txt", "section": "abstract"}}],
  "verdict_local": "warn",
  "false_positive_risk": "high",
  "recommended_reviewer_action": "Glance at whether the float count matches the breadth of the empirical claim; if it feels thin, route the substantive scope check to baseline-comparison-audit / consistency-audit."
}
```

**Worked non-finding — `HP-LLM-FIGURE` (unanchored → held at `info`, the design working):**
the reviewer's impression is that a teaser figure "looks generated", but no caption
claim in the ledger covers that figure (the extractor keeps numbers / scope / captions /
citations, and here the figure carries no extracted caption claim — the PDF could not be
visually inspected). With no verbatim ledger span to anchor to, the validator (and the
adjudicator) hold it at `info` — a note, never a flag. A surface impression that lands
on no extracted claim structurally almost never becomes even a `minor`
flag. **We are not an AI-text classifier.**

**Worked finding — `HP-PAGE-PADDING` (anchored → survives as `minor`):** the reviewer
notes an oversized float plus a repeated block that conspicuously pad toward the page
limit. To rise above `info` the finding must anchor to a ledger claim the padding rests
on (a caption / scope / table-cell span) — an unanchored "this section feels padded"
impression stays `info`. Even with a verbatim anchored span it survives only as
`minor`, `false_positive_risk: high` — context to look closer, never a claim about how
(or by what) the text was produced. The same anchor-or-`info` gate applies to
**`HP-THIN-FLOAT`** and **`HP-LLM-FIGURE`**: anchor to the real scope / caption span and
name the concrete surface fact, or stay `info`. Neither is an authorship verdict — for
AI writing-style impressions use the AIS track (`skills/ai-style-impressions`), and for
authorship detection a dedicated tool.
