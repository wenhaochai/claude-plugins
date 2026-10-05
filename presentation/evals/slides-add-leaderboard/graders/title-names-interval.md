---
type: regex
pattern: '<h2[^>]*>[^<]*(?:interval|\bCI\b|95\s*%|置信区间)'
flags: i
match: contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

The leaderboard title names the interval the source publishes.
