---
type: regex
pattern: 'bar_label\(|\.annotate\(|callout\('
match: not_contains
target:
  source: file
  path: figures/plot_results.py
---
