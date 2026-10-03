---
type: regex
pattern: '2026-10-01|1 Oct(?:ober)?,? 2026|Oct(?:ober)? 1,? 2026|2026年10月1日'
flags: i
match: contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

The source line carries the date the leaderboard was read (the export date in the CSV).
