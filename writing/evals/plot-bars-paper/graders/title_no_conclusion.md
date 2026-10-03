---
type: regex
pattern: '(set_title|suptitle|title\s*=)\s*\(?\s*[frb]?["''][^"''\n]*(outperform|beat|best|wins?\b|superior|better|dominat|leads?\b|highest|state[- ]of[- ]the[- ]art)'
flags: i
match: not_contains
target:
  source: file
  path: figures/plot_results.py
weight: 2
---
