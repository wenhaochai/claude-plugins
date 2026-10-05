---
# RULE-13: no prose parentheses in body text. Baselines tend to write "Friday (Oct 9) at
# 2pm" or "(averaged over 3 seeds)". Markdown link targets and the skill's own activation
# line, which names RULE ranges in parentheses, are exempt.
type: regex
pattern: '(?<!\])\((?!https?:)(?![^()]*RULE)[^()]*[A-Za-z]{2,}[^()]*\)'
match: not_contains
target: last_message
---
