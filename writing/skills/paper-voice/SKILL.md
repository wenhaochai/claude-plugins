---
name: paper-voice
description: The prose voice of pre-2023 papers by Kaiming He, Joseph E. Gonzalez and Alex Dimakis, measured on 15 arXiv sources, for drafting or rewriting research-paper prose that reads as LLM-written. Load it with writing:style for any paper; where the two disagree (parentheses, repeated key terms, "In this paper", contribution lists, hedges, italics at a definition), this skill wins. voice_stats.py counts a draft against the corpus.
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
   Re-use the defined term; do not hunt for synonyms.
   - "This enables building a large and consistent dictionary on-the-fly" (1911.05722)
9. **Vary openings.** Corpus 23.8% of sentences open with a subordinate or prepositional clause ("By restricting ...",
   "Unlike model development, ...", "Despite that potential, ..."); draft 14.7%.
10. **Parentheses for asides.** Corpus 10.4 per 1000 words, footnotes 0.6; draft 0 and 0. Use them for an example, a
    gloss or a side fact, never for the main claim. Em-dashes stay rare (corpus 0.8).
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

## Where this overrides writing:style

| writing:style | Corpus | Here |
|---|---|---|
| RULE-13 no prose parentheses or em-dashes | 10.4 parentheses, 0.8 em-dashes | Parentheses allowed for asides; em-dashes rare |
| RULE-16 no repeated content word in adjacent sentences | key nouns repeated; 6.7% open with This/These | Repeat key terms; link with This |
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
