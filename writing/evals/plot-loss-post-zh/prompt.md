---
tags: [plot]
max_turns: 15
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Bash, Write, Edit, Skill]
description: Chinese request for a loss-vs-compute chart to post on X; tests the house style module, the post canvas width (not a paper width or 16:9), a log compute axis, no bbox_inches='tight', the PNG written.
---

帮我把 runs.csv 里三个模型大小的 loss 随 compute 变化的曲线画成一张图，我要发推特用。脚本写到 plot_loss.py，图存成 loss.png。
