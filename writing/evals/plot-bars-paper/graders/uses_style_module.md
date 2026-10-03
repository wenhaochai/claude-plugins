---
type: regex
pattern: '^(?=[\s\S]*(from style import|import style\b))(?=[\s\S]*\bcanvas\()(?=[\s\S]*\bsave\()'
match: contains
target:
  source: file
  path: figures/plot_results.py
weight: 2
---
