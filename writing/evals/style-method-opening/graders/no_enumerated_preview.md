---
type: regex
pattern: '\((1|i)\)[\s\S]{0,400}\((2|ii)\)|\\begin\{(itemize|enumerate)\}'
match: not_contains
target:
  source: file
  path: sections/method.tex
---
