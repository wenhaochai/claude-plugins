---
description: Add a leaderboard slide from a CSV with published intervals; the author's rules ask for the top five with the interval, a title naming it, the read date in the source line and a paired EN/ZH script.
tags: [talk-slides]
max_turns: 15
timeout_seconds: 540
allowed_tools: [Read, Glob, Grep, Skill, Bash, Edit, Write]
---

Add a leaderboard slide to my group-meeting deck in deck/ (claude.ai Slides project folder). The data is in data/agent_arena_leaderboard.csv. Write it to deck/project/slides/leaderboard.html, put it right after the cover (update the order in deck.json too), and write the speaker notes, 讲稿我会照着念. No need to publish.
