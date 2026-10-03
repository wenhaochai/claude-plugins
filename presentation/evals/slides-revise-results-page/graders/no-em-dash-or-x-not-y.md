---
type: regex
pattern: '—|, not '
match: not_contains
target: {source: file, path: deck/project/slides/results.html}
---

No em dash and no "X, not Y" wording left in the slide or its notes.
