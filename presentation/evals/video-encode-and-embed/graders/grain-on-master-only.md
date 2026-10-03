---
type: regex
pattern: 'noise=alls'
match: count:1
target: {source: file, path: encode.sh}
---

Light grain (ffmpeg noise filter) is added once, on the master; the web copies drop it.
