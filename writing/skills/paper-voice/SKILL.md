---
name: paper-voice
description: The prose voice of pre-2023 papers by Kaiming He, Joseph E. Gonzalez and Alex Dimakis, measured on 15 arXiv sources, plus Dimakis's own writing notes ("Ideas for better writing", 2018), for drafting or rewriting research-paper prose that reads as LLM-written. Load it with writing:style for any paper; where the two disagree (parentheses, repeated key terms, "In this paper", contribution lists, hedges, italics at a definition), this skill wins. voice_stats.py counts a draft against the corpus.
---

# Paper voice

A reader called a draft "VERY claude". Its sentences were the right length (22.0 words against the corpus's 21.7); what
gave it away was what the sentences did and how they joined. These rules come from counting the abstract, introduction
and first method section of 15 papers written before LLM drafting (32,697 words):

| Author | arXiv |
|---|---|
| Kaiming He (first author) | 1512.03385 ResNet, 1703.06870 Mask R-CNN, 1811.08883 Rethinking ImageNet Pre-training, 1911.05722 MoCo, 2111.06377 MAE |
| Joseph E. Gonzalez (lab) | 1006.4990 GraphLab, 1402.2394 GraphX, 1612.03079 Clipper, 1812.03651 Serverless: One Step Forward, 1902.03383 Berkeley View on Serverless, 2201.12023 Alpa |
| Alex Dimakis | 1003.5309 Gossip Algorithms, 1301.3791 XORing Elephants, 1612.03301 Gradient Coding, 1703.03208 Compressed Sensing using Generative Models |

Rates are per 1000 words. "Draft" is the LLM-written paper that prompted this skill (FrontierCS 2, 2026-10-19).

## Rules

1. **Put the authors in the text.** Corpus "we/our/us" 16.4, and 13.7% of sentences open with We or Our; draft 4.3 and
   4.7%. Narrate the choices: we built, we chose, we found, we ask.
   - "We hypothesize that it is easier to optimize the residual mapping than to optimize the original, unreferenced
     mapping." (1512.03385)
   - "In this paper we show that feedback and coordination is not necessary" (1612.03301)
2. **A consequence is a sentence, not a ", so" tail.** Corpus 0.24, draft 4.0 (17 times). At most one ", so" per page.
   Write the consequence as its own sentence, or cut it when the figure shows it.
3. **Say how sure you are, and what you think.** Corpus hedges (may, can, likely) 8.6, "we believe/hypothesize/expect"
   0.46, questions 0.15; draft 2.6, 0, 0. Hedge where the evidence is partial. Give a stance where the authors hold
   one, as a "we" sentence, never as an aphorism.
   - "The reason may stem from differences in their respective signal spaces." (1911.05722)
   - "we raise a set of challenges we believe must be met" (1812.03651)
4. **Open with a scene or a question, then the gap, then "In this paper".** Every corpus introduction starts from one
   concrete situation or one question before it describes the design.
   - "Driven by the significance of depth, a question arises: Is learning better networks as easy as stacking more
     layers?" (1512.03385)
   - "For example, consider an online news organization that wants to deploy a content recommendation service"
     (1612.03079)
5. **List the contributions once.** "In summary, our key contributions are:" with bullets (1612.03079, 2201.12023),
   "Our Contributions:" (1301.3791, 1703.03208), or "(i) (ii) (iii)" in prose (1811.08883). One list, in the
   introduction. Sections still open with their content, not an overview.
6. **Explain the intuition.** After a mechanism, say in one sentence why it should work.
   - "Intuitively, a larger dictionary may better sample the underlying continuous, high-dimensional visual space"
     (1911.05722)
7. **Short paragraphs, one turn each.** Corpus 3.7 sentences and 80 words per paragraph; draft 5.6 and 123. Start a new
   paragraph when the argument turns. A two-sentence paragraph that poses the problem is normal.
8. **Link back with "This" and repeat the key noun.** Corpus 6.7% of sentences open with This or These; draft 1.0%.
   Re-use the defined term and its notation; do not hunt for synonyms. Ordinary words still follow writing:style
   RULE-16 (no repeat in the same or the next sentence), as Dimakis's notes also ask.
   - "This enables building a large and consistent dictionary on-the-fly" (1911.05722)
9. **Vary openings.** Corpus 23.8% of sentences open with a subordinate or prepositional clause ("By restricting ...",
   "Unlike model development, ...", "Despite that potential, ..."); draft 14.7%.
10. **Parentheses for asides, and rarely.** Corpus 10.4 per 1000 words, footnotes 0.6; draft 0 and 0. Use them for an
    example, a gloss or a side fact, never for the main claim, never nested, and at most one per paragraph: Dimakis
    (his notes) asks for them "only in very rare situations", and his own papers use 7.2 per 1000 words. Em-dashes
    stay rare (corpus 0.8).
    - "Inference is the process of using the model to make a prediction given an input (e.g., predict a user's rating
      for a movie)." (1612.03079)
