---
type: regex
pattern: 'font-size:\s*(?!(?:24|26|28|32|52|84|96|104)px)\d+(?:\.\d+)?px'
match: not_contains
target: {source: file, path: deck/project/slides/results.html}
---

Every font size is on the author's scale (Google Sans Text 24/26, Google Sans 24/28/32/52/84/96/104).
