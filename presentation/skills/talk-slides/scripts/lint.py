"""Static checks on Slides deck files before any render.

    python3 lint.py [deck_dir]      # deck_dir holds project/slides/*.html; default: current directory

Errors: the file contract (one section, id equals file name, notes last), the subset limits
(200 elements, 15 nested divs, 24 pinned children per host, SVG under 52 KB and without <text>),
text under 24px, a negative left/top, which the runtime clamps to 0, an empty width-only div,
which the runtime drops with its gap, and notes over 4,000 characters.
Warnings: em dashes, the "X, not Y" pattern, the word campaign, [bracketed] placeholders, raw
line breaks in the notes, which the runtime turns into spaces, notes that are not pairs of one
English line and its Chinese line split by blank lines, and English sentences over 18 words. A verbatim quote or an
interval such as [19%, 39%] may trip a warning.
"""
import html
import os
import re
import sys
from html.parser import HTMLParser

VOID = {'br', 'hr', 'img'}
CJK = re.compile(r'[\u4e00-\u9fff]')
PAINT = ('background', 'border', 'box-shadow')


class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.n, self.in_svg, self.svg_nodes = [], 0, False, 0
        self.issues, self.uid, self.max_div, self.pinned, self.text = [], 0, 0, {}, []
        self.in_aside, self.last_div = False, None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        st = (a.get('style') or '').replace(' ', '')
        self.last_div = None
        if self.in_svg:
            self.svg_nodes += 1
            if tag == 'text':
                self.issues.append('svg <text>: fonts never load in an svg, paint labels as <p> over it')
            self.stack.append(tag)
            return
        self.n += 1
        for decl in (a.get('style') or '').split(';'):
            if ':' not in decl:
                continue
            k, v = (x.strip() for x in decl.split(':', 1))
            if k == 'font-size':
                num = re.sub('[^0-9.]', '', v)
                if num and float(num) < 24:
                    self.issues.append(f'font-size {v} on <{tag}>')
            if k in ('margin', 'z-index') or 'var(' in v or v.endswith('rem') or (v.endswith('em') and k != 'letter-spacing'):
                self.issues.append(f'unsupported css {k}:{v}')
            if k in ('left', 'top') and v.startswith('-'):
                self.issues.append(f'negative {k}:{v} is clamped to 0 by the runtime')
        if 'position:absolute' in st:
            host = next((x[2] for x in reversed(self.stack) if isinstance(x, tuple) and x[0] == 'div' and x[1]), 'section')
            self.pinned[host] = self.pinned.get(host, 0) + 1
        if tag == 'svg':
            self.in_svg = True
        if tag == 'aside':
            self.in_aside = True
        depth = sum(1 for x in self.stack if isinstance(x, tuple) and x[0] == 'div')
        self.max_div = max(self.max_div, depth + (tag == 'div'))
        if tag == 'div' and 'width:' in st and not any(p + ':' in st for p in PAINT) and 'flex:' not in st and 'position:absolute' not in st:
            self.last_div = st
        if tag not in VOID:
            self.uid += 1
            self.stack.append((tag, 'position:relative' in st, self.uid) if tag != 'svg' else 'svg')

    def handle_startendtag(self, tag, attrs):
        if self.in_svg:
            self.svg_nodes += 1
            return
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stack:
            self.stack.pop()

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == 'div' and self.last_div is not None:
            self.issues.append(f'empty unpainted div with a width is dropped with its gap: {self.last_div[:60]}')
        self.last_div = None
        if self.stack:
            self.stack.pop()
        if tag == 'svg':
            self.in_svg = False
        if tag == 'aside':
            self.in_aside = False

    def handle_data(self, data):
        if data.strip():
            self.last_div = None
        if not self.in_svg:
            self.text.append((self.in_aside, data))


def lint(deck_dir):
    sl = os.path.join(deck_dir, 'project', 'slides')
    bad = 0
    for f in sorted(os.listdir(sl)):
        if not f.endswith('.html'):
            continue
        sid, src = f[:-5], open(os.path.join(sl, f)).read()
        p = Parser()
        p.feed(src)
        errs, warns = list(p.issues), []
        if not re.match(rf'<section id="{re.escape(sid)}"', src.strip()):
            errs.append('section id differs from the file name')
        if src.count('<section') != 1:
            errs.append('a slide file holds exactly one <section>')
        if '<aside>' in src and not re.search(r'</aside>\s*</section>\s*$', src):
            errs.append('<aside> must be the last child of the section')
        if p.n > 200:
            errs.append(f'{p.n} elements, the limit is 200')
        if p.max_div > 15:
            errs.append(f'div depth {p.max_div}, the limit is 15')
        errs += [f'{v} pinned children in one host, the limit is 24' for v in p.pinned.values() if v > 24]
        errs += ['svg larger than 52 KB' for m in re.finditer(r'<svg.*?</svg>', src, re.S) if len(m.group(0).encode()) > 52000]
        visible = ' '.join(d for in_aside, d in p.text if not in_aside)
        for pat, name in (('—', 'em dash'), (', not ', '"X, not Y" pattern'), ('campaign', 'the word campaign')):
            if pat in visible:
                warns.append(name)
        notes = ' '.join(d for in_aside, d in p.text if in_aside)
        left = re.findall(r'\[[^\]\n]{1,60}\]', visible + ' ' + notes)
        if left:
            warns.append(f'{len(left)} placeholder(s) left, e.g. {left[0]}')
        m = re.search(r'<aside>(.*?)</aside>', src, re.S)
        if m:
            parts = re.split(r'<br\s*/?>', m.group(1))
            if any('\n' in part.strip() for part in parts):
                warns.append('raw line breaks in the notes: the runtime turns them into spaces, write <br>')
            text = '\n'.join(re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', part))).strip() for part in parts)
            if len(text) > 4000:
                errs.append(f'notes are {len(text)} characters, the limit is 4,000')
            pairs = [b.split('\n') for b in text.strip().split('\n\n')]
            if any(len(b) != 2 or CJK.search(b[0]) or not CJK.search(b[1]) for b in pairs):
                warns.append('notes are not a script: pairs of one English line and its Chinese line, split by blank lines')
            else:
                sents = [s for b in pairs for s in re.split(r'(?<=[.?!])\s+', b[0].strip()) if s]
                long = [s for s in sents if len(s.split()) > 18]
                if long:
                    warns.append(f'{len(long)} English sentence(s) over 18 words, e.g. "{long[0][:40]}..."')
        bad += bool(errs)
        tag = '!!' if errs else ('..' if warns else 'ok')
        print(f'{tag} {sid:16s} elements={p.n:3d} pinned_max={max(p.pinned.values()) if p.pinned else 0:2d} div_depth={p.max_div:2d}',
              ('errors: ' + '; '.join(errs)) if errs else '', ('warnings: ' + '; '.join(warns)) if warns else '')
    print(f'{bad} slide(s) with errors')
    return bad


if __name__ == '__main__':
    sys.exit(1 if lint(sys.argv[1] if len(sys.argv) > 1 else '.') else 0)
