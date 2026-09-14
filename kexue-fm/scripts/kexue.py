#!/usr/bin/env python3
"""科学空间 kexue.fm（苏剑林博客）本地库。

  kexue.py search 查询1 [查询2 ...] [--since YYYY-MM-DD] [--limit N]
      每个参数是一路查询，分别召回后按倒数排名融合；一路里多个词用引号括起，表示同时出现。
  kexue.py show ID
      输出全文 Markdown（LaTeX 原样）和引用格式。
  kexue.py sync
      增量抓取新文章写入 data/kexue.sqlite（需要 requests、beautifulsoup4、lxml）。

也可以直接用 SQL 查 data/kexue.sqlite：
  posts(id, url, title, date, category, tags, readers, excerpt, content_md, cite_text, bibtex)
  fts(title, tags, content_md)   FTS5 trigram 索引，rowid = posts.id
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import time
from collections import defaultdict
from html import unescape
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "data" / "kexue.sqlite"
CACHE = Path(os.environ.get("KEXUE_CACHE", Path.home() / ".cache" / "kexue-fm"))
BASE = "https://kexue.fm"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
CATEGORIES = ["Everything", "Astronomy", "Mathematics", "Phy-chem", "Big-Data",
              "Biology", "Photograph", "Questions", "Life-Feeling", "Resources"]
MORE = "<!--more-->"
SCHEMA = """
CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY, url TEXT, title TEXT, date TEXT, category TEXT, tags TEXT,
  readers INTEGER, excerpt TEXT, content_md TEXT, cite_text TEXT, bibtex TEXT);
