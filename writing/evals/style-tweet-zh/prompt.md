---
tags: [style]
max_turns: 4
timeout_seconds: 180
allowed_tools: [Read, Glob, Grep, Skill]
description: Chinese request for an English launch tweet; tests no prose parentheses such as "(averaged over 3 seeds)" (RULE-13), the rule a baseline breaks here, plus no em-dash, no hype vocabulary, claims sized to a small mixed gain.
---

我们的新论文刚挂 arXiv，帮我写一条英文推特宣传一下。

结果：同样是 7B 模型，我们的方法在 GSM8K / MATH / HumanEval 上分别比 baseline 高 2.1 / 0.4 / 1.3 个点，三个 seed 取平均。链接用 https://arxiv.org/abs/2410.01234 占位。

只给我推文正文就行，不用解释。
