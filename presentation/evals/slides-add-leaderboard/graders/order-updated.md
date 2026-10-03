---
type: regex
pattern: '"order"\s*:\s*\[\s*"cover"\s*,\s*"leaderboard"'
match: contains
target: {source: file, path: deck/project/deck.json}
---

deck.json lists the new slide right after the cover.
