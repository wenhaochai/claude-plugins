# kexue-fm

科学空间 [kexue.fm](https://kexue.fm/)（苏剑林博客）全站离线库 + 一个 Claude Code skill。

```
kexue-fm/
├── scripts/kexue.py     抓取 + 查询，单文件
├── data/kexue.sqlite    全站文章（posts 表 + fts 全文索引）
└── skills/kexue/        SKILL.md
```

## 库里有什么

每篇文章一行：id、URL、标题、日期、分类、标签、阅读数、评论数、系列名与序号（从标题识别）、小节目录、摘要（`<!--more-->` 之前）、全文 Markdown（LaTeX 原样保留）、字数、官方引用格式、BibTeX、上下篇、站内相似文章。覆盖 10 个分类、2009 年至最近一次 sync 的全部文章，不含评论区。

## 用法

```bash
python3 scripts/kexue.py search 位置编码 外推 --excerpt
python3 scripts/kexue.py show 8265 --toc
python3 scripts/kexue.py series 升级之路
python3 scripts/kexue.py related 8265
python3 scripts/kexue.py stats
python3 scripts/kexue.py sync          # 增量更新；需要 requests beautifulsoup4 lxml
```

查询只依赖 Python 标准库（SQLite ≥ 3.34，需 FTS5 trigram）。`sync` 把原始 HTML 缓存在 `~/.cache/kexue-fm/`，请求间隔 0.6 s。

## 版权

文章内容版权归苏剑林所有，站点授权为 CC BY-NC-SA（署名、非商业、相同方式共享）。本库仅作个人检索与学习用途；引用请使用文中给出的官方格式。