11. **Drop the contrast tics.** Against the corpus the draft had ", not X" 8 times, "still" 6, "instead" 4, "only" 2 and
    "each/every" 2.8 times as often. Keep one only when the contrast is the claim.
12. **No colon reveals.** Corpus colons introduce a list, a definition or a question ("We ask: ..."), not a punchline
    ("Cost does not order the agents: ...").
13. **No rhythmic closers.** Do not end a paragraph on an aphorism ("Finding results like this one still takes reading
    the patches.") or a chiasmus ("The reply shrinks, and with it each lookup."). End on the fact, or on what the
    authors make of it.
14. **Numbers: a few, plain, early.** The corpus gives one or two headline numbers in the abstract and introduction ("a
    vanilla ViT-Huge model achieves the best accuracy (87.8%)", 2111.06377) and few in discussion prose. Do not swap a
    number for a precise-sounding quantifier chain ("more often than most agents that cost more per run"): give the
    number once, or make a coarser claim.
15. **Italics once, at a definition.** He sets a new term in \emph where he defines it, and nowhere else.
16. **No run-in labels in argument prose.** Bold lead-ins such as "The task.", "Two designs.", "Results." over a case
    study or a results subsection read as LLM scaffolding (the owner, on FrontierCS 2, 2026-10-19). Let the first
    sentence of each paragraph name its topic. Named groupings that a reader scans (related-work families, numbered
    appendix steps, setup items like "Agents." and "Cost.") may keep `\paragraph`.

## From Dimakis's notes ("Ideas for better writing", 2018)

Alex Dimakis wrote these notes for his students. Several of them are already writing:style rules: one thesis per
paragraph (RULE-P11), the simplest example first (RULE-P12), captions that stand alone (RULE-P13), theorems as an API
(RULE-P14), restating a symbol's role (RULE-P15), at most one or two new names (RULE-P16), equation punctuation
(RULE-P17), no repeated word nearby (RULE-16) and no apologizing (RULE-17). The rest is below.

17. **Run a reader simulator.** Before a pass, name the reader (a first-year graduate student, someone in the general
    area, an expert on the topic) and read every claim as that reader. Mark what they find obvious, trivial or
    confusing.
18. **Answer "who cares" for that reader.** Most readers are made to read the paper. Tie the work to what they already
    care about (their own work, or something fundamental) rather than to why the authors find it interesting.
19. **Do not hide the simple idea.** Fear of sounding obvious makes papers bury a simple idea under a general or
    complicated statement. State the simple idea plainly; that is what readers remember.
20. **One story.** More results do not make a paper stronger. A side result that does not serve the main narrative
    (Dimakis's "friend Bob and his car") weakens it: cut it, or move it to an appendix. Before keeping a paragraph,
    ask what the reader is supposed to get from it.
21. **Self-contained sections.** A reader should follow the experiments without the theory and any caption without the
    rest. Avoid definitions on one page that a claim needs ten pages later; an appendix restates what it proves.
22. **Keep definitions, assumptions and results apart,** and keep theoretical results apart from practical ones. State
    an assumption once, with its justification, in one place.
23. **Experiments that teach.** Test outside the assumptions (robustness, not just agreement with the theory). Move one
    parameter at a time. For every plot and every paragraph, say what the reader should learn. Compare apples to
    apples: reuse the baseline's data, metric and plot form.
24. **No conceptual spaghetti.** Not "In this work, requiring A, and similarly to B (even though it required C), we show
    D." Write: "In this work we show D. We require A. This is similar to B. Note that B required C." One topic per
    sentence; a sentence that carries two topics is split whatever its length (aim near 20 words; writing:style
    RULE-12 still splits anything over 30).
25. **Cut words, then adverbs.** For every word, ask whether it can go. Delete adverbs. Avoid opening a sentence with
    "Therefore", "However" or "Thus"; if one stays, follow it with a comma.
26. **A citation is not a noun.** "Bellman et al. [5] introduced dynamic programming", never "[5] introduced dynamic
    programming", least of all at the start of a sentence (`\citet`, writing:style RULE-P6).
27. **Small conventions.** No scare quotes. Write eigenvector, semidefinite and bipartite without hyphens. Figures are
    vector graphics. A title does not repeat a word. When unsure of a convention (et al., a term, an abbreviation),
    copy how established papers in the field do it.
28. **Write in drafts.** Dimakis polished his notes over seven drafts and an NSF proposal over 27 versions. Expect
    several passes, each with one goal (story, then paragraphs, then sentences, then words); `voice_stats.py` reports
    the mechanical items 24-26 as well.

## From Sophie Wang ("Behind the scenes of paper writing", 2026)

29. **Two narratives, each standing alone.** The figures with their captions tell the whole story; the prose
    tells it too. They do different jobs: the figures let the results speak (writing:plot, "Figures in a
    paper"); the prose says why the problem is interesting, why these experiments, and what we conclude from
    them. If a result does not speak for itself in its figure, simplify the experiment or show the result more
    directly before writing around it.
30. **Aim at a change in understanding.** The test of the paper is whether the reader leaves understanding
    something fundamental better and can apply it to a problem they care about (rule 18 names that reader).

## Where this overrides writing:style

| writing:style | Corpus | Here |
|---|---|---|
| RULE-13 no prose parentheses or em-dashes | 10.4 parentheses, 0.8 em-dashes | Parentheses allowed for asides, at most one per paragraph and never nested; em-dashes rare |
| RULE-16 no repeated content word in adjacent sentences | key nouns repeated; 6.7% open with This/These | Repeat defined terms and notation; link with This; ordinary words still follow RULE-16 |
| RULE-08 and "relations over adjectives" | 8.6 hedges, 2.6 intensifiers | Hedges and a stance allowed; no unquantified "significantly" in results |
| RULE-P1 no overview paragraphs | "In this paper" 0.6; a contribution list in all three authors | One "In this paper" and one contribution list in the introduction |
| RULE-P2 no emphasis | \emph at definitions | Italics at a term's definition only |
| RULE-12 split at 30 words | 16.8% of sentences over 30 words | Soft limit; mix setup, intuition and claim sentences |

Everything else in writing:style stands.

## Before and after (facts unchanged)

1. "The judge keeps the evaluator, the held-out final suite and the human reference private, so the agent gets
   feedback during the run without seeing any of them." → "The agent gets feedback while it works, but it never sees
   how that feedback is computed. The evaluator, the held-out final suite and the human reference all stay with the
   judge."
2. "Most runs whose final score exceeds the human reference's still fall short of the reference on at least one metric
   or workload, so a higher final score does not imply a pass." → "A higher final score does not mean a pass. In fact,
   most runs that score above the human reference miss it on at least one metric or workload."
3. "It may edit only the allowed files, those that held the contribution, and may add new modules in a directory set
   aside for them." → "The agent may edit only the files that held the contribution (and add new modules in one
   designated directory)."
4. "An agent's FCI is its strength relative to Kimi K2.7's at ten points per logit, so Kimi K2.7 is 0." → "We report
   strength on a scale of ten points per logit, measured from Kimi K2.7 (which therefore has an FCI of 0)."
5. "Neither of the benchmark's measures picks out the idea: ... Finding results like this one still takes reading the
   patches." → "We found this idea only by reading the patches; neither of our measures would have surfaced it."

## Process

1. Rewrite one section at a time; keep every fact, number and citation.
2. Count: `python voice_stats.py <paper-dir or .tex files>`. Rows marked `*` are more than twice the corpus on a
   should-be-low metric (", so", ", not X", "instead", paragraph length) or under half of it on a should-be-high one
   ("we", hedges, parentheses, This openings). Aim to clear every `*`, not to match the corpus to the decimal.
3. Read it aloud. A sentence that could close any paper gets cut.
