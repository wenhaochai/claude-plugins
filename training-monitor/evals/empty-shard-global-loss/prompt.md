---
description: Dashboard global loss is a mean of per-rank means that records an empty rank as 0 (fake dip at steps 30-34) and hides one bad rank from step 25. Tests the sum-then-divide reduction, skip-empty-ranks rule, and worst-rank loss.
tags: [training-monitor]
max_turns: 12
timeout_seconds: 420
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---
8 卡数据并行的预训练。dashboard 上的 global loss（当前目录的 dashboard_loss.csv）在 step 30–34 突然掉下去一大截又弹回来，step 25 左右还往上跳了一下。每个 rank 自己记的 loss 在 rank_loss.csv 里：loss_mean 是这个 rank 当步的平均 loss，n_valid_tokens 是当步的有效 token 数。

step 30 那几步是模型真的变好了吗？step 32 真实的 global loss 应该是多少？这个 run 到底哪里有问题？
