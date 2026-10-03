---
description: Grad-norm ramp then a loss+grad co-spike at step 212, plus an isolated grad-only spike at 140. Tests co-spike alerting, grad norm as the early signal, and a robust (median/MAD) alert rule.
tags: [training-monitor]
max_turns: 12
timeout_seconds: 420
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---
我在跑一个 1B 的 dense 预训练，梯度裁剪阈值 1.0。最近 260 步的指标我导出到了当前目录的 metrics.csv（每步一行）。帮我看看这个 run 健康吗，出了什么事，要不要停？

另外我想加一个自动报警，免得半夜没人盯着。给我一条具体的报警规则，说清楚算什么量、什么时候触发。
