---
type: regex
pattern: '<h2[^>]*>(?:[^<]*\b(?:wins?|beats?|leads?|outperforms?|dominates?|crush(?:es)?|better|best|improves?|helps?|matters?|works?)\b|[^<,]*,[^<,]*,)'
flags: i
match: not_contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

The title is a noun label and makes no claim: no verdict verb such as wins, beats or leads, no "better" or "best", and no comma-joined list of clipped phrases.
