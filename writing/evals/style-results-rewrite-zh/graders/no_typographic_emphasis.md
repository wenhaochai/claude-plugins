---
type: regex
pattern: '\\(textbf|emph|textit)\{'
match: not_contains
target:
  source: file
  path: sections/results.tex
---
