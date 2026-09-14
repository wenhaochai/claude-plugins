#!/usr/bin/env python3
"""科学空间 kexue.fm（苏剑林博客）本地库：抓取 + 查询，单文件。

  kexue.py sync                          增量抓取全站文章，写入 data/kexue.sqlite
  kexue.py search [词...] [--tag T] [--category C] [--year Y] [--since D] [--series S]
                  [--sort rank|date|old|readers] [--limit N] [--excerpt [N]]
  kexue.py show ID [--toc | --excerpt | --section 标题 | --max-chars N]
  kexue.py series [名称]                  列出全部系列 / 某系列的篇目
  kexue.py related ID                    同系列、上下篇、互引、站内相似、同标签
  kexue.py stats                         全库统计

查询只依赖标准库；sync 需要 requests + beautifulsoup4 + lxml。
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from datetime import datetime
from html import unescape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "kexue.sqlite"
CACHE = Path(os.environ.get("KEXUE_CACHE", Path.home() / ".cache" / "kexue-fm"))
BASE = "https://kexue.fm"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/128.0 Safari/537.36")
CATEGORIES = ["Everything", "Astronomy", "Mathematics", "Phy-chem", "Big-Data",
              "Biology", "Photograph", "Questions", "Life-Feeling", "Resources"]
DELAY = float(os.environ.get("KEXUE_DELAY", "0.6"))

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts(
  id INTEGER PRIMARY KEY, url TEXT, title TEXT, date TEXT, category TEXT, category_zh TEXT,
  tags TEXT, readers INTEGER, comments INTEGER, series TEXT, series_index INTEGER,
  headings TEXT, excerpt TEXT, content_md TEXT, length INTEGER, cite_text TEXT, bibtex TEXT,
  prev_id INTEGER, next_id INTEGER, similar_ids TEXT, fetched_at TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(title, tags, headings, content_md, content='posts', content_rowid='id', tokenize='trigram');
"""


# ============================================================================ 抓取
class Client:
    """首个请求会拿到 403 + cookie，带 cookie 重试即可。"""

    def __init__(self):
        import requests
        self.s = requests.Session()
        self.s.headers.update({"User-Agent": UA, "Accept-Language": "zh-CN,zh;q=0.9"})
        self.bootstrap()

    def bootstrap(self):
        try:
            self.s.get(BASE + "/", timeout=30)
        except Exception:
            pass

    def get(self, url, retries=4):
        for i in range(retries):
            try:
                r = self.s.get(url, timeout=60)
            except Exception as e:
                print(f"  ! {url}: {e}", file=sys.stderr)
                time.sleep(2 * (i + 1))
                continue
            if r.status_code == 403 and "window.location.href" in r.text[:300]:
                self.bootstrap()
                time.sleep(1)
                continue
            return r
        return None


def enumerate_ids(client, known=frozenset()):
    """按分类翻页收集文章 id；某一页全是已知 id 时该分类停止（文章按时间倒序，新文只会出现在前面）。"""
    from bs4 import BeautifulSoup
    ids = set()
    for slug in CATEGORIES:
        page = 1
        while True:
            r = client.get(f"{BASE}/category/{slug}/{page}/")
            if r is None or r.status_code != 200:
                break
            soup = BeautifulSoup(r.text, "lxml")
            found = {int(m) for m in re.findall(r'href="https://kexue\.fm/archives/(\d+)"', str(soup.select_one("#content") or soup))}
            ids |= found
            print(f"  {slug} 第 {page} 页，累计 {len(ids)}", file=sys.stderr, end="\r" if sys.stderr.isatty() else "\n")
            if not found or found <= known or not soup.select_one("ol.page-navigator li.next a"):
                break
            page += 1
            time.sleep(DELAY)
    print(file=sys.stderr)
    return sorted(ids)


def fetch(client, ids):
    CACHE.mkdir(parents=True, exist_ok=True)
    todo = [i for i in ids if not (CACHE / f"{i}.html").exists()]
    print(f"下载 {len(todo)} 篇（已缓存 {len(ids) - len(todo)}）", file=sys.stderr)
    for n, pid in enumerate(todo, 1):
        r = client.get(f"{BASE}/archives/{pid}")
        if r is None or r.status_code != 200 or 'id="PostContent"' not in r.text:
            print(f"  跳过 {pid}: {getattr(r, 'status_code', None)}", file=sys.stderr)
            continue
        (CACHE / f"{pid}.html").write_text(r.text, encoding="utf-8")
        if n % 25 == 0:
            print(f"  {n}/{len(todo)}", file=sys.stderr)
        time.sleep(DELAY)


