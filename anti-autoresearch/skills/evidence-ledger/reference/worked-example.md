# Evidence Ledger — Step 2 worked example

**Worked example** (clean fixture `eval/fixtures/clean/sample_paper.tex` as `main.tex`)
— the stdout above, then two real claims (`location.file` mirrors the path you pass to
`--latex`):

```json
{ "claim_id": "C001", "type": "table_cell",
  "text_span": "Baseline \\cite{smith2024bar} & 73.1 \\\\",
  "location": {"file": "main.tex", "line": 36, "section": "table:1"},
  "value": {"raw":"73.1","normalized":73.1,"unit":null,"metric":null,"direction":"unknown","aggregation":"unspecified"},
  "evidence_anchor": "e6186efa…0460", "extractor": "table_parser", "confidence": "medium" }

{ "claim_id": "C003", "type": "number",
  "text_span": "FooNet reaches 78.0\\% accuracy, improving from a 73.1\\% baseline to 78.0\\% accuracy, a 6.7\\% relative improvement.",
  "location": {"file": "main.tex", "line": 9, "section": "abstract"},
  "value": {"raw":"78.0","normalized":78.0,"unit":"%","metric":"accuracy","direction":"unknown","aggregation":"unspecified"},
  "evidence_anchor": "e6186efa…0460", "extractor": "latex_regex", "confidence": "high" }
```

> **The ledger states, it does not judge.** Run the extractor on the *corrupted*
> `eval/fixtures/synthetic_corruptions/delta_inflate.tex` (abstract says "16.7%
> relative improvement") and you get an **identical 13-claim shape** — only C003's
> verbatim text changes. Spotting that 16.7% contradicts 73.1→78.0 is
> **consistency-audit**'s job (HP-DELTA-ERROR), not the ledger's; the ledger just
> captures the span faithfully.
