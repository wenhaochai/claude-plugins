---
type: regex
pattern: '^(?=[\s\S]*(from style import|import style\b))(?=[\s\S]*\bcanvas\()(?=[\s\S]*\bsave\()'
match: contains
target:
  source: file
  path: plot_loss.py
weight: 2
---
