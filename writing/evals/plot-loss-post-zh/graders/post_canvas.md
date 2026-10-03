---
type: regex
pattern: 'WIDTH_POST|card\s*=\s*True'
match: contains
target:
  source: file
  path: plot_loss.py
weight: 2
---
