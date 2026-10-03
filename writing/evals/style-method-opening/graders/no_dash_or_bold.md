---
type: regex
pattern: '-{3}|—|\\textbf\{'
match: not_contains
target:
  source: file
  path: sections/method.tex
---
