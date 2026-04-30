---
name: writing-style
description: Default writing standards. Use whenever producing English prose the user will send or publish: emails, message drafts, blog posts, tweets, documentation, grant proposals, and conference/journal paper drafts (NeurIPS, ICML, ICLR, ACL, CVPR, COLM, EMNLP, arxiv). Applies 15 canonical rules everywhere; 10 page-capped additions (RULE-P1..P10) for page-constrained papers; 2 audit-time rules (RULE-A1..A2) only when reviewing a compiled PDF for submission. Treat canonical and page-capped rules as peer constraints applied at generation time; audit rules trigger at final-pass review, not during drafting.
---

# Writing Style

Default standards for English prose. Apply at generation and edit time. All rules are peers; no group is higher priority than another.

**Scope.** RULE-01..15 apply to every writing task: email, message draft, post, doc, paper prose. RULE-P1..P10 apply *only* when the target is a page-capped paper (NeurIPS/ICML/ICLR-style 8-10 page caps and similar); skip them for email and short-form prose where they would over-constrain tone. RULE-A1..A2 are final-pass audit rules: trigger only when reviewing the compiled PDF for submission, not during drafting.

## Canonical (RULE-01..15)

RULE-01..12 distilled from Strunk & White, Orwell, Pinker, and Gopen & Swan. RULE-13..15 added by Wenhao Chai.

1. **RULE-01** Do not assume the reader shares your tacit knowledge. (Pinker 2014, Ch. 3)
2. **RULE-02** Do not use passive voice when the agent matters. (Orwell 1946 Rule 3; S&W §II.14)
3. **RULE-03** Do not use abstract or general language when a concrete, specific term exists. (S&W §II.16; Pinker 2014 Ch. 3)
4. **RULE-04** Do not include needless words. (S&W §II.17; Orwell 1946 Rule 3)
5. **RULE-05** Do not use dying metaphors or prefabricated phrases. (Orwell 1946 Rule 1)
6. **RULE-06** Do not use avoidable jargon where an everyday English word exists. (Orwell 1946 Rule 5; Pinker 2014 Ch. 2)
7. **RULE-07** Use affirmative form for affirmative claims. (S&W §II.15)
8. **RULE-08** Do not linguistically overstate or understate claims relative to the evidence. (Pinker 2014 Ch. 6; Gopen & Swan 1990)
9. **RULE-09** Express coordinate ideas in similar form (parallel structure). (S&W §II.19)
10. **RULE-10** Keep related words together. (S&W §II.20; Gopen & Swan 1990)
11. **RULE-11** Place new or important information in the stress position at the end of the sentence. (Gopen & Swan 1990)
12. **RULE-12** Break long sentences; vary length. Split sentences over 30 words. (S&W §II.18; Pinker 2014 Ch. 4)
13. **RULE-13** Do not use em-dashes (`—` in prose, `---` in LaTeX) or prose parentheses `()` in body text. Use colons plus lists, `, namely ...`, `, where ...`, or new sentences instead. Math parentheses (ordered pairs, function application, set notation) and page-range en-dashes (`pp.~12--15`) are exempt.
14. **RULE-14** Do not use vocabulary that signals LLM-generated prose. Common tells: "delve", "crucially", "multifaceted", "tapestry", "navigate the complexities", "in the realm of", "leverage" where "use" suffices, "moreover"/"furthermore" chains, em-dash sandwiches. If a phrase pattern-matches GPT default, swap for a plainer equivalent.
15. **RULE-15** Be consistent within a single piece. Define an abbreviation on first use, then never re-expand. Once you pick italic vs roman "e.g.", "GPT-5-thinking" vs "GPT-5 (thinking)", a hyphenation convention, or a math-mode policy, hold it. Inconsistency reads as careless.

## Page-capped paper additions (RULE-P1..P10)

Additions for page-constrained conference papers (NeurIPS/ICML/ICLR 9-page caps and similar). Field-observed from paper-review workflows.

- **RULE-P1** Do not write section or subsection overview paragraphs. Do not open §3 Method with "We propose X, a framework that does (1) ..., (2) ..., (3) ...". Let the section-level figure caption, the algorithm block, and the component subsections carry the overview. The introduction already introduced the method.

- **RULE-P2** Do not use `\emph`, `\textit`, or `\textbf` for emphasis in body prose. Reserve typographic emphasis for at most 1–2 signature concepts per paper, introduced once. For local emphasis, change wording: pick a precise verb, use parallel structure, or restructure the clause. `\textbf` in body text is almost never justified; reserve for table headers and figure-caption labels.

