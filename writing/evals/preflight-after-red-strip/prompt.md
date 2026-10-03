---
tags: [preflight]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Bash, Skill]
description: User believes the camera-ready is clean after stripping red marks; tests that the check finds the red mark left in an \input'd appendix file and the >5pt overfull box in the build log.
---

I just stripped all the red review marks from our ICML camera-ready in cr/. Quick sanity check before I send it to the co-authors? No TeX on this box; cr/main.log is from the Overleaf build of this exact version.
