---
type: regex
pattern: 'Date\.now|performance\.now|new Date\('
match: not_contains
target: {source: file, path: video/director.js}
---

The director is deterministic: it reads no wall clock, so frame t is a function of t (the page's own animation uses rAF timestamps).
