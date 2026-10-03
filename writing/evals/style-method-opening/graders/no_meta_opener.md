---
type: regex
pattern: 'in this section|this section (presents|describes|introduces|details)|we (now )?(present|propose|introduce) TRACE|the rest of this section|is organized as follows'
flags: i
match: not_contains
target:
  source: file
  path: sections/method.tex
weight: 2
---
