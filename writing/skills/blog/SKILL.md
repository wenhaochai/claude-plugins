---
name: blog
description: "How to write a technical blog post about your own experiments, the kind a strong deep-learning researcher would publish: the story arc from the surprise that started the work to open questions and related work, a voice after Sasha Rush, Phillip Isola and Lilian Weng, model posts to learn from (Cartesia's From Tokens to Bytes, anvilarth's RL for diffusion), one running example, how figures and text share the work, links to the full experiment record, fluent Chinese for a bilingual post, and the audit that keeps numbers, links and claims intact through every rewrite. Use with writing:style for sentences and writing:plot for figures."
---

# Blog

A post tells one story about experiments whose full record lives elsewhere (an experiment page, a repo, a run table). The
post is shorter and sharper than the record; it never tries to be the record. Load `writing:style` for sentence rules and
`writing:plot` (section "Figures in a post") for charts. Rules below cite the owner's words where they come from.

## The story

1. **Open with the setup made visible.** One short animation shows every part of the experiment and the compared
   variable before the reader meets a sentence (owner, 2026-10-31: "做最前面一个视频来讲这个setup"). The compared variable
   stays on screen for the whole loop, the content is real (real token splits, numbers read from the figure data), the
   type is large enough for the page width, and the loop ends on the main result; a generic schematic of boxes carries no
   information (owner, 2026-11-01, on such a video: "我觉得你开局的这个视频就做的不行").
2. **Motivation: the surprise that started the work.** One paragraph and one figure: what you expected, what happened, and
   the question it raised. End on that question.
3. **Background, then the setup.** A post about an object outside the reader's daily work first explains what it is and
   how it is built, in one short section (owner, 2026-11-01: "blog里应该还要包含一个tokenizer的介绍，什么是tokenizer，又是怎么
   训练的"). Then the setup, in at most three short paragraphs. Define every term the post uses later, once, at first use,
   with the field's standard name for what you did: "8 epochs on an eighth of the text", not "repeated data", which reads
   as duplicate documents (owner, 2026-11-01: "数据重复不是一个好词？有点让人误解").
4. **One section per finding.** The heading states the finding; the first sentence says it again in plain words; the figure
   carries the evidence; the last sentence says what it implies or which question comes next.
5. **Controls before mechanism.** Right after the main effect, rule out the confounds a skeptical reader thinks of first.
6. **Then where the effect sits, what reduces it and by how much, and what is left.**
7. **Close with limitations (three or four sentences), takeaways (the claim and what a practitioner should do with it),
   open questions, related work, and a read-more card to the record.**
8. **One running example.** Pick one concrete case early (a word, a prompt, a run) and come back to it where a section
   ends, so each finding is seen on the same case and the reader knows what is still unexplained (owner, 2026-11-01,
   holding up anvilarth's posts, whose sections end on "But there is still no fourth cup.").

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

No seed talk (owner, 2026-11-01: "把里面所有关于随机种子的描述删除，这很minimal而且不利于阅读"): a post says nothing about
random seeds or run counts, in the prose or the captions: no "one run", "averaged over runs", "a second seed shifts …",
"within seed noise". The record carries them; the post states what the runs show.

## Exemplars

Posts the owner holds up as models (owner, 2026-11-01: "写的也很好，非常好，深入浅出，值得学习"). Read one before
writing, for its moves, not its topic.

- Cartesia, "From Tokens to Bytes", parts I and II (2026; cartesia.ai/blog/from-tokens-to-bytes-part-1 and -part-2): the
  contributions as a numbered map before the evidence; background after that promise, so the reader knows why it matters;
  the same input shown under each method side by side; one metric carried through every comparison; experiments staged as
  questions, with baselines added one at a time; the post's own caveats in their own paragraphs.
- anvilarth, "RL for diffusion", parts 1 and 2 (anvilarth.github.io/rl-for-diffusion-part-1.html and -part-2.html): one
  running example, checked again where each section ends; each section ends on the limit that motivates the next; a toy
  case with real numbers before any formula, and every formula read back in plain words; the reader's doubt as a short
  question that opens the next step ("Why not just take more steps?"); a "where it breaks" paragraph for each method;
  advice marked as advice, apart from measured claims; a closing table of what to do in which situation, at what cost.
- Sasha Rush, Phillip Isola and Lilian Weng: see The voice.

## Figures and text

- A post figure has a title that names it, a grey subtitle that states its finding, and a caption that says what is
  plotted and how it was measured (`writing:plot`, Figures in a post).
- The text cites every figure by number, before or where it appears, never repeats a subtitle word for word, and never
  names a colour: it names the series.
- Fewer, stronger figures. Every figure carries one step of the argument; one that does not goes, with its paragraph (owner,
  2026-11-01: "图3及其描述删除，这个不重要"). Two figures that make the same point become one figure with two panels
  (owner, 2026-11-01: "fig 8和9是不是要merge一下，这表达意思都一样？"). A cut figure's one result that the argument needs
  stays as a sentence that links to where the figure now lives.

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

- In a draft, every sentence that guards a claim (a scope disclaimer, a compute caveat), hedges it, or announces pending work
  (queued, running, still being tested) is marked red for the author to check: `<span class="chk">` in prose, ⟦…⟧ in a
  caption or subtitle. Mark, do not delete; the author keeps or cuts each one, and the marks go before release (owner,
  2026-11-01: "这种防御性的占位语句你应该用红色标出，方便检查（全文都这样）").

- A rewrite or a style pass changes words, not facts. Before and after, compare mechanically: the numbers of each language
  as multisets, every href, every note marker, every figure reference, and the elements that are not prose (figures,
  schematics, cards). Anything lost or added is a bug unless it was the point of the edit.
- After a model writes or polishes prose, read it for: questions in series, a thesis beyond the evidence, a figure credited
  with what it does not show ("as the video shows" on a claim the video does not make), advice stronger than the result
  ("choose a smaller vocabulary" where the data say "choose with the number of passes in mind"). Fix these by hand.
- Facts come from the record's generated fact sheet, never from memory; a number that is not in it does not go in the post.
