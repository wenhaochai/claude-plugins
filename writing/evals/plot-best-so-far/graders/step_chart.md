---
type: regex
pattern: '\.step\(|drawstyle\s*=\s*["'']steps'
match: contains
target:
  source: file
  path: best_so_far.py
weight: 2
---
