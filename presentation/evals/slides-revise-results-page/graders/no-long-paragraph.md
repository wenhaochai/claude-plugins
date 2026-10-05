---
type: regex
pattern: '^(?:(?!<aside>)[\s\S])*?>(?:[^<\s]+[ \t]+){20}[^<\s]+'
match: not_contains
target: {source: file, path: deck/project/slides/results.html}
---

The long paragraph is gone: no visible text run on the slide reaches 21 words.
