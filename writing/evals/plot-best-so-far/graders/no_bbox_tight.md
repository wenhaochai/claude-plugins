---
type: regex
pattern: 'bbox_inches\s*=\s*["'']tight'
match: not_contains
target:
  source: file
  path: best_so_far.py
---
