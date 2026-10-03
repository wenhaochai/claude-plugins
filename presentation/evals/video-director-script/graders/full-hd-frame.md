---
type: regex
pattern: '1920[\s\S]*1080|1080[\s\S]*1920'
match: contains
target: {source: file, path: video/director.js}
---

Frames are drawn at 1920x1080.
