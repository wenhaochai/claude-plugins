---
type: regex
pattern: 'Orion-3[\s\S]*?1312[\s\S]*?Kestrel-Pro[\s\S]*?1298[\s\S]*?Juniper-XL[\s\S]*?1291[\s\S]*?Basalt-2[\s\S]*?1270[\s\S]*?Marlin-Ultra[\s\S]*?1262'
match: contains
target: {source: file, path: deck/project/slides/leaderboard.html}
---

The top five appear in rank order, each with its score.
