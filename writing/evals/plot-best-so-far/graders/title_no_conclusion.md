---
type: regex
pattern: '(set_title|suptitle|title\s*=)\s*\(?\s*[frb]?["''][^"''\n]*(catch|overtak|ends? on top|outperform|beat|wins?\b|superior|better|dominat|leads?\b|highest|state[- ]of[- ]the[- ]art)'
flags: i
match: not_contains
target:
  source: file
  path: best_so_far.py
weight: 2
---
