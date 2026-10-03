---
type: regex
pattern: '\[click\]|click (?:mark|build)|builds?\b[^\n]{0,80}(?:click|mark)'
flags: i
match: contains
target: last_message
---

The report brings up the [click] marks against the slide's click builds (two builds, one mark).