CREATE VIRTUAL TABLE IF NOT EXISTS fts USING fts5(title, tags, content_md, content='posts', content_rowid='id', tokenize='trigram');
"""


# ============================================================================ 抓取
def get(session, url):
    """站点首个请求返回 403 并种 cookie，带 cookie 重试即可。"""
    for i in range(4):
        try:
            r = session.get(url, timeout=60)
        except Exception as e:
            print(f"  ! {url}: {e}", file=sys.stderr)
            time.sleep(2 * (i + 1))
            continue
        if r.status_code == 403 and "window.location.href" in r.text[:300]:
            time.sleep(1)
            continue
        return r
    return None


def enumerate_ids(session, known):
    """按分类翻页收集 id；某页全是已知 id 时停止（列表按时间倒序）。"""
    ids = set()
    for slug in CATEGORIES:
        page = 1
        while (r := get(session, f"{BASE}/category/{slug}/{page}/")) is not None and r.status_code == 200:
            found = {int(m) for m in re.findall(r'href="https://kexue\.fm/archives/(\d+)"', r.text.split('id="SideBar"')[0])}
            ids |= found
            if not found or found <= known or 'class="next"' not in r.text:
                break
            page += 1
            time.sleep(0.6)
    return ids


def md(node):
    """HTML -> Markdown，文本原样保留（LaTeX 不转义）。"""
    from bs4 import Comment, NavigableString, Tag
    if isinstance(node, Comment):
        return MORE if node.strip() == "more" else ""
    if isinstance(node, NavigableString):
        return str(node)
    if not isinstance(node, Tag):
        return ""
    name = node.name.lower()
    if name in ("script", "style"):
        return ""
    if name == "br":
        return "\n"
    if name == "img":
        src = node.get("src") or ""
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
        return "\n\n" + "\n".join(["| " + " | ".join(rows[0]) + " |", "|" + "---|" * w] + ["| " + " | ".join(r) + " |" for r in rows[1:]]) + "\n\n"
    inner = "".join(md(c) for c in node.children)
    if name == "a":
        href, inner = node.get("href", ""), inner.strip()
        href = BASE + href if href.startswith("/") else href
        return "" if inner in ("", "#") else inner if not href or href.startswith("#") else f"[{inner}]({href})"
    if name in ("strong", "b") and inner.strip():
        return f"**{inner.strip()}**"
    if name[0] == "h" and name[1:].isdigit():
        return f"\n\n{'#' * int(name[1])} {inner.strip()}\n\n"
    if name == "blockquote":
        return "\n\n" + "\n".join("> " + l for l in inner.strip().splitlines()) + "\n\n"
    if name == "li":
        return f"\n- {inner.strip()}"
    if name in ("p", "div", "ul", "ol", "tr", "figure", "center", "hr"):
        return f"\n\n{inner.strip()}\n\n"
    return inner


def parse(pid, html):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    head, content = soup.select_one("div.PostHead"), soup.select_one("#PostContent")
    if head is None or content is None:
        return None
    sub = head.select_one("span.submitted").get_text(" ", strip=True)
    cite = soup.select("#how_to_cite p.cite_style")
    cite_text = " ".join(cite[0].get_text(" ", strip=True).split()) if cite else ""
    bibtex = ""
    if len(cite) > 1:
        raw = unescape(re.sub(r"<[^>]+>", "", re.sub(r"<br\s*/?>", "\n", cite[1].decode_contents())))
        bibtex = "\n".join(l.strip() for l in raw.splitlines() if l.strip())
    for t in content.select("#content_tips, #how_to_cite, #pay, script, style"):
        t.decompose()
    body = md(content)
    excerpt = body.split(MORE)[0] if MORE in body else body[:600]
    body = re.sub(r"(?m)^>?[ \t]*" + MORE + r"[ \t]*$", "", body).replace(MORE, "")
    body = re.sub(r"\n{3,}", "\n\n", re.sub(r"[ \t]+\n", "\n", body)).strip() + "\n"
    tools = soup.select_one("#tools span.cat")
    links = tools.select("a[href]") if tools else []
    return dict(
        id=pid, url=f"{BASE}/archives/{pid}", title=head.select_one("h1").get_text(strip=True),
        date=(re.search(r"\d{4}-\d{2}-\d{2}", sub) or [None])[0],
        category=next((a.get_text(strip=True) for a in links if "/category/" in a["href"]), None),
        tags=json.dumps([a.get_text(strip=True) for a in links if "/tag/" in a["href"]], ensure_ascii=False),
        readers=int(m.group(1)) if (m := re.search(r"(\d+)位读者", sub)) else None,
        excerpt=re.sub(r"\s*\n\s*", "\n", excerpt).strip()[:1000], content_md=body, cite_text=cite_text, bibtex=bibtex,
    )


def cmd_sync(a):
    import requests
    session = requests.Session()
    session.headers.update({"User-Agent": UA})
    get(session, BASE + "/")
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    have = {r[0] for r in con.execute("SELECT id FROM posts")}
    new = sorted(enumerate_ids(session, have) - have)
    CACHE.mkdir(parents=True, exist_ok=True)
    for pid in new:
        f = CACHE / f"{pid}.html"
        if not f.exists():
            r = get(session, f"{BASE}/archives/{pid}")
            if r is None or 'id="PostContent"' not in r.text:
                print(f"  跳过 {pid}", file=sys.stderr)
                continue
            f.write_text(r.text, encoding="utf-8")
            time.sleep(0.6)
        if p := parse(pid, f.read_text(encoding="utf-8")):
            con.execute(f"INSERT OR REPLACE INTO posts({','.join(p)}) VALUES ({','.join('?' * len(p))})", list(p.values()))
            print(f"  + {pid}  {p['date']}  {p['title']}")
    con.execute("INSERT INTO fts(fts) VALUES ('rebuild')")
    con.commit()
    con.execute("VACUUM")
    print(f"库内 {con.execute('SELECT COUNT(*) FROM posts').fetchone()[0]} 篇，本次新增 {len(new)} 篇")


# ============================================================================ 查询
def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con


def recall(con, query, since, k=60):
    """一路召回：全文 bm25 排名（标题权重最高）+ 标签精确命中。trigram 要求词长 ≥3，更短的词退化为 LIKE。"""
    terms = query.split()
    long_, short = [t for t in terms if len(t) >= 3], [t for t in terms if len(t) < 3]
    cond, params = [], []
    for t in short:
        cond.append("(p.title LIKE ? OR p.content_md LIKE ?)")
        params += [f"%{t}%"] * 2
    if since:
        cond.append("p.date >= ?")
        params.append(since)
    where = "".join(" AND " + c for c in cond)
    if long_:
        match = " AND ".join('"' + t.replace('"', '""') + '"' for t in long_)
        sql = f"SELECT p.id FROM fts JOIN posts p ON p.id = fts.rowid WHERE fts MATCH ?{where} ORDER BY bm25(fts, 10, 5, 1) LIMIT ?"
        text = con.execute(sql, [match] + params + [k]).fetchall()
    else:
        text = con.execute(f"SELECT p.id FROM posts p WHERE 1{where} ORDER BY (p.title LIKE ?) DESC, p.readers DESC LIMIT ?",
                           params + [f"%{short[0]}%", k]).fetchall()
    tagged = con.execute("SELECT p.id FROM posts p WHERE EXISTS (SELECT 1 FROM json_each(p.tags) WHERE lower(value) = lower(?))"
                         + (" AND p.date >= ?" if since else "") + " ORDER BY p.date DESC LIMIT ?",
                         [query] + ([since] if since else []) + [k]).fetchall()
    return [[r[0] for r in text], [r[0] for r in tagged]]


def cmd_search(a):
    con = connect()
    score, hits, empty = defaultdict(float), defaultdict(list), []
    for q in a.query:
        lists = recall(con, q, a.since)
        if not any(lists):
            empty.append(q)
        for lst in lists:
            for rank, pid in enumerate(lst):
                score[pid] += 1 / (60 + rank)          # reciprocal rank fusion
                if q not in hits[pid]:
                    hits[pid].append(q)
    top = sorted(score, key=lambda i: -score[i])[:a.limit]
    rows = {r["id"]: r for r in con.execute(f"SELECT id, date, title FROM posts WHERE id IN ({','.join('?' * len(top))})", top)}
    print(f"「{' | '.join(a.query)}」命中 {len(score)} 篇，前 {len(top)} 篇:")
    for i in top:
        r = rows[i]
        print(f"{r['id']:>5}  {r['date']}  {r['title']}" + (f"  ← {', '.join(hits[i])}" if len(a.query) > 1 else ""))
    if empty:
        print(f"（无命中，换个说法：{' | '.join(empty)}）")


def cmd_show(a):
    r = connect().execute("SELECT * FROM posts WHERE id = ?", (a.id,)).fetchone() or sys.exit(f"库中没有 {a.id}")
    print(f"# {r['title']}\n{r['url']} | {r['date']} | {r['category']} | {', '.join(json.loads(r['tags']))}\n\n"
          f"{r['content_md']}\n---\n{r['cite_text']}\n{r['bibtex']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query", nargs="+")
    s.add_argument("--since")
    s.add_argument("--limit", type=int, default=20)
    s.set_defaults(f=cmd_search)
    s = sub.add_parser("show")
    s.add_argument("id", type=int)
    s.set_defaults(f=cmd_show)
    sub.add_parser("sync").set_defaults(f=cmd_sync)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
