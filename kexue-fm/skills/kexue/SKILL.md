---
name: kexue
description: 科学空间 kexue.fm（苏剑林博客）全站本地库。用户提到「苏剑林 / 苏神 / 科学空间 / kexue.fm / 博文」，或问 RoPE、线性Attention、扩散模型、Muon、位置编码、最大熵、VAE、GAN、Transformer升级之路 等这些文章讲过的主题，或给出 kexue.fm/archives/<id> 链接时触发。能做：检索、读某篇（Markdown + LaTeX 原样）、列系列篇目、找上下文与互引、给官方引用格式、按主题看演化时间线、增量同步新文。纯中文，离线读本地 SQLite。
---

# kexue：科学空间本地库

一个脚本、一个库。所有操作走 `kexue.py`：

```bash
KX="${CLAUDE_PLUGIN_ROOT}/scripts/kexue.py"   # 变量为空时用 ~/.claude/plugins/marketplaces/wenhaochai/kexue-fm/scripts/kexue.py
```

| 任务 | 命令 |
|---|---|
| 检索 | `python3 "$KX" search 词1 词2 [--tag 标签] [--category 分类] [--year 年] [--since 日期] [--series 系列] [--sort rank\|date\|old\|readers] [--limit N] [--excerpt]` |
| 读一篇 | `python3 "$KX" show ID [--toc \| --excerpt \| --section 小节标题 \| --max-chars 0]` |
| 系列 | `python3 "$KX" series` 列全部；`series 升级之路` 列篇目（`--excerpt` 附摘要） |
| 上下文 | `python3 "$KX" related ID` 同系列、上下篇、本文引用的、引用本文的、站内相似、同标签、文中 arXiv |
| 统计 | `python3 "$KX" stats` 篇数、分类、年份、标签、阅读榜 |
| 同步 | `python3 "$KX" sync` 增量抓取新文章（需要 requests、beautifulsoup4、lxml） |

## 怎么用

**检索。** 把问题拆成 1–3 个词，用文中常见写法：「位置编码」而非「相对位置」，「语言模型」而非「LLM」，英文术语原样（RoPE、softmax、Muon）。全文索引是 trigram，3 个字符以上的词按 bm25 排序（标题权重最高），更短的词退化为 LIKE。命中为 0 就换同义词；命中过多加 `--series` 或 `--sort readers`。arXiv 编号可直接当检索词（`search 2104.09864`），因为正文里的链接也被索引。

**读。** 长文先 `--toc`，再 `--section` 按小节读，不要一次读完 3 万字。苏剑林的文章结构固定：动机 → 推导 → 实验 → 文章小结；讲解沿这个顺序，公式按原文 LaTeX 记号引用，数值只引文中写的。`show` 末尾自带官方引用格式和 BibTeX，用户要引用时直接给。

**回答技术问题。** 先 `search` 找 2–5 篇，再 `show --section` 读关键推导，最后按「结论 → 推导链（3–6 步）→ 出处（id + 标题 + 链接）」作答。同一主题的后续文章可能修正了早期结论，用 `related ID` 看「引用了本文的文章」，把最新的认识也交代出来。

**看演化。** `search 词 --sort old` 得到按时间排列的命中，按年份分组讲；或 `series 名称` 直接给系列顺序。

**最新文章。** 库截止到最近一次 `sync`（`stats` 第一行给出日期范围）。用户问「最近」「新出的」时先跑 `sync`，再 `search --sort date --limit 10`。

## 边界

- 覆盖全站 10 个分类、2009 年至今的全部文章；不含评论区。
- 图片只保留 URL；表格已转 Markdown。
- 输出给用户的链接格式：`https://kexue.fm/archives/<id>`。
