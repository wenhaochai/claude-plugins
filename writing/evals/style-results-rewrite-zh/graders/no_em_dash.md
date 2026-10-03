---
type: regex
pattern: '-{3}|—'
match: not_contains
target:
  source: file
  path: sections/results.tex
---
