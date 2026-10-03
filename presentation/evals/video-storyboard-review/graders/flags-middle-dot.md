---
type: regex
pattern: 'middle dot|U\+00B7|间隔号|中间点|中点|居中点|圆点|"·"|`·`|“·”'
flags: i
match: contains
target: last_message
---

The review flags the middle dot in the kicker, the author line and the closing line.
