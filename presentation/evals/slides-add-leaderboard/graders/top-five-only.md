---
type: regex
pattern: 'Tamarack|Quillwort|Fennelbrook|Sorrelline'
match: not_contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

The slide shows the top five only; ranks 6 to 9 are left off.
