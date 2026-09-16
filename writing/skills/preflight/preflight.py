#!/usr/bin/env python3
"""Mechanical submission preflight for a LaTeX paper directory.

Six checks an LLM is unreliable at, each reported as PASS / WARN / FAIL:

  0.1 compile        latexmk exit status (hard gate)
  0.2 page count     against the venue cap
  0.3 build log      overfull / underfull boxes, undefined citations and references
  0.4 placeholders   TODO / XXX / TBD / [CITATION] / lorem, and leftover \\textcolor{red}
  0.5 correspondence , which / respectively density per file
  0.6 bib hygiene    missing fields, future years, arXiv ids parked in the title field

Usage:
    python3 preflight.py <paper-dir> [--venue iclr] [--main main.tex] [--no-compile]

Exit status is 1 when any check fails, so it works as a gate in a larger script.
"""
import argparse
import os
import re
import subprocess
import sys
from datetime import date

# Body-page caps, excluding references and appendix. Update when a venue changes its call.
VENUE_PAGES = {
    'neurips': 9, 'icml': 8, 'iclr': 9, 'cvpr': 8, 'iccv': 8,
    'eccv': 14, 'acl': 8, 'emnlp': 8, 'colm': 9, 'aaai': 7,
    'arxiv': None, 'tmlr': None,
}
# Uppercase-only for the marker words, so a filename like citations_todo.md does not trip it.
PLACEHOLDER = re.compile(
    r'\b(?:TODO|XXX|FIXME|TBD|PLACEHOLDER)\b|\[CITATION\]|\?\?\?|<<<'
    r'|(?i:Conclusions Here|Lorem ipsum)')
# A macro definition naming a placeholder is the machinery, not a leftover.
MACRO_DEF = re.compile(r'\\(?:re)?newcommand|\\providecommand|\\def\\|\\DeclareRobustCommand')
RED = re.compile(r'\\textcolor\{red\}')
LOG_PATTERNS = [
    ('undefined citation', re.compile(r'Citation [`\'"][^\'"`]*[\'"`] on page \d+ undefined')),
    ('undefined reference', re.compile(r'Reference [`\'"][^\'"`]*[\'"`] on page \d+ undefined')),
    ('overfull hbox', re.compile(r'Overfull \\hbox \((\d+(?:\.\d+)?)pt too wide\)')),
    ('underfull hbox', re.compile(r'Underfull \\hbox')),
]

results = []


def report(level, tag, msg):
    results.append((level, tag, msg))
    print(f'[{level}] {tag:22s} {msg}')


def tex_files(root):
    out = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames
                       if d not in {'.git', '_minted', 'svg-inkscape', 'build', 'out'}]
        out += [os.path.join(dirpath, f) for f in filenames if f.endswith('.tex')]
    return out


def check_compile(root, main, skip):
    if skip:
        report('WARN', '0.1 compile', 'skipped by --no-compile')
        return True
    if not os.path.exists(os.path.join(root, main)):
        report('FAIL', '0.1 compile', f'{main} not found in {root}')
        return False
    p = subprocess.run(['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error', main],
                       cwd=root, capture_output=True, text=True)
    if p.returncode != 0:
        tail = [l for l in p.stdout.splitlines() if l.startswith('!')][:5]
        report('FAIL', '0.1 compile', 'latexmk failed: ' + ('; '.join(tail) or 'see build output'))
        return False
    report('PASS', '0.1 compile', f'{main} builds')
    return True


def check_pages(root, main, venue):
    pdf = os.path.join(root, os.path.splitext(main)[0] + '.pdf')
    if not os.path.exists(pdf):
        report('WARN', '0.2 page count', 'no PDF to measure')
        return
    p = subprocess.run(['pdfinfo', pdf], capture_output=True, text=True)
    m = re.search(r'^Pages:\s*(\d+)', p.stdout, re.M)
    if not m:
        report('WARN', '0.2 page count', 'pdfinfo gave no page count')
        return
    pages = int(m.group(1))
    cap = VENUE_PAGES.get(venue)
    if cap is None:
        report('PASS', '0.2 page count', f'{pages} pages, no cap for {venue}')
    elif pages > cap:
        report('FAIL', '0.2 page count', f'{pages} pages total, cap is {cap} body pages')
    else:
        report('PASS', '0.2 page count', f'{pages} pages total, {venue} cap {cap} body pages')


def check_log(root, main):
    log = os.path.join(root, os.path.splitext(main)[0] + '.log')
    if not os.path.exists(log):
        report('WARN', '0.3 build log', 'no .log file')
        return
    text = open(log, encoding='utf-8', errors='ignore').read()
    counts = {}
    for name, rx in LOG_PATTERNS:
        hits = rx.findall(text)
        if hits:
            counts[name] = hits
    if not counts:
        report('PASS', '0.3 build log', 'clean')
        return
    for name, hits in counts.items():
        if name.startswith('undefined'):
            report('FAIL', '0.3 build log', f'{len(hits)} {name}s')
        elif name == 'overfull hbox':
            bad = [h for h in hits if float(h) > 5.0]
            level = 'FAIL' if bad else 'WARN'
            report(level, '0.3 build log',
                   f'{len(hits)} overfull hboxes, {len(bad)} over 5pt')
        else:
            report('WARN', '0.3 build log', f'{len(hits)} {name}es')


