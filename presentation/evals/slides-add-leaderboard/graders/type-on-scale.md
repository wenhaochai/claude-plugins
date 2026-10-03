---
type: regex
pattern: 'font-size:\s*(?!(?:24|28|36|56|120)px)\d+(?:\.\d+)?px'
match: not_contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

Every font size is on the author's scale (sans 24/28/36, serif 56/120).
