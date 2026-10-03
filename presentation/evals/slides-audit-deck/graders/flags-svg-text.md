---
type: regex
pattern: 'svg[^\n]{0,120}text|text[^\n]{0,120}svg'
flags: i
match: contains
target: last_message
---

The report flags the <text> labels inside the method slide's SVG (fonts never load in an SVG; labels go in <p> over it).
