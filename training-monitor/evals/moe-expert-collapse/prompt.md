---
description: Layer 3 router collapses (busiest expert 3x the mean by step 1000, EP shard 0 overloaded) while layers 0-2 stay balanced. Tests MaxVio / imbalance ratio, normalized entropy, and EP shard imbalance.
tags: [training-monitor]
max_turns: 12
timeout_seconds: 420
allowed_tools: [Read, Glob, Grep, Bash, Skill]
---
我们在训一个 MoE，每层 8 个专家、top-2 路由，每步每层 8192 个 token。当前目录的 router_load.csv 是每 100 步记一次的每层每个专家分到的 token 数（e0–e7）。专家并行 EP=2：专家 0–3 在第 0 组卡上，专家 4–7 在第 1 组卡上。

帮我看看负载均衡有没有问题。用一个数说清楚有多严重，再告诉我 dashboard 上该放哪些指标、怎么报警。