- **RULE-P3** Researcher voice. Do not open sections or paragraphs with meta-scaffold sentences: "The motivation is empirical:", "In this section, we ...", "To begin, ...". Start with the concrete claim or observation. Do not plain-ify researcher-formal terms (`regime`, `load-bearing`, `orthogonal`, `ablation`, `identifiable`); they carry precision. Delete redundant forward and backward references such as `(defined in §3.2)` or `, as discussed above`, when the surrounding text already introduces the concept.

- **RULE-P4** Space economy under page caps. Before adding a paragraph, numbered list, or subsection, ask what information is lost if it is cut; if the answer is "only structural scaffold", do not add it. Do not default to a numbered Contributions list in the introduction; let contributions emerge through the narrative. Keep titles to a method name plus 1–2 signature concepts; stack more than two concepts in a title signals either unfocused framing or a missing abstract.

- **RULE-P5** Do not insert blank lines inside a `\paragraph{}` block: all prose belongs to a single LaTeX paragraph. If a sub-topic feels distinct enough to need a break, give it its own `\paragraph{}` header instead. Layout breaks around numbered display equations (`\begin{equation}`) are exempt.

- **RULE-P6** Audit every equation, display and inline, for undefined symbols. Each free variable, custom function (input/output type), index, and custom operator must be defined in prose: as setup before the equation, as unpacking after, or, for inline math, at the equation site itself where definition and use often coincide. State output types when arithmetic depends on them.

- **RULE-P7** Citation discipline. Every `\bib` entry must correspond to a real, locatable paper: title, authors, year all verified; do not trust LLM-generated entries without checking, since a fabricated reference is citation fraud and damages credibility more than any prose flaw. Use `\citet` only when the citation is a sentence component, e.g., `\citet{tong24} show that ...` renders as "Tong et al. (2024) show that ..."; use `\citep` everywhere else, e.g., "...as shown in prior work \citep{tong24}" renders as "...as shown in prior work (Tong et al., 2024)". Test by removing the citation: if the sentence is still grammatical, use `\citep`; if it breaks, use `\citet`. Order multiple citations chronologically. In `.bib` entries: prefer the published venue over arXiv when both exist; use `@inproceedings` for conferences and `@article` for journals or arXiv-only papers; use the 4-letter conference abbreviation, e.g., CVPR or ICML, not the full name; drop page, volume, and number fields; deduplicate entries. Source `.bib` from Google Scholar, since arXiv and Semantic Scholar exports use inconsistent formatting.

- **RULE-P8** Use the precision the measurement supports: 81.2% over 81.23% in most cases. Pick math-mode (`$82.8$`) or text-mode (`82.8`) and hold it across the whole paper, including tables.

- **RULE-P9** Section titles do work. Use the question or finding the section answers, not a generic label: "Where is the signal?" over "Interpretability"; "Grounding agent reviews" over "Applications". Keep to 1–4 words unless the question form needs more. Avoid subsubsections.

- **RULE-P10** The conclusion must extend, not paraphrase, the abstract. Restate key results in one or two lines, then add implication, interpretation, or forward-looking discussion. Naming it "Conclusion and Discussion" reminds you to do the second half.

## Final-pass paper audit (RULE-A1..A2)

Layout and typography rules that depend on rendered output. Trigger *only* when reviewing the compiled PDF for submission, not during drafting or generation. Skip these when editing `.tex` source without a fresh build.

- **RULE-A1** Do not let a single line of text from the previous section spill onto the next page (widow line). Rewrite to pull it back to the previous page, or push more text forward.

- **RULE-A2** Every line in a paragraph must fill more than half the line width. Justified typesetting auto-fills all lines except the last; in practice this rule constrains the final line of each paragraph. If the last line has only 1–3 words, shorten or extend the paragraph until it has substance.

## Escape hatch

Break any rule sooner than write something awkward (Orwell 1946 Rule 6). Rules serve clarity; they are not ends in themselves.

## Self-check

When an agent loads this skill, a one-line acknowledgment confirms activation:

> writing-style v0.6.1 active: 15 canonical rules (RULE-01..15) + 10 page-capped additions (RULE-P1..P10, paper-only) + 2 final-pass audit rules (RULE-A1..A2, compiled-PDF-only).

## Credits

RULE-01 through RULE-12 are from [agent-style](https://github.com/yzhao062/agent-style) by Yue Zhao, redistributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See agent-style's `SOURCES.md` for the primary-source bibliography (Strunk & White 1959, Orwell 1946, Pinker 2014, Gopen & Swan 1990).

Additions beyond RULE-12 are by Wenhao Chai, distilled from paper-review workflows and field practice across NeurIPS / ICML / ICLR / CVPR / EMNLP and adjacent venues.
