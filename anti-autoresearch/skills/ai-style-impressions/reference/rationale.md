# AI Writing-Style Impressions — rationale

## Why this exists

Real reviewers say the quiet part out loud about *style*: *"这一看就是大模型写的味儿"* (this
reads like an LLM wrote it), *"满篇 'it is worth noting' / '值得注意的是'"* (every
paragraph hedges with "it is worth noting"), *"通篇 not only…but also、一堆 however/
therefore"* (chains of however/therefore/moreover), *"堆术语，论证是空的"* (term-stuffing with
no argument under it), *"实验叫 'Experiment Set Gamma'，从没定义"* (an undefined internal
codename used as if defined), *"图都是一个味儿的 AI 生成图"* (the figures share one generated
visual grammar), *"附录像把跑的 trace 一股脑倒进去"* (the appendix reads like a dumped run
trace). An autoresearch pipeline (or a rushed human leaning on an assistant) produces
exactly these *style* artifacts.

These signals are **real** in the sense that reviewers react to them — but they are
**not evidence of misconduct, and not evidence of authorship.** Honest LLM-assisted
writing produces phrase tics; non-native English produces awkward transitions; a house
style produces bold module names and consistent figures; a careful author hedges in the
Limitations. So this skill's contract is narrow and permanent:

- it emits **only** the 13 `AIS-*` style patterns, each as an **impression**;
- it tags **every** finding `not_integrity_finding: true` + `false_positive_risk: high`
  and attaches an `fp_case` (the legitimate, not-necessarily-AI explanation);
- it **never** says a paper is "AI-generated", never assigns a probability or a score,
  and **never** moves the verdict;
- **silence is the common, correct output** — most papers should produce few or zero
  AIS impressions.

It exists so a reviewer's *style* reactions become **named, located, checkable
impressions** instead of an unfalsifiable "vibe" — and so that whenever a style tell is
actually a **substantive** problem, this skill **hands it to the right integrity
auditor** rather than smuggling it in under a style label.

## Step 3 gate scope

Scope of this gate: **AIS allow-list + anchoring + AIS field-forcing** (it does **not**
run `schemas/finding.schema.json`, just like `presentation-signals`) — drop everything
that is not an `AIS-*` pattern, verbatim-span anchoring (unanchored above-info →
`info`), `skill` forced to `ai-style-impressions`, `not_integrity_finding` forced
`true`, FP-risk forced `high`, observability fixed to `0`, `fp_case` /
`recommended_reviewer_action` defaulted if missing, enum coercion, and cross-model
provenance. **No severity cap** — capping is unnecessary because
`tools/adjudicate_findings.py` independently forces every AIS finding to `info` (by
`skill`, by the `AIS-` prefix, AND by the deprecated-style-id set) and assigns it
`_verdict_weight = 0`, so it is excluded from `overall_verdict` no matter what severity
it carries here.
