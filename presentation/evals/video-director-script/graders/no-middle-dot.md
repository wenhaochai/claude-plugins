---
type: regex
pattern: '·|\\u00b7|&middot;'
flags: i
match: not_contains
target: {source: file, path: video/director.js}
---

No middle dot (U+00B7) in the video copy; the page's kicker, byline and title tag all carry one.