def check_placeholders(files, root):
    ph, red = [], []
    for f in files:
        for i, line in enumerate(open(f, encoding='utf-8', errors='ignore'), 1):
            if line.lstrip().startswith('%') or MACRO_DEF.search(line):
                continue
            if PLACEHOLDER.search(line):
                ph.append(f'{os.path.relpath(f, root)}:{i}')
            if RED.search(line):
                red.append(f'{os.path.relpath(f, root)}:{i}')
    if ph:
        report('FAIL', '0.4 placeholders', f'{len(ph)} left: ' + ', '.join(ph[:5]))
    else:
        report('PASS', '0.4 placeholders', 'none')
    if red:
        report('FAIL', '0.4 red marks', f'{len(red)} leftover \\textcolor{{red}}: '
               + ', '.join(red[:5]))
    else:
        report('PASS', '0.4 red marks', 'none')


def check_correspondence(files, root):
    worst = []
    for f in files:
        t = open(f, encoding='utf-8', errors='ignore').read()
        which = len(re.findall(r', which', t))
        resp = len(re.findall(r'respectively', t))
        if which or resp:
            worst.append((which + resp, which, resp, os.path.relpath(f, root)))
    worst.sort(reverse=True)
    if not worst:
        report('PASS', '0.5 correspondence', 'no ", which" or "respectively"')
        return
    top = '; '.join(f'{p} ({w} which, {r} respectively)' for _, w, r, p in worst[:3])
    total_resp = sum(r for _, _, r, _ in worst)
    level = 'WARN' if total_resp else 'PASS'
    report(level, '0.5 correspondence', f'densest: {top}')


def check_bib(root):
    bibs = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != '.git']
        bibs += [os.path.join(dirpath, f) for f in filenames if f.endswith('.bib')]
    if not bibs:
        report('WARN', '0.6 bib hygiene', 'no .bib file')
        return
    year_now = date.today().year
    missing, future, arxiv_title = [], [], []
    for b in bibs:
        text = open(b, encoding='utf-8', errors='ignore').read()
        for entry in re.finditer(r'@(\w+)\s*\{\s*([^,]+),(.*?)\n\}', text, re.S):
            kind, key, body = entry.group(1).lower(), entry.group(2).strip(), entry.group(3)
            if kind in {'comment', 'string', 'preamble'}:
                continue
            fields = {m.group(1).lower() for m in re.finditer(r'(\w+)\s*=', body)}
            need = {'author', 'title', 'year'}
            if kind in {'inproceedings', 'article', 'incollection'}:
                need |= {'booktitle'} if kind == 'inproceedings' else {'journal'}
            gap = need - fields
            if gap:
                missing.append(f'{key}: no {", ".join(sorted(gap))}')
            ym = re.search(r'year\s*=\s*[{"]?\s*(\d{4})', body)
            if ym and int(ym.group(1)) > year_now:
                future.append(f'{key}: year {ym.group(1)}')
            tm = re.search(r'title\s*=\s*\{(.*?)\}', body, re.S)
            if tm and re.search(r'arxiv|\d{4}\.\d{4,5}', tm.group(1), re.I):
                arxiv_title.append(key)
    for label, items, level in (('missing fields', missing, 'WARN'),
                                ('future year', future, 'FAIL'),
                                ('arXiv id in title', arxiv_title, 'WARN')):
        if items:
            report(level, '0.6 bib hygiene', f'{len(items)} {label}: ' + '; '.join(items[:4]))
    if not (missing or future or arxiv_title):
        report('PASS', '0.6 bib hygiene', f'{len(bibs)} .bib clean')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('paper_dir')
    ap.add_argument('--venue', default='arxiv', choices=sorted(VENUE_PAGES))
    ap.add_argument('--main', default='main.tex')
    ap.add_argument('--no-compile', action='store_true')
    a = ap.parse_args()
    root = os.path.abspath(a.paper_dir)
    print(f'preflight {root}  venue={a.venue}\n')
    ok = check_compile(root, a.main, a.no_compile)
    files = tex_files(root)
    if ok:
        check_pages(root, a.main, a.venue)
        check_log(root, a.main)
    check_placeholders(files, root)
    check_correspondence(files, root)
    check_bib(root)
    fails = [r for r in results if r[0] == 'FAIL']
    warns = [r for r in results if r[0] == 'WARN']
    print(f'\n{len(results) - len(fails) - len(warns)} pass, {len(warns)} warn, {len(fails)} fail')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
