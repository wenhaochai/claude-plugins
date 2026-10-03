---
type: regex
pattern: 'bbox_inches\s*=\s*["'']tight'
match: not_contains
target:
  source: file
  path: figures/plot_results.py
---
