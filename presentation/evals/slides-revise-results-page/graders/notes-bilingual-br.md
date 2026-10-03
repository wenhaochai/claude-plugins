---
type: regex
pattern: '<aside>[\s\S]*<br\s*/?>[\s\S]*[一-鿿][\s\S]*</aside>'
match: contains
target: {source: file, path: deck/project/slides/results.html}
---

The notes are written with <br> line breaks and carry Chinese lines (the English/Chinese script format).
