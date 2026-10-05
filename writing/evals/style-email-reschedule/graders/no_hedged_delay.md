---
# RULE-08 and RULE-03: the notes say the ablations slipped two days, so the email states
# two days. Baselines soften the known number to "about two days behind", which
# understates a fact the writer has and adds a needless word.
type: regex
pattern: '\b(about|around|roughly|approximately|nearly|almost|some)\s+(two|2)\s+days|~\s*2\s*days'
flags: i
match: not_contains
target: last_message
---
