# Presentation Signals — why this exists

## Why this exists

Real reviewers notice surface tells before they read a single number — and they say
so out loud: *"两张表一模一样"* (two tables are identical), *"图还是大模型生成的"*
(the figure is LLM-generated), *"就这还没写满9页"* (couldn't even fill 9 pages),
*"堆砌名词吗"* (just stuffing jargon?), *"本文不是什么什么，而是什么什么…论文应该直接表达
做了什么"* (stop hedging "this paper is not X but rather Y" — just say what you did),
*"摘要写的像实验分析,读不到引言"* (the abstract reads like an experiment log; the
introduction is unreadable). An autoresearch pipeline (or a rushed human) produces
exactly these artifacts: a table copy-pasted and never updated, an oversized float to
pad the page limit, a decorative generated illustration in place of a real results
plot, paragraphs of generic LLM boilerplate, draft text so densely over-hedged that
every sentence defends against an objection, and an abstract that dumps experiment
notes instead of telling a background → contribution → evidence story.

These signals are **real** in the sense that reviewers react to them — but they are
**weak evidence of misconduct**. A concise honest paper has few floats; a careful
honest author uses LLM assistance for prose; a legitimate teaser figure can look
"generated". So this skill's contract is narrow and permanent:

- it emits only the five §F surface patterns, all **capped at `minor`**;
- it defaults every *semantic* finding to `false_positive_risk: high` (the deterministic
  `HP-DUP-TABLE` / `HP-PIPELINE-ARTIFACT` checks set their own — the latter is low-FP);
- it **never** says a paper is "AI-generated" or implies fabrication;
- **silence is the common, correct output** — most papers should produce few or zero
  surface findings.

It exists to add *context* to the substantive auditors (`consistency-audit`,
`experiment-forensics`, `baseline-comparison-audit`, `citation-forensics`), not to
stand alone. If a surface tell sits next to a real numeric contradiction, the
substantive finding carries the weight; the surface note just says "look closer."
