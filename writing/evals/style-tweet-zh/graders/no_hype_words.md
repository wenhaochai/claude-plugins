---
# A word quoted in a note about what the tweet avoids ("significantly") is a mention, not a use, so a quote mark before it is exempt.
type: regex
pattern: '(?<!["“‘])(?:revolution|game[- ]?chang|groundbreaking|unprecedented|breakthrough|\bdelve|state[- ]of[- ]the[- ]art|\bSOTA\b|dramatic|massive|\bhuge\b|significant(ly)?\b|\bthrilled\b|\bcrush)'
flags: i
match: not_contains
target: last_message
---