# ============================================================================ HTML -> Markdown
def md(node):
    """保留文本原样（LaTeX 不转义）的极简转换。"""
    from bs4 import Comment, NavigableString, Tag
    if isinstance(node, Comment):
        return "\n<!--more-->\n" if node.strip() == "more" else ""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in ("script", "style"):
        return ""
    if name == "br":
        return "\n"
    if name == "hr":
        return "\n\n---\n\n"
    if name == "img":
        src = node.get("src") or node.get("data-src") or ""
        return f"![{node.get('alt', '')}]({BASE + src if src.startswith('/') else src})"
    if name == "pre":
        return f"\n\n```\n{node.get_text().rstrip()}\n```\n\n"
    if name == "code":
        return f"`{node.get_text()}`"
    if name == "table":
        rows = [[" ".join(md(td).split()) for td in tr.find_all(["td", "th"])] for tr in node.find_all("tr")]
        if not rows:
            return ""
        w = max(map(len, rows))
        rows = [r + [""] * (w - len(r)) for r in rows]
        lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return "\n\n" + "\n".join(lines) + "\n\n"
    inner = "".join(md(c) for c in node.children)
    if name == "a":
        href = node.get("href", "")
        href = BASE + href if href.startswith("/") else href
        inner = inner.strip()
        if not inner or inner == "#":
            return ""
        return inner if not href or href.startswith("#") else f"[{inner}]({href})"
    if name in ("strong", "b"):
        return f"**{inner.strip()}**" if inner.strip() else ""
    if name in ("em", "i"):
        return f"*{inner.strip()}*" if inner.strip() else ""
    if name[0] == "h" and name[1:].isdigit():
        return f"\n\n{'#' * int(name[1])} {inner.strip()}\n\n"
    if name == "p":
        return f"\n\n{inner.strip()}\n\n"
    if name == "blockquote":
        return "\n\n" + "\n".join("> " + l for l in inner.strip().splitlines()) + "\n\n"
    if name == "li":
        return f"\n- {inner.strip()}"
    if name in ("ul", "ol"):
        return f"\n{inner}\n\n"
    if name in ("div", "figure", "figcaption", "center", "tr"):
        return f"\n{inner}\n"
    return inner


def clean(s):
    return re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", s)).strip() + "\n"


# ============================================================================ 系列识别
CN = {"零": 0, "〇": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5, "六": 6, "七": 7, "八": 8, "九": 9}
SERIES_RE = [
    re.compile(r"^(?P<s>.+?)[：:]\s*(?P<i>\d{1,3})[、.．]\s*\S"),                    # Transformer升级之路：2、…
    re.compile(r"^(?P<s>.+?)\s*[⋅·]?\s*[（(](?P<i>[一二三四五六七八九十零〇]+|\d{1,3})[）)]"),  # 生成扩散模型漫谈（一）：… / 【搜出来的文本】⋅（一）…
]


def cn_int(s):
    if s.isdigit():
        return int(s)
    if "十" in s:
        a, _, b = s.partition("十")
        return (CN[a] if a else 1) * 10 + (CN[b] if b else 0)
    return CN.get(s)


def detect_series(title):
    for pat in SERIES_RE:
        m = pat.match(title)
        if m and (i := cn_int(m.group("i"))) is not None:
            return m.group("s").strip(" 《【》】⋅·"), i
    return None, None


