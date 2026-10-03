---
tags: [preflight]
max_turns: 10
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Bash, Skill]
description: Chinese pre-submission check on a NeurIPS draft whose TODOs are all commented-out or macro-definition decoys; tests the real findings (red mark, respectively density, bib warnings) without false TODO alarms.
---

draft/ 是我们要投 NeurIPS 的稿子，投稿前帮我检查一下还有什么没清理干净的、能不能交。这台机器上没装 TeX，Overleaf 上编译是过的。
