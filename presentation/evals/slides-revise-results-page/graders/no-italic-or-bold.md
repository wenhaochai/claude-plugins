---
type: regex
pattern: 'font-style:\s*italic|font-weight:\s*(?:700|800|900|bold)'
match: not_contains
target: {source: file, path: deck/project/slides/results.html}
---

Nothing italic and no bold weights; the fixture title is serif 700 and the caption is italic.
