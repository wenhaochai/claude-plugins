---
name: kexue
description: 科学空间 kexue.fm（苏剑林博客）全站本地库。用户提到苏剑林、科学空间、kexue.fm，或想查这些文章讲过的主题（RoPE、线性Attention、扩散模型、Muon、MuP、MoE、最大熵、VAE 等），或给出 kexue.fm/archives/<id> 链接时使用。离线读本地 SQLite。
---

# kexue

```bash
KX="${CLAUDE_PLUGIN_ROOT}/scripts/kexue.py"
DB="${CLAUDE_PLUGIN_ROOT}/data/kexue.sqlite"
python3 "$KX" search 查询1 查询2 ... [--since 2023-01-01] [--limit 20]
python3 "$KX" show ID
python3 "$KX" sync        # 抓取新文章
```

也可以直接对 `$DB` 写 SQL：
`posts(id, url, title, date, category, tags, readers, excerpt, content_md, cite_text, bibtex)`，
`fts(title, tags, content_md)` 是 trigram 全文索引，`rowid = posts.id`。

## 查询思路

用户的问题往往和文中用词对不上。比如问「LLM 预训练」，文章里很少出现「预训练」，但会写 Muon、MuP、学习率、Batch Size、Scaling Law。所以不要只搜原词：

1. 把问题拆成文中会出现的具体词，中英写法都试，一次传进去：
   `search 优化器 Muon MuP 学习率 "Batch Size" "Scaling Law" MoE 损失函数 --since 2023-01-01`
2. 每个参数是一路查询，结果按各路排名融合，`←` 后面标出命中了哪几路。命中路数多的文章更核心。
3. 输出末尾列出无命中的查询，换同义词再搜。
4. 对候选文章读 `excerpt` 判断是否相关：`sqlite3 "$DB" "select id, excerpt from posts where id in (...)"`。
5. 读正文用 `show ID`。长文可以用 SQL 取 `content_md` 的片段。回答时注明文章 id、标题和链接 `https://kexue.fm/archives/<id>`，引用时给出 `cite_text` 或 `bibtex`。
