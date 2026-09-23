"""Render every slide in the Slides runtime and measure the laid-out text.

    python3 audit_render.py RUNTIME_DIR [slide_id ...] [--out DIR] [--chrome PATH]

RUNTIME_DIR holds the runtime files read from the deck with the Artifact tool (index.html,
artifact-type/app.js, artifact-type/app.css), a `project` folder or symlink with the deck, and
`_blob/<id>` copies of any uploaded images. The script writes `_files.json`, serves the folder on a
free local port, opens each slide from the runtime's own print sheet in headless Chrome, saves a
screenshot, and reports what the runtime did to the slide:

  shrink    a computed font size that the slide never declares: the column was overfull and the
            runtime scaled its text down
  overflow  text wider or taller than its box
  margin    a text box outside x 128..1792, or below y 920 on a slide with a footer band, 952 without
  overlap   two text boxes that intersect by more than 2px

The shrink check compares against the font sizes written in the slide file, so give every text
element its own font-size, as the deckkit builders do; a size inherited from a parent shows up as
a false shrink finding. Exit status 1 when any slide has a finding. Screenshots and audit.json go
to --out.
"""
import argparse
import functools
import hashlib
import http.server
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time

CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CT = {'.html': 'text/html', '.json': 'application/json', '.js': 'text/javascript', '.css': 'text/css', '.md': 'text/markdown',
      '.png': 'image/png', '.jpg': 'image/jpeg', '.webp': 'image/webp', '.svg': 'image/svg+xml'}
INJECT = r'''<script>
(function(){
  const n = parseInt((location.hash.match(/n=(\d+)/) || [])[1] || '1');
  const css = document.createElement('style');
  css.textContent = `body > *:not(.slides-print-sheet){display:none !important}
    .slides-print-sheet{display:block !important; position:absolute; left:0; top:0}
    .slides-print-slide{display:none !important}
    .slides-print-slide:nth-child(${n}){display:block !important}
    html,body{margin:0 !important; overflow:hidden !important; background:#777 !important}`;
  document.head.appendChild(css);
  let tries = 0;
  function measure(){
    const slide = document.querySelector('.slides-print-slide:nth-child(' + n + ')');
    if ((!slide || (slide.innerText || '').trim().length < 2) && tries++ < 80) return setTimeout(measure, 250);
    document.fonts.ready.then(() => setTimeout(() => {
      const root = slide.firstElementChild, R = root.getBoundingClientRect();
      const out = {n, count: document.querySelectorAll('.slides-print-slide').length, texts: []};
      root.querySelectorAll('[data-text-path]').forEach(el => {
        const r = el.getBoundingClientRect(), cs = getComputedStyle(el);
        out.texts.push({x: Math.round(r.left - R.left), y: Math.round(r.top - R.top), w: Math.round(r.width), h: Math.round(r.height),
          t: (el.innerText || '').trim().replace(/\s+/g, ' ').slice(0, 60), fs: cs.fontSize,
          ox: el.scrollWidth - el.clientWidth, oy: el.scrollHeight - el.clientHeight});
      });
      document.title = 'AUDIT' + JSON.stringify(out);
    }, 800));
  }
  window.addEventListener('load', () => setTimeout(measure, 300));
})();
</script>'''


