---
name: blog
description: "How to write a technical blog post about your own experiments, the kind a strong deep-learning researcher would publish: the story arc from the surprise that started the work to open questions and related work, a voice after Sasha Rush, Phillip Isola and Lilian Weng, how figures and text share the work, links to the full experiment record, fluent Chinese for a bilingual post, and the audit that keeps numbers, links and claims intact through every rewrite. Use with writing:style for sentences and writing:plot for figures."
---

# Blog

A post tells one story about experiments whose full record lives elsewhere (an experiment page, a repo, a run table). The
post is shorter and sharper than the record; it never tries to be the record. Load `writing:style` for sentence rules and
`writing:plot` (section "Figures in a post") for charts. Rules below cite the owner's words where they come from.

## The story

1. **Open with the setup made visible.** One short animation or schematic shows every part of the experiment and the
   compared variable before the reader meets a sentence (owner, 2026-10-31: "做最前面一个视频来讲这个setup").
2. **Motivation: the surprise that started the work.** One paragraph and one figure: what you expected, what happened, and
   the question it raised. End on that question.
3. **Setup in at most three short paragraphs.** Define every term the post uses later, once, at first use.
4. **One section per finding.** The heading states the finding; the first sentence says it again in plain words; the figure
   carries the evidence; the last sentence says what it implies or which question comes next.
5. **Controls before mechanism.** Right after the main effect, rule out the confounds a skeptical reader thinks of first.
6. **Then where the effect sits, what reduces it and by how much, and what is left.**
7. **Close with limitations (three or four sentences), takeaways (the claim and what a practitioner should do with it),
   open questions, related work, and a read-more card to the record.**

## The voice

Blend three writers (owner, 2026-10-31: "仿照 … sasha from cornell，phillip from mit，weng li from openai的风格"):

- **Sasha Rush, the sentence.** Short declarative sentences. A claim, then the smallest example that makes it obvious. A
  question only where it sets up the next step: two or three in a whole post. A question opening every section reads as a
  formula, and a question can smuggle in a comparison the data does not support; cut it.
- **Phillip Isola, the thesis.** One idea the reader can carry away, and intuition built from mechanism: say what a
  parameter actually sees, not that "the model overfits more". The thesis never outruns the evidence; a mechanism the
  experiments did not test is stated as a hypothesis or left out.
- **Lilian Weng, the structure.** Each term defined once and used the same way everywhere; sections that read as a sequence
  of questions and answers; related work grouped by theme, one sentence per work.

Concision (owner, 2026-10-31: "故事更精炼更有表达力"): cut every sentence that a heading, a figure subtitle or a caption
already says, and keep only the one or two numbers a paragraph rests on (`writing:style` RULE-18).

## Figures and text

- A post figure has a title that names it, a grey subtitle that states its finding, and a caption that says what is
  plotted and how it was measured (`writing:plot`, Figures in a post).
- The text cites every figure by number, before or where it appears, never repeats a subtitle word for word, and never
  names a colour: it names the series.
- Fewer, stronger figures; a figure that repeats another one's point goes, and its one result the argument needs stays as
  a sentence that links to where the figure now lives.

## Links to the record

- Link from the post only where the record holds something the post does not show: the code and recipe, every run with its
  training curves, a figure cut from the post, a test the post mentions in one sentence, a question still running. Not more
  and not fewer (owner, 2026-10-31: "不要多也不要少").
- Put the link on the words that describe its target, and point it at the precise anchor (a question heading or a figure),
  not at the top of the page.
- End the post with a read-more card to the record: its picture, its title and one sentence on what is there.

## Related work

- Open every source before citing it: title, authors in order, venue, and the claim with its numbers as the source states
  them. A reference from memory or from a survey gets checked first; a wrong author list or an invented claim is worse than
  no citation.
- One sentence per work for what it found, one clause for how it relates to this post; group by theme; end with one
  sentence on what this post adds that none of them does.
- A reader of a remedy will ask whether you tried it (owner, 2026-10-31: "我们related work里面的这些trick我们都试过在我们的
  setup下不管用吗"). Know the answer for each one, with your number, and be ready to say it in a clause.

## Open questions

- Each one: the question, what the experiments show so far, and the experiment that would answer it.
- Before calling a question open, search the record: a test may already exist. Report its result, even an inconclusive one,
  instead of proposing it as future work.

## A bilingual post

- Write each language for its own readers; never translate sentence by sentence (owner, 2026-10-31, on a Chinese version
  that read as translationese: "感觉这个中文我完全读不懂 … 要写出流畅的文字").
- Chinese for ML researchers: short to medium sentences with explicit connectives (因为、所以、但是、也就是说), no long
  attributive chains (……的……的……的), no stacked semicolon clauses, none of the translated-text habits (将……、进行……、被……).
  Keep English where Chinese ML writers keep it (token, embedding, BPE, softmax, EMA, batch), and keep the exact words the
  charts print for the main quantities.
- Same numbers, links and notes in both languages.

## Rewrites and style passes

- A rewrite or a style pass changes words, not facts. Before and after, compare mechanically: the numbers of each language
  as multisets, every href, every note marker, every figure reference, and the elements that are not prose (figures,
  schematics, cards). Anything lost or added is a bug unless it was the point of the edit.
- After a model writes or polishes prose, read it for: questions in series, a thesis beyond the evidence, a figure credited
  with what it does not show ("as the video shows" on a claim the video does not make), advice stronger than the result
  ("choose a smaller vocabulary" where the data say "choose with the number of passes in mind"). Fix these by hand.
- Facts come from the record's generated fact sheet, never from memory; a number that is not in it does not go in the post.