# ============================================================================ 解析
def parse(pid, html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    head, content = soup.select_one("div.PostHead"), soup.select_one("#PostContent")
    if head is None or content is None:
        return None
    title = head.select_one("h1").get_text(strip=True)
    sub = head.select_one("span.submitted").get_text(" ", strip=True)
    date = (re.search(r"\d{4}-\d{2}-\d{2}", sub) or [None])[0]
    readers = re.search(r"(\d+)位读者", sub)
    cite_text, bibtex = "", ""
    if (htc := soup.select_one("#how_to_cite")) and (ps := htc.select("p.cite_style")):
        cite_text = " ".join(ps[0].get_text(" ", strip=True).split())
        if len(ps) > 1:
            raw = re.sub(r"<br\s*/?>", "\n", ps[1].decode_contents())
            bibtex = "\n".join(l.strip() for l in unescape(re.sub(r"<[^>]+>", "", raw)).splitlines() if l.strip())
    for sel in ("#content_tips", "#how_to_cite", "#pay", ".pay", "script", "style"):
        for t in content.select(sel):
            t.decompose()
    body = clean(md(content))
    excerpt = body.split("<!--more-->")[0].strip() if "<!--more-->" in body else "\n\n".join(body.split("\n\n")[:2])
    body = clean(body.replace("<!--more-->", ""))
    cat, cat_zh, tags = None, None, []
    for a in (soup.select_one("#tools span.cat") or soup.new_tag("span")).select("a[href]"):
        if m := re.search(r"/category/([^/\"]+)", a["href"]):
            cat, cat_zh = m.group(1), a.get_text(strip=True)
        elif "/tag/" in a["href"]:
            tags.append(a.get_text(strip=True))
    comments = soup.select_one("#tools .comment_comments")
    nav = [int(m) for m in re.findall(r"/archives/(\d+)", str(soup.select_one("#entrynavigation") or ""))]
    similar = []
    for m in re.findall(r"/archives/(\d+)", str(soup.select_one("#similar") or "")):
        if int(m) != pid and int(m) not in similar:
            similar.append(int(m))
    headings = [h.get_text(" ", strip=True).rstrip("#").strip() for h in content.select("h2, h3")]
    series, idx = detect_series(title)
    return dict(
        id=pid, url=f"{BASE}/archives/{pid}", title=title, date=date, category=cat, category_zh=cat_zh,
        tags=json.dumps(tags, ensure_ascii=False), readers=int(readers.group(1)) if readers else None,
        comments=int(m.group()) if comments and (m := re.search(r"\d+", comments.get_text())) else 0,
        series=series, series_index=idx, headings=json.dumps(headings, ensure_ascii=False),
        excerpt=re.sub(r"\n{2,}", "\n", excerpt)[:1200], content_md=body,
        length=len(re.findall(r"[一-鿿]|[A-Za-z]+|\d+", body)), cite_text=cite_text, bibtex=bibtex,
        prev_id=nav[0] if nav else None, next_id=nav[-1] if len(nav) > 1 else None,
        similar_ids=json.dumps(similar), fetched_at=datetime.now().isoformat(timespec="seconds"),
    )


def upsert(con, p):
    cols = list(p)
    con.execute(f"INSERT OR REPLACE INTO posts({','.join(cols)}) VALUES ({','.join('?' * len(cols))})", [p[c] for c in cols])


def cmd_sync(a):
    DB.parent.mkdir(exist_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    have = {r[0] for r in con.execute("SELECT id FROM posts")}
    client = Client()
    ids = enumerate_ids(client, frozenset() if a.reparse else frozenset(have))
    fetch(client, ids)
    todo = ids if a.reparse else [i for i in ids if i not in have]
    n = 0
    for pid in todo:
        f = CACHE / f"{pid}.html"
        if not f.exists():
            continue
        if p := parse(pid, f.read_text(encoding="utf-8")):
            upsert(con, p)
            n += 1
    con.execute("UPDATE posts SET series = NULL, series_index = NULL WHERE series IN "
                "(SELECT series FROM posts GROUP BY series HAVING COUNT(*) = 1)")   # 只有一篇的不算系列
    con.execute("INSERT INTO fts(fts) VALUES ('rebuild')")   # 外部内容表：索引不存正文副本
    con.commit()
    con.execute("VACUUM")
    total = con.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    con.close()
    print(f"库内 {total} 篇；本次写入 {n} 篇（新增 {len(set(todo) - have)}）")


# ============================================================================ 查询
def connect():
    if not DB.exists():
        sys.exit(f"缺少 {DB}，先运行 kexue.py sync")
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def line(r):
    s = f"  [{r['series']} #{r['series_index']}]" if r["series"] else ""
    return f"{r['id']:>5}  {r['date']}  {r['title']}{s}"


def show_rows(rows, header=None):
    if header:
        print(header)
    print("\n".join(line(r) for r in rows) if rows else "（无结果）")


def fts_match(terms):
    """trigram 分词要求每个词 ≥3 字符；短词退化为 LIKE。返回 (match 表达式, 短词列表)。"""
    long_ = [t for t in terms if len(t) >= 3]
    return " AND ".join('"' + t.replace('"', '""') + '"' for t in long_), [t for t in terms if len(t) < 3]


def cmd_search(a):
    con = connect()
    match, short = fts_match(a.query)
    where, params = [], []
    for t in short:
        where.append("(p.title LIKE ? OR p.content_md LIKE ?)")
        params += [f"%{t}%", f"%{t}%"]
    for col, val in (("p.tags LIKE ?", f'%"{a.tag}"%' if a.tag else None), ("(p.category = ? OR p.category_zh = ?)", a.category),
                     ("substr(p.date,1,4) = ?", str(a.year) if a.year else None), ("p.date >= ?", a.since),
                     ("p.date <= ?", a.until), ("p.series LIKE ?", f"%{a.series}%" if a.series else None)):
        if val:
            where.append(col)
            params += [val, val] if col.count("?") == 2 else [val]
    order = {"date": "p.date DESC", "old": "p.date ASC", "readers": "p.readers DESC"}.get(a.sort)
    if match:
        sql = "SELECT p.*, bm25(fts, 10, 5, 3, 1) AS rank FROM fts JOIN posts p ON p.id = fts.rowid WHERE fts MATCH ?"
        params = [match] + params
        sql += (" AND " + " AND ".join(where) if where else "") + f" ORDER BY {order or 'rank'} LIMIT ?"
    else:
        sql = "SELECT p.* FROM posts p" + (" WHERE " + " AND ".join(where) if where else "") + f" ORDER BY {order or 'p.date DESC'} LIMIT ?"
    rows = con.execute(sql, params + [a.limit]).fetchall()
    show_rows(rows, f"「{' '.join(a.query) or '全部'}」命中 {len(rows)} 篇（上限 {a.limit}）:")
    if a.excerpt:
        for r in rows:
            print(f"\n--- {r['id']} {r['title']}\n{r['excerpt'][:a.excerpt]}")


def cmd_show(a):
    con = connect()
    r = con.execute("SELECT * FROM posts WHERE id = ?", (a.id,)).fetchone() or sys.exit(f"库中没有 id={a.id}")
    print(f"# {r['title']}\n{r['url']}  |  {r['date']}  |  {r['category_zh']}  |  标签: {', '.join(json.loads(r['tags']))}"
          f"  |  阅读 {r['readers']}  |  评论 {r['comments']}  |  约 {r['length']} 字")
    if r["series"]:
        print(f"系列: {r['series']} 第 {r['series_index']} 篇")
    heads = json.loads(r["headings"])
    if a.toc:
        print("\n目录:\n" + "\n".join(f"  - {h}" for h in heads))
        return
    if a.excerpt:
        print("\n" + r["excerpt"])
        return
    body = r["content_md"]
    if a.section:
        parts = re.split(r"(?m)^(#{1,6} .+)$", body)
        picked = [parts[i] + "\n" + parts[i + 1] for i in range(1, len(parts), 2) if a.section in parts[i]]
        body = "\n".join(picked) if picked else f"（没有包含「{a.section}」的小节；目录: {heads}）"
    if a.max_chars and len(body) > a.max_chars:
        body = body[:a.max_chars] + f"\n\n…（已截断，全文 {len(r['content_md'])} 字符；用 --section 或 --max-chars 0）"
    print("\n" + body)
    print(f"\n---\n引用: {r['cite_text']}\n{r['bibtex']}")


def cmd_series(a):
    con = connect()
    if a.name:
        rows = con.execute("SELECT * FROM posts WHERE series LIKE ? ORDER BY series, series_index, date", (f"%{a.name}%",)).fetchall()
        cur = None
        for r in rows:
            if r["series"] != cur:
                cur = r["series"]
                print(f"\n## {cur}（{sum(r2['series'] == cur for r2 in rows)} 篇）")
            print(f"{r['series_index']:>3}. {r['id']:>5}  {r['date']}  {r['title']}")
            if a.excerpt:
                print("      " + r["excerpt"][:a.excerpt].replace("\n", " "))
        if not rows:
            print("（没有匹配的系列）")
        return
    rows = con.execute("SELECT series, COUNT(*) n, MIN(date) d0, MAX(date) d1 FROM posts WHERE series IS NOT NULL "
                       "GROUP BY series HAVING n >= 2 ORDER BY d1 DESC").fetchall()
    print(f"共 {len(rows)} 个系列:")
    for r in rows:
        print(f"{r['n']:>3} 篇  {r['d0']} ~ {r['d1']}  {r['series']}")


def cmd_related(a):
    con = connect()
    r = con.execute("SELECT * FROM posts WHERE id = ?", (a.id,)).fetchone() or sys.exit(f"库中没有 id={a.id}")
    print(f"# {r['id']} {r['title']}  ({r['date']})")

    def by_ids(ids):
        ids = [i for i in ids if i]
        if not ids:
            return []
        got = {x["id"]: x for x in con.execute(f"SELECT * FROM posts WHERE id IN ({','.join('?' * len(ids))})", ids)}
        return [got[i] for i in ids if i in got]

    if r["series"]:
        print(f"\n## 同系列「{r['series']}」")
        for x in con.execute("SELECT * FROM posts WHERE series = ? ORDER BY series_index, date", (r["series"],)):
            print(f"{x['series_index']:>3}. {x['id']:>5}  {x['date']}  {x['title']}{'  ←当前' if x['id'] == r['id'] else ''}")
    show_rows(by_ids([r["prev_id"], r["next_id"]]), "\n## 上一篇 / 下一篇")
    out = sorted({int(x or y) for x, y in re.findall(r"kexue\.fm/archives/(\d+)|\]\(/archives/(\d+)", r["content_md"])} - {r["id"]})
    show_rows(by_ids(out), "\n## 本文引用的站内文章")
    inbound = [x[0] for x in con.execute("SELECT rowid FROM fts WHERE fts MATCH ? AND rowid != ? ORDER BY rowid",
                                         (f'"archives/{r["id"]}"', r["id"]))]
    show_rows(by_ids(inbound), "\n## 引用了本文的文章")
    show_rows(by_ids(json.loads(r["similar_ids"])), "\n## 站内“相似文章”")
    tags = json.loads(r["tags"])
    if tags:
        scored = defaultdict(int)
        for t in tags:
            for x in con.execute("SELECT id FROM posts WHERE tags LIKE ? AND id != ?", (f'%"{t}"%', r["id"])):
                scored[x[0]] += 1
        top = sorted(scored, key=lambda i: -scored[i])[:a.limit]
        print(f"\n## 同标签（{', '.join(tags)}）")
        for x in by_ids(top):
            print(f"{line(x)}  (共 {scored[x['id']]} 个标签)")
    arx = sorted(set(re.findall(r"arxiv\.org/(?:abs|pdf)/(\d{4}\.\d{4,5})", r["content_md"])))
    if arx:
        print("\n## 文中提到的 arXiv 论文\n" + "\n".join(f"  https://arxiv.org/abs/{p}" for p in arx))


def cmd_stats(a):
    con = connect()
    n, d0, d1 = con.execute("SELECT COUNT(*), MIN(date), MAX(date) FROM posts").fetchone()
    print(f"科学空间本地库: {n} 篇，{d0} ~ {d1}\n\n按分类:")
    for r in con.execute("SELECT category_zh, category, COUNT(*) c FROM posts GROUP BY category ORDER BY c DESC"):
        print(f"{r['c']:>5}  {r['category_zh']} ({r['category']})")
    print("\n按年份:")
    for r in con.execute("SELECT substr(date,1,4) y, COUNT(*) c FROM posts GROUP BY y ORDER BY y"):
        print(f"{r['y']}: {r['c']}")
    ns = con.execute("SELECT COUNT(*) FROM (SELECT series FROM posts WHERE series IS NOT NULL GROUP BY series HAVING COUNT(*) >= 2)").fetchone()[0]
    tagc = defaultdict(int)
    for (t,) in con.execute("SELECT tags FROM posts"):
        for x in json.loads(t):
            tagc[x] += 1
    print(f"\n系列 {ns} 个；标签 {len(tagc)} 个，前 30:")
    print(", ".join(f"{t}({c})" for t, c in sorted(tagc.items(), key=lambda kv: -kv[1])[:30]))
    print("\n阅读数前 15:")
    for r in con.execute("SELECT * FROM posts ORDER BY readers DESC LIMIT 15"):
        print(f"{r['readers']:>8}  {line(r)}")


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("sync"); s.add_argument("--reparse", action="store_true", help="用缓存重新解析全部文章"); s.set_defaults(f=cmd_sync)
    s = sub.add_parser("search"); s.add_argument("query", nargs="*")
    for opt in ("--tag", "--category", "--since", "--until", "--series"):
        s.add_argument(opt)
    s.add_argument("--year", type=int); s.add_argument("--sort", choices=["rank", "date", "old", "readers"], default="rank")
    s.add_argument("--limit", type=int, default=20); s.add_argument("--excerpt", type=int, nargs="?", const=300, default=0)
    s.set_defaults(f=cmd_search)
    s = sub.add_parser("show"); s.add_argument("id", type=int); s.add_argument("--toc", action="store_true")
    s.add_argument("--excerpt", action="store_true"); s.add_argument("--section"); s.add_argument("--max-chars", type=int, default=12000)
    s.set_defaults(f=cmd_show)
    s = sub.add_parser("series"); s.add_argument("name", nargs="?"); s.add_argument("--excerpt", type=int, nargs="?", const=200, default=0)
    s.set_defaults(f=cmd_series)
    s = sub.add_parser("related"); s.add_argument("id", type=int); s.add_argument("--limit", type=int, default=10); s.set_defaults(f=cmd_related)
    s = sub.add_parser("stats"); s.set_defaults(f=cmd_stats)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
