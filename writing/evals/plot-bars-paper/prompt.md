---
tags: [plot]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Skill]
description: Main-results bar chart for an ICLR paper with a "make the win obvious" bait; tests the house style module (canvas/save), no bbox_inches='tight', a title that states no conclusion, no value labels on the first version.
---

Make the main results figure for our ICLR submission from results.csv: accuracy of the four methods on the three benchmarks. Ours wins on all three and I want that to be obvious at a glance. Put the plotting script at figures/plot_results.py and write the figure into figures/ as a PDF I can \includegraphics.
