---
tags: [style]
max_turns: 6
timeout_seconds: 300
allowed_tools: [Read, Glob, Grep, Write, Skill]
description: Opening of a NeurIPS method section from notes into a new file; tests no roadmap/overview paragraph, no meta-scaffold opener, no em-dash or bold emphasis.
---

I'm drafting our NeurIPS submission. Please write the start of the method section into sections/method.tex: the \section header and the prose that comes before the first subsection. The intro already pitches the method. My notes:

- method name: TRACE
- setting: a language model solves a problem as a chain of reasoning steps s_1, ..., s_T
- key idea: score each step by how often k = 8 sampled continuations from that step reach the same final answer
- components, one subsection each: 3.1 step scorer, 3.2 budget allocator (spend more samples on low-score steps), 3.3 verifier-free stopping rule
- total sample budget B is fixed per problem

Write LaTeX only for this part; I'll do the subsections myself.
