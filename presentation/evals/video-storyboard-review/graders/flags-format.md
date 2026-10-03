---
type: regex
pattern: '1920|1080p?|60\s*fps|60\s*帧'
flags: i
match: contains
target: last_message
---

The review moves the output from 1280x720 at 30 fps to 1920x1080 at 60 fps.
