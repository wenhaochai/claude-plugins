---
type: regex
pattern: '^\s*<section id="results"[^>]*>(?:(?!<section)[\s\S])*</aside>\s*</section>\s*$'
match: contains
target: {source: file, path: deck/project/slides/results.html}
---

The file is one <section id="results"> with the <aside> as its last child.
