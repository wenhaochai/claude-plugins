---
type: regex
pattern: 'lint\.py\s+(?:\S*deck|\.(?:\s|$|"))'
match: contains
target: trace
---

The agent ran the bundled static lint on the deck (a lint.py command with the deck path; the skill text itself says DECK_DIR, which does not match).
