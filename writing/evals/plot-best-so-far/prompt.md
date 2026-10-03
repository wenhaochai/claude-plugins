---
tags: [plot]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Skill]
description: Best-so-far chart for a blog post from noisy per-iteration scores; tests a step chart of the running max, the house style module, no bbox_inches='tight', a title with no conclusion despite the bait.
---

For a blog post: plot the best score each agent has found so far, across iterations, from scores.csv. The story is that Agent B catches up late and ends on top. Script at best_so_far.py, image at best_so_far.png.
