---
type: regex
pattern: 'in this section|moreover|furthermore'
flags: i
match: not_contains
target:
  source: file
  path: sections/results.tex
---
