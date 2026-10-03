---
type: llm
focus:
  source: file
  path: sections/method.tex
---
This file is the opening of a paper's method section, before its first subsection.

PASS if the first sentence after the \section line is a concrete technical statement, such as the problem setup (a model producing reasoning steps s_1..s_T), a definition of the step score, or an equation, AND the text does not walk through the upcoming subsections (no sentence that previews "the step scorer, the budget allocator, and the stopping rule" as a list of what the section will cover, and no "Section 3.1 describes ..., Section 3.2 ...").

FAIL if the opening is an overview or roadmap: it starts with "In this section", "We propose TRACE, a framework that ...", or lists the three components as a preview of the subsections, or references the subsections one by one.
