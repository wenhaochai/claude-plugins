---
type: regex
pattern: '>(?=[^<]*Arena)(?=[^<]*(?:2026-10-01|1 Oct(?:ober)?,? 2026|Oct(?:ober)? 1,? 2026|2026年10月1日))[^<]*<'
match: contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

One text element, the source line, names the arena and the read date together.
