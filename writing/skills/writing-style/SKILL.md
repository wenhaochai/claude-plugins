---
name: writing-style
description: Default writing standards. Use whenever producing English prose the user will send or publish — emails, message drafts, blog posts, tweets, documentation, grant proposals, and conference/journal paper drafts (NeurIPS, ICML, ICLR, ACL, CVPR, COLM, EMNLP, arxiv). Applies 12 canonical rules everywhere; additionally apply 5 page-capped additions (RULE-P1..P5) when the target is a page-constrained paper. Treat all rules as peer constraints and apply at generation time, not as a post-hoc linter.
---

# Writing Style

Default standards for English prose. Apply at generation and edit time. All rules are peers; no group is higher priority than another.

**Scope.** RULE-01..12 apply to every writing task — email, message draft, post, doc, paper prose. RULE-P1..P5 apply *only* when the target is a page-capped paper (NeurIPS/ICML/ICLR-style 8-10 page caps and similar); skip them for email and short-form prose where they would over-constrain tone.

## Canonical (RULE-01..12)

Distilled from Strunk & White, Orwell, Pinker, and Gopen & Swan.

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

## Page-capped paper additions (RULE-P1..P5)

Additions for page-constrained conference papers (NeurIPS/ICML/ICLR 9-page caps and similar). Field-observed from paper-review workflows.

- **RULE-P1** Do not use em-dashes (`---`) or prose parentheses `()` in body text. Use colons plus lists, `, namely ...`, `, where ...`, or new sentences instead. Math parentheses (ordered pairs, function application, set notation) and page-range en-dashes (`pp.~12--15`) are exempt.

- **RULE-P2** Do not write section or subsection overview paragraphs. Do not open §3 Method with "We propose X, a framework that does (1) ..., (2) ..., (3) ...". Let the section-level figure caption, the algorithm block, and the component subsections carry the overview. The introduction already introduced the method.

- **RULE-P3** Do not use `\emph`, `\textit`, or `\textbf` for emphasis in body prose. Reserve typographic emphasis for at most 1–2 signature concepts per paper, introduced once. For local emphasis, change wording: pick a precise verb, use parallel structure, or restructure the clause. `\textbf` in body text is almost never justified; reserve for table headers and figure-caption labels.

- **RULE-P4** Researcher voice. Do not open sections or paragraphs with meta-scaffold sentences: "The motivation is empirical:", "In this section, we ...", "To begin, ...". Start with the concrete claim or observation. Do not plain-ify researcher-formal terms (`regime`, `load-bearing`, `orthogonal`, `ablation`, `identifiable`); they carry precision. Delete redundant forward and backward references such as `(defined in §3.2)` or `, as discussed above`, when the surrounding text already introduces the concept.

- **RULE-P5** Space economy under page caps. Before adding a paragraph, numbered list, or subsection, ask what information is lost if it is cut; if the answer is "only structural scaffold", do not add it. Do not default to a numbered Contributions list in the introduction; let contributions emerge through the narrative. Keep titles to a method name plus 1–2 signature concepts; stack more than two concepts in a title signals either unfocused framing or a missing abstract.

## Escape hatch

Break any rule sooner than write something awkward (Orwell 1946 Rule 6). Rules serve clarity; they are not ends in themselves.

## Self-check

When an agent loads this skill, a one-line acknowledgment confirms activation:

> writing-style v0.2.0 active: 12 canonical rules (RULE-01..12) + 5 page-capped additions (RULE-P1..P5, paper-only).

## Credits

RULE-01 through RULE-12 are from [agent-style](https://github.com/yzhao062/agent-style) by Yue Zhao, redistributed under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). See agent-style's `SOURCES.md` for the primary-source bibliography (Strunk & White 1959, Orwell 1946, Pinker 2014, Gopen & Swan 1990).

RULE-P1 through RULE-P5 are additions by Wenhao Chai, distilled from NeurIPS / ICML / ICLR paper-review workflows.
