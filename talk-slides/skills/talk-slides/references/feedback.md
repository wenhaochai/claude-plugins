# The author's revision notes

These notes came in over 29 published versions of one paper talk: a paper on picking a subset of benchmark tasks, a part on why benchmark rankings agree, four public indices, and two grading errors in an agent benchmark. Each row gives the note in the author's words, what changed in the deck, and the rule that the note became in `SKILL.md`.

## Standing preferences

- Replies in chat are short. Open decisions come as a few short multiple-choice questions.
- Slides, talks and notes stay plain: facts and numbers, no slogans, no elevated framing.
- English on slides follows the author's prose rules: no "X, not Y" construction, no comma-joined clipped headlines, no em dashes, no "campaign" outside verbatim quotes.
- Before publishing, read the live deck and keep any edit made in the page.
- The speaker reads the English script in a second language: short lines, common words and no names that are hard to say.

## Notes in order

| # | Note | Change | Rule |
|---|---|---|---|
| 1 | 表不够直观，全换成图 | Every table became a chart | Charts over tables |
| 2 | 这种没对齐？ | Titles and legends had shifted one column left in the runtime; offsets moved into pinned hosts | Check alignment in the runtime itself |
| 3 | 全面审计 | Every slide rendered in the runtime and every number rechecked against raw data | Audit before each publish |
| 4 | paper本身讲太多了，首先你应该来个paper首页截图，然后一张图是做法，一张图是直观的对比结果，就结束了 | The paper part cut to three slides; the data and critique slides deleted | The paper takes three slides |
| 5 | 论文的第三页讲的不是很清楚，只是一个数但没有对应的拟合图 | A fit plot added next to ρ = 0.99 | A headline number sits beside its figure |
| 6 | 对就是这个…，别的不用引用了 | The part rebuilt on the one post the author named | Cite only the sources the author names |
| 7 | 找一个好的办法用一页说明这个问题 | Two slides merged into one | One idea per slide |
| 8 | 然后第三部分是分别一页一页介绍每一个index | One slide per index | One slide per method, index or example |
| 9 | 首页的副标题就在乱写啊 | The cover subtitle became paper, author and date | The cover states facts |
| 10 | part2太多字了，我需要你直接给出重点 | The slide reduced to the equation, one figure and one chart | Say the point directly |
| 11 | 第二页也要修一下 | The agenda rewritten to match the parts | The agenda matches the deck |
| 12 | 第六页你怎么体现claudiness呢？想想办法 | A diverging bar chart of the second component's weights | Show the concept as a chart |
| 13 | 每页slides的文字量还是太多了，减少！ | Text cut on every slide, the detail moved to the notes | Labels and numbers on the slide, sentences in the notes |
| 14 | 第八页可以删掉，换成他们官网的这张图 | The index's own treemap replaced a redrawn chart | Use the official figure |
| 15 | Praise和Criticism不用这样列出来，我会直接写在讲稿里，你页面尽可能多的描述index的组成和原则就好 | Praise and criticism boxes removed; composition and scoring principles shown | Evaluation goes in the notes, principles on the slide |
| 16 | Claudiness这边没画错？ | The chart rechecked against the source table | Check every chart against its source |
| 17 | videomme openai是−0.35啥意思，不也应该是+0.35？ | Signs removed; the two ends labelled with their direction; the sign convention moved to the notes | Magnitudes with direction labels |
| 18 | 第11页要包括更多介绍 | The benchmark's intro slide gained how tasks, grading and scoring work | A new topic's first slide gives enough context |
| 19 | 14页重写 | The summary rewritten as one point per part and a closing line | Summary structure |
| 20 | 每一页的 How the score is built感觉有点没什么表达力，换点视觉信号强一点的 | Label-and-sentence rows replaced by charts, a pipeline and a worked example | Show mechanisms as charts and examples |
| 21 | 检查一下part3里是不是去做了很多低质量信息的可视化，去除掉 | Icons, an invented dot pattern, cost bars, a release timeline, a one-model score card and a mislabelled source bar removed | Every mark carries data that matters |
| 22 | Two benchmarks run on a subset 这种信息也不关键啊，我觉得不如你把现在各个index的leaderboard画个图呢 | A side fact replaced by each index's current leaderboard with its uncertainty | Show what the audience needs first |
| 23 | Claude Opus 5.5 66.16错了吧 | The leaderboard re-fetched; the source had updated overnight | Re-fetch live data on publish day |
| 24 | 整体你觉得还有什么要改吗，审计 | A shrunk summary slide and a clamped tick label fixed; optional edits offered as choices | Audit, then ask about optional changes |
| 25 | 每一页的标题，我不想你总是带有某些结论式的，你就简单的比如 AA Index Harbor Index这种名词说明一下这页是什么就好了 | Every title became a noun label; eyebrows name the part | Noun titles |
| 26 | 现在帮我写讲稿，中英双语 | The notes on all 14 slides became a script: Chinese paragraphs, then the same content in English | The notes are a bilingual script |
| 27 | 审计，讲稿口语化，我不是native speaker | One English sentence per line and at most 18 words, common words, rounded numbers, no time words that go stale | Spoken English for a second-language speaker |
| 28 | 讲稿再压短一些，不会读的名字就应该删掉 | The script cut by about 40% to near 12 minutes; authors, people in task data and hard product names replaced by roles | Short scripts without hard names |
| 29 | 中文在后、英文在前，中间空行 | English first, one blank line, then Chinese, without labels. The check behind it found that the runtime turns raw newlines in `<aside>` into spaces, so every script so far had shown as one paragraph; line breaks became `<br>` | Notes order, and `<br>` for every line break |

## What the rules protect against

- **Text walls.** The first drafts read like a report on slides. The fix each time was fewer words and a chart.
- **Decoration posing as information.** A request for stronger visuals was followed by a request to strip the weak ones. Keep a visual only when it shows data that matters to the talk.
- **Stale or wrong numbers.** One leaderboard number was out of date by the time the author read it, and one chart category misread what its source meant. Recompute from raw files, re-fetch live pages, and read every category label against the source.
- **Runtime drift.** Local previews passed while the runtime shifted a row, clamped a label and shrank a slide. Only the runtime audit catches these. The runtime also ran every script into one paragraph, because it reads raw newlines in `<aside>` as spaces; the file looked right until the notes panel was read.
- **A script too hard to read aloud.** The first script had long written sentences, exact decimals and names the speaker could not say. Short spoken lines, rounded numbers and roles in place of names fixed it, and the cut brought the talk from about 20 minutes to about 12.