def write_files_json(rt):
    files = {}
    for root, _, names in os.walk(rt, followlinks=True):
        for n in names:
            full = os.path.join(root, n)
            rel = os.path.relpath(full, rt)
            if rel in ('_files.json', 'index_audit.html'):
                continue
            b = open(full, 'rb').read()
            files[rel] = {'sha256': hashlib.sha256(b).hexdigest(), 'size': len(b),
                          'contentType': CT.get(os.path.splitext(n)[1], 'application/octet-stream')}
    json.dump({'ver': str(int(time.time())), 'files': files, 'narrowed': False}, open(os.path.join(rt, '_files.json'), 'w'))


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def serve(rt):
    s = socket.socket()
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    handler = functools.partial(Quiet, directory=rt)
    httpd = http.server.ThreadingHTTPServer(('127.0.0.1', port), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd, port


def render(chrome, url, png):
    common = [chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--window-size=1920,1080', '--virtual-time-budget=20000']
    subprocess.run(common + [f'--screenshot={png}', url], capture_output=True)
    dom = subprocess.run(common + ['--dump-dom', url], capture_output=True, text=True).stdout
    m = re.search(r'<title>AUDIT(.*?)</title>', dom, re.S)
    if not m:
        return None
    j = m.group(1)
    for a, b in (('&quot;', '"'), ('&lt;', '<'), ('&gt;', '>'), ('&amp;', '&')):
        j = j.replace(a, b)
    return json.loads(j)


def findings(src, res):
    declared = {float(v) for v in re.findall(r'font-size:\s*([0-9.]+)px', src)}
    footer = 'bottom:64px' in src
    limit = 921 if footer else 953
    out = []
    for t in res['texts']:
        fs = float(t['fs'][:-2])
        if all(abs(fs - d) > 0.01 for d in declared):
            out.append(f"shrink {t['fs']}: {t['t'][:40]}")
        if t['ox'] > 1 or t['oy'] > 1:
            out.append(f"overflow {t['ox']}x{t['oy']}px: {t['t'][:40]}")
        is_footer = footer and t['y'] >= 960
        if not is_footer and (t['x'] < 128 or t['x'] + t['w'] > 1793 or t['y'] + t['h'] > limit):
            out.append(f"margin at x={t['x']} y={t['y']} w={t['w']} h={t['h']}: {t['t'][:40]}")
    T = [t for t in res['texts'] if t['w'] > 0 and t['h'] > 0]
    for i in range(len(T)):
        for j in range(i + 1, len(T)):
            a, b = T[i], T[j]
            ix = min(a['x'] + a['w'], b['x'] + b['w']) - max(a['x'], b['x'])
            iy = min(a['y'] + a['h'], b['y'] + b['h']) - max(a['y'], b['y'])
            if ix > 2 and iy > 2:
                out.append(f"overlap: {a['t'][:24]} / {b['t'][:24]}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('runtime')
    ap.add_argument('slides', nargs='*')
    ap.add_argument('--out', default='audit_out')
    ap.add_argument('--chrome', default=os.environ.get('CHROME', CHROME))
    a = ap.parse_args()
    rt = os.path.abspath(a.runtime)
    src = open(os.path.join(rt, 'index.html')).read()
    assert '</head>' in src, 'index.html from the Slides type is missing'
    open(os.path.join(rt, 'index_audit.html'), 'w').write(src.replace('</head>', INJECT + '</head>', 1))
    write_files_json(rt)
    order = json.load(open(os.path.join(rt, 'project', 'deck.json')))['order']
    want = a.slides or order
    os.makedirs(a.out, exist_ok=True)
    httpd, port = serve(rt)
    report, bad = {}, 0
    try:
        for sid in want:
            n = order.index(sid) + 1
            res = render(a.chrome, f'http://127.0.0.1:{port}/index_audit.html#n={n}', os.path.join(a.out, f'{sid}.png'))
            if res is None:
                print(f'!! {sid:16s} no measurement: the runtime did not render the slide')
                bad += 1
                continue
            f = findings(open(os.path.join(rt, 'project', 'slides', f'{sid}.html')).read(), res)
            report[sid] = {'texts': res['texts'], 'findings': f}
            bad += bool(f)
            sizes = sorted({t['fs'] for t in res['texts']}, key=lambda x: float(x[:-2]))
            print(f"{'!!' if f else 'ok'} {sid:16s} texts={len(res['texts']):3d} sizes={' '.join(sizes)}")
            for x in f[:8]:
                print('     ', x)
    finally:
        httpd.shutdown()
    json.dump(report, open(os.path.join(a.out, 'audit.json'), 'w'), ensure_ascii=False, indent=1)
    print(f'{bad} slide(s) with findings; screenshots in {os.path.abspath(a.out)}')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
