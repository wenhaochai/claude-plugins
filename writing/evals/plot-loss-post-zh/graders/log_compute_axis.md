---
type: regex
pattern: 'set_xscale\(\s*["'']log|loglog\(|xscale\s*=\s*["'']log'
match: contains
target:
  source: file
  path: plot_loss.py
---
