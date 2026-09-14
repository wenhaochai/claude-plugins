# kexue-fm

科学空间 [kexue.fm](https://kexue.fm/)（苏剑林博客）全站离线库。

```
scripts/kexue.py     抓取 + 查询
data/kexue.sqlite    posts 表 + fts 全文索引
skills/kexue/        SKILL.md
```

```bash
python3 scripts/kexue.py search Muon MuP 学习率 --since 2023-01-01   # 每个参数一路查询，按倒数排名融合
python3 scripts/kexue.py show 8265                                  # 全文 + 引用格式
python3 scripts/kexue.py sync                                       # 增量抓取，需要 requests beautifulsoup4 lxml
```

表结构：`posts(id, url, title, date, category, tags, readers, excerpt, content_md, cite_text, bibtex)`；`fts(title, tags, content_md)` 为 FTS5 trigram 索引，`rowid = posts.id`。查询只依赖 Python 标准库。

文章版权归苏剑林所有，站点授权为 CC BY-NC-SA。本库仅供个人检索与学习，引用请使用文中的官方格式。
