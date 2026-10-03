---
type: regex
pattern: '<source[^>]*av01[\s\S]*?<source'
match: contains
target: {source: file, path: site/index.html}
---

The embed lists the AV1 source first, typed with an av01 codecs string, then the H.264 fallback.
