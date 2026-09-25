"""Design tokens and layout builders for talk decks in the claude.ai Slides artifact format.

Every builder returns an HTML string in the Slides subset: inline styles, px units, text at
24px or larger, and pinned children only inside a sized `position:relative` host. The geometry
constants come from a deck that passed the runtime audit, so the defaults fit a 1920x1080 slide
with a footer band: under a one-line title the body has 644px at gap 40 and 1664px of width.
"""
import html as _html
import re

# ---------------------------------------------------------------- tokens
INK, SOFT, MUTED, ACC = '#15141A', '#4A4852', '#6F6C76', '#7A1A1A'
PAPER, CARD, RULE, CHIP = '#F6F3EC', '#FBFAF6', '#D9D3C3', '#E7E2D6'
BLUE, GREY, LGREY, WHITE, PINK = '#2F5D8A', '#8A8791', '#D2CCBD', '#FFFFFF', '#F1DCD6'
NIGHT, NIGHT_TEXT, NIGHT_SOFT, NIGHT_ACC, NIGHT_RULE = '#15141A', '#EDE9DE', '#BDB8AC', '#D0705F', '#3A3842'
SERIF = "'Newsreader', Georgia, serif"
SANS = "'Inter Tight', Arial, sans-serif"
RED_STRIPE = 'repeating-linear-gradient(135deg, #7A1A1A 0px, #7A1A1A 9px, #A5544B 9px, #A5544B 18px)'
FACES = {
    'newsreader': {'family': 'Newsreader',
                   'href': 'https://fonts.googleapis.com/css2?family=Newsreader:ital,wght@0,400;0,500;0,600;1,400;1,500&display=swap'},
    'inter-tight': {'family': 'Inter Tight',
                    'href': 'https://fonts.googleapis.com/css2?family=Inter+Tight:wght@400;500;600&display=swap'},
}


def esc(text):
    return _html.escape(text, quote=False)


# ---------------------------------------------------------------- slide shells


def eyebrow(text, color=ACC):
    return f'<p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:{color}">{text}</p>'


def head(eyebrow_text, title_text):
    return f'''<div style="display:flex; flex-direction:column; gap:12px">
    {eyebrow(eyebrow_text)}
    <h2 style="font-family:{SERIF}; font-size:56px; font-weight:500; line-height:1.1; letter-spacing:-1px; color:{INK}">{title_text}</h2>
  </div>'''


def foot(text):
    return f'<p style="position:absolute; left:128px; bottom:64px; width:1664px; font-size:24px; color:{MUTED}">{text}</p>'


def aside(note):
    """Speaker notes. The runtime reads <aside> like HTML text and turns a raw newline into a space,
    so every line break is written as <br>; the raw newline after it only keeps the file readable."""
    if not note:
        return ''
    body = re.sub(r'<br>(?!<br>)', '<br>\n', esc(note).replace('\n', '<br>'))
    return f'\n  <aside>{body}</aside>'


def slide(sid, eyebrow_text, title_text, body, source=None, gap=40, note=''):
    """A light content slide: eyebrow, noun title, body, optional pinned source line, notes."""
    pad = '128px 128px 160px' if source else '128px'
    f = '\n  ' + foot(source) if source else ''
    return f'''<section id="{sid}" data-transition="fade" style="background:{PAPER}; color:{INK}; font-family:{SANS}; padding:{pad}; display:flex; flex-direction:column; gap:{gap}px">
  {head(eyebrow_text, title_text)}
  {body}{f}{aside(note)}
</section>
'''


def cover(sid, eyebrow_text, title_html, subtitle, left, right, note=''):
    return f'''<section id="{sid}" data-transition="fade" style="background:{NIGHT}; color:{NIGHT_TEXT}; font-family:{SANS}; padding:128px; display:flex; flex-direction:column; justify-content:space-between">
  <p style="font-size:24px; font-weight:600; letter-spacing:3px; text-transform:uppercase; color:{NIGHT_ACC}">{eyebrow_text}</p>
  <div style="display:flex; flex-direction:column; gap:32px">
    <h1 style="font-family:{SERIF}; font-size:120px; font-weight:500; line-height:1.05; letter-spacing:-2px; color:{NIGHT_TEXT}">{title_html}</h1>
    <p style="font-size:36px; line-height:1.3; color:{NIGHT_SOFT}; width:1300px">{subtitle}</p>
  </div>
  <div style="display:flex; justify-content:space-between; border-top:1px solid {NIGHT_RULE}; padding:32px 0 0 0">
    <p style="font-size:28px; color:{NIGHT_TEXT}">{left}</p>
    <p style="font-size:28px; color:{NIGHT_SOFT}">{right}</p>
  </div>{aside(note)}
</section>
'''


def agenda(sid, parts, title, note=''):
    """parts: [(name, one-line description)], one row per part of the talk."""
    rows = ''
    for i, (name, desc) in enumerate(parts):
        border = 'border:1px solid #D9D3C3; border-left:none; border-right:none' if i == 0 else 'border:1px solid #D9D3C3; border-top:none; border-left:none; border-right:none'
        rows += f'''
    <div style="display:flex; gap:48px; align-items:baseline; {border}; padding:44px 0">
      <p style="font-family:{SERIF}; font-size:56px; line-height:1; color:{ACC}; width:80px">{i + 1}</p>
      <p style="font-size:36px; color:{INK}; width:480px">{name}</p>
      <p style="font-size:28px; line-height:1.4; color:{SOFT}; width:1000px">{desc}</p>
    </div>'''
    return f'''<section id="{sid}" data-transition="fade" style="background:{PAPER}; color:{INK}; font-family:{SANS}; padding:128px; display:flex; flex-direction:column; gap:48px">
  {head('Outline', title)}
  <div style="display:flex; flex-direction:column">{rows}
  </div>{aside(note)}
</section>
'''


# ---------------------------------------------------------------- small parts


def pin(x, top, w, text, style):
    """Pinned text. Keep x and top at 0 or more: the runtime clamps negative offsets to 0."""
    assert x >= 0 and top >= 0, 'negative offset is clamped to 0 by the runtime'
    return f'<p style="position:absolute; left:{round(x)}px; top:{round(top)}px; width:{round(w)}px; {style}">{text}</p>'


def ctitle(text):
    """Chart title: a short noun phrase in 28px semibold."""
    return f'<p style="font-size:28px; font-weight:600; color:{INK}">{text}</p>'


def label(text, color=INK):
    """Panel heading: the same style as ctitle, 28px semibold."""
    return f'<p style="font-size:28px; font-weight:600; color:{color}">{text}</p>'


def image(alt, w, h, src='', extra=''):
    """An image frame. With src empty the slide shows a sized placeholder until the file is uploaded."""
    s = f' src="{src}"' if src else ''
    return f'<img{s} alt="{esc(alt)}" style="width:{w}px; height:{h}px; object-fit:contain{"; " + extra if extra else ""}">'


def swatch_legend(items):
    """items: [(color, text)]; square swatches in one row."""
    out = ''.join(f'<div style="display:flex; align-items:center; gap:12px"><div style="width:28px; height:28px; background:{c}"></div>'
                  f'<p style="font-size:24px; color:{INK}; white-space:nowrap">{t}</p></div>' for c, t in items)
    return f'<div style="display:flex; gap:24px">{out}</div>'


# ---------------------------------------------------------------- charts


def composition(groups, px_per_unit, legend_items=None, width=820, gap=18):
    """Weighted composition: one block per group, a bar split into member segments, member names below.

    groups: [(heading, [(units, color)], names_line)]. Units become px_per_unit pixels wide.
    """
    parts = []
    if legend_items:
        parts.append(swatch_legend(legend_items))
    for heading, segs, names in groups:
        bars = ''.join(f'<div style="width:{round(u * px_per_unit)}px; height:28px; background:{c}"></div>' for u, c in segs)
        parts.append(f'''<div style="display:flex; flex-direction:column; gap:8px">
        <p style="font-size:28px; font-weight:600; color:{INK}">{heading}</p>
        <div style="display:flex; gap:4px">{bars}</div>
        <p style="font-size:24px; line-height:1.3; color:{SOFT}">{names}</p>
      </div>''')
    return f'<div style="width:{width}px; display:flex; flex-direction:column; gap:{gap}px">' + ''.join(parts) + '\n    </div>'


def seg_bar(segs, width=788, bracket=None, gap=4):
    """A 100% bar with one labelled column per segment, e.g. the share of weight each grader holds.

    segs: [(share, background, name, detail)]; bracket: (first, last, text) spans segments first..last.
    """
    avail = width - gap * (len(segs) - 1)
    ws = [round(avail * s[0]) for s in segs]
    ws[-1] = avail - sum(ws[:-1])
    cols = ''
    for w, (share, bg, name, detail) in zip(ws, segs):
        cols += f'''
          <div style="width:{w}px; display:flex; flex-direction:column; gap:8px">
            <p style="background:{bg}; color:{WHITE}; font-size:24px; line-height:1.4; padding:6px 12px">{round(share * 100)}%</p>
            <p style="font-size:24px; font-weight:600; color:{INK}; padding:0 16px 0 0">{name}</p>
            <p style="font-size:24px; line-height:1.3; color:{SOFT}; padding:0 16px 0 0">{detail}</p>
          </div>'''
    out = ''
    if bracket:
        a, b, text = bracket
        x = sum(ws[:a]) + gap * a
        bw = sum(ws[a:b + 1]) + gap * (b - a)
        out += f'''<div style="position:relative; width:{width}px; height:46px">
          {pin(x, 0, bw, text, f'font-size:24px; color:{ACC}; text-align:center')}
          <div style="position:absolute; left:{x}px; top:34px; width:{bw}px; height:12px; border:2px solid {ACC}; border-bottom:none"></div>
        </div>
        '''
    return out + f'<div style="display:flex; gap:{gap}px">{cols}\n        </div>'


def board(title, rows, a0, a1, ticks, NW=260, TW=482, RH=40, tick_fmt=str, caption=None):
    """Leaderboard dot plot. rows: [(name, shown value, value, lo or None, hi or None)], best first.

    The leader is red; an interval draws as a light band, a missing one as a hairline.
    Width = NW + 16 + TW + 30. Height = 39 + 6 + len(rows) * RH + 6 + 46, plus 37 for a caption.
    """
    X = lambda v: (v - a0) / (a1 - a0) * TW
    out = ''
    for i, (name, shown, v, lo, hi) in enumerate(rows):
        band = (f'<div style="position:absolute; left:{round(X(lo))}px; top:{RH // 2 - 6}px; width:{round(X(hi) - X(lo))}px; height:12px; border-radius:6px; background:{LGREY}"></div>'
                if lo is not None else f'<div style="position:absolute; left:0px; top:{RH // 2}px; width:{TW}px; height:1px; background:{RULE}"></div>')
        out += f'''
          <div style="display:flex; align-items:center; gap:16px">
            <p style="width:{NW}px; font-size:24px; color:{INK}; text-align:right; white-space:nowrap">{name} <span style="color:{MUTED}">{shown}</span></p>
            <div style="position:relative; width:{TW}px; height:{RH}px">
              {band}
              <div style="position:absolute; left:{round(X(v)) - 11}px; top:{RH // 2 - 11}px; width:22px; height:22px; border-radius:50%; background:{ACC if i == 0 else INK}"></div>
            </div>
          </div>'''
    tk = ''.join(pin(NW + 16 + X(t) - 30, 12, 60, tick_fmt(t), f'font-size:24px; color:{SOFT}; text-align:center') for t in ticks)
    axis = f'''<div style="position:relative; width:{NW + 16 + TW + 30}px; height:46px">
            <div style="position:absolute; left:{NW + 16}px; top:0px; width:{TW}px; height:2px; background:{INK}"></div>{tk}
          </div>'''
    cap = f'\n        <p style="font-size:24px; line-height:1.3; color:{SOFT}">{caption}</p>' if caption else ''
    return f'''<div style="display:flex; flex-direction:column; gap:6px">
        {ctitle(title)}
        <div style="display:flex; flex-direction:column; gap:0px">{out}
        </div>
        {axis}{cap}
      </div>'''


def range_rows(rows, lo_v=0.5, hi_v=1.0, ticks=(0.5, 0.6, 0.7, 0.8, 0.9, 1.0), NW=150, TW=700, RH=80, fmt='{:.2f}'):
    """Method comparison: a big dot for the mean and a bar from worst to best, values printed.

    rows: [(name, mean, best, worst, highlight)].
    """
    R = lambda r: 70 + (r - lo_v) / (hi_v - lo_v) * (TW - 140)
    out = ''
    for name, mean, best, worst, hl in rows:
        col = ACC if hl else INK
        mid = RH // 2 + 14
        out += f'''
        <div style="display:flex; align-items:center; gap:24px">
          <p style="width:{NW}px; font-size:28px; color:{col}; text-align:right">{name}</p>
          <div style="position:relative; width:{TW}px; height:{RH}px">
            <div style="position:absolute; left:{round(R(worst))}px; top:{mid - 4}px; width:{round(R(best) - R(worst))}px; height:8px; border-radius:4px; background:{LGREY}"></div>
            <div style="position:absolute; left:{round(R(mean)) - 15}px; top:{mid - 15}px; width:30px; height:30px; border-radius:50%; background:{col}; border:3px solid {PAPER}"></div>
            {pin(R(mean) - 50, mid - 50, 100, fmt.format(mean), f'font-size:28px; color:{col}; text-align:center')}
            {pin(R(worst) - 66, mid - 17, 58, fmt.format(worst), f'font-size:24px; color:{MUTED}; text-align:right')}
            {pin(R(best) + 8, mid - 17, 58, fmt.format(best), f'font-size:24px; color:{MUTED}')}
          </div>
        </div>'''
    tk = ''.join(pin(R(v) - 40, 0, 80, f'{v:.1f}', f'font-size:24px; color:{SOFT}; text-align:center') for v in ticks)
    axis = (f'<div style="display:flex; gap:24px"><div style="width:{NW}px; height:2px; background:{PAPER}"></div>'
            f'<div style="position:relative; width:{TW}px; height:34px">{tk}</div></div>')
    return f'<div style="display:flex; flex-direction:column; gap:0px; padding:8px 0 0 0">{out}\n      </div>\n      {axis}'


def scatter(points, ax_max=0.8, ps=430, yl=70, ticks=(0, 0.2, 0.4, 0.6, 0.8), notes=(), aria='scatter plot'):
    """Predicted-versus-actual scatter with the identity line. points: [(x, y)] in data units.

    Returns the plot host and the x-tick row. The plot sits 17px inside the host at top and bottom, so the
    top and bottom tick labels need no negative offset and stay clear of the x-tick row.
    notes: [(text, style)] stacked at the top left inside the plot.
    """
    T = 17
    X = lambda v: min(max(v, 0), ax_max) / ax_max * ps
    Y = lambda v: ps - min(max(v, 0), ax_max) / ax_max * ps
    dots = ''.join(f'<circle cx="{X(a):.1f}" cy="{Y(b):.1f}" r="7" fill="{ACC}" stroke="#FFFFFF" stroke-width="1.5"/>' for a, b in points)
    svg = (f'<svg aria-label="{esc(aria)}" style="position:absolute; left:{yl}px; top:{T}px" width="{ps}" height="{ps}" viewBox="0 0 {ps} {ps}">'
           f'<line x1="0" y1="{ps}" x2="{ps}" y2="0" stroke="#828589" stroke-width="2" stroke-dasharray="8 7"/>{dots}'
           f'<line x1="1" y1="0" x2="1" y2="{ps}" stroke="{INK}" stroke-width="2"/>'
           f'<line x1="0" y1="{ps - 1}" x2="{ps}" y2="{ps - 1}" stroke="{INK}" stroke-width="2"/></svg>')
    yt = ''.join(pin(0, T + Y(v) - 17, yl - 14, f'{round(v * 100)}%', f'font-size:24px; color:{SOFT}; text-align:right') for v in ticks)
    nt, top = '', T + 18
    for text, style in notes:
        nt += pin(yl + 28, top, 300, text, style)
        top += 46
    xt = ''.join(pin(yl + X(v) - 40, 0, 80, f'{round(v * 100)}%', f'font-size:24px; color:{SOFT}; text-align:center') for v in ticks)
    host = f'<div style="position:relative; width:{yl + ps + 20}px; height:{ps + 2 * T}px">{svg}{yt}{nt}</div>'
    xrow = f'<div style="position:relative; width:{yl + ps + 40}px; height:34px">{xt}</div>'
    return host, xrow


def histogram(heights, kept, band_labels, axis_labels, width=1664, height=380, gap=12):
    """Distribution with a highlighted band. heights: bar heights in px; kept: indices drawn in the accent.

    band_labels: [(x, w, text, bold)] above the plot; axis_labels: [(x, w, text, align)] below it.
    The two dashed thresholds are drawn at the edges of the kept run of bars.
    """
    n = len(heights)
    bw = (width - gap * (n - 1)) / n
    bars = ''.join(f'<div style="flex:1; height:{h}px; background:{ACC if i in kept else LGREY}"></div>' for i, h in enumerate(heights))
    lo, hi = min(kept), max(kept)
    xs = [round(lo * (bw + gap) - gap / 2), round((hi + 1) * (bw + gap) - gap / 2)]
    dashes = ''.join(f'<div style="position:absolute; left:{x}px; top:0px; width:2px; height:{height}px; border-left:2px dashed #828589"></div>' for x in xs)
    top = ''.join(pin(x, 0, w, t, f'font-size:24px; color:{ACC if b else SOFT}; text-align:center') for x, w, t, b in band_labels)
    bottom = ''.join(pin(x, 0, w, t, f'font-size:24px; color:{SOFT}; text-align:{a}') for x, w, t, a in axis_labels)
    return f'''<div style="display:flex; flex-direction:column; gap:12px">
    <div style="position:relative; width:{width}px; height:34px">{top}</div>
    <div style="position:relative; width:{width}px; height:{height}px; display:flex; align-items:flex-end; gap:{gap}px; border-bottom:2px solid {INK}">{bars}{dashes}</div>
    <div style="position:relative; width:{width}px; height:34px">{bottom}</div>
  </div>'''


# ---------------------------------------------------------------- cards and lists


def card(eyebrow_text, big_html, caption, sub_html, width=368):
    return f'''<div style="width:{width}px; background:{CARD}; border:1px solid {RULE}; border-radius:12px; padding:24px; display:flex; flex-direction:column; gap:8px">
      <p style="font-size:28px; font-weight:600; color:{INK}">{eyebrow_text}</p>
      {big_html}
      <p style="font-size:24px; line-height:1.3; color:{INK}">{caption}</p>
      {sub_html}
    </div>'''


def big(text):
    return f'<p style="font-family:{SERIF}; font-size:56px; line-height:1; color:{INK}">{text}</p>'


def sub(text):
    return f'<p style="font-size:24px; line-height:1.3; color:{MUTED}">{text}</p>'


def pill(text, bg):
    return f'<p style="background:{bg}; color:{WHITE}; font-size:24px; font-weight:600; padding:2px 10px; border-radius:16px">{text}</p>'


def pipeline(cards):
    """Four 368px cards joined by arrows across the full content width."""
    arrow = (f'<div style="width:64px; display:flex; align-items:center; justify-content:center">'
             f'<x-shape kind="arrow-right" style="width:40px; height:22px; background:{GREY}"></x-shape></div>')
    return f'<div style="display:flex">{arrow.join(cards)}</div>'


def check(glyph, bg, text):
    return f'''
          <div style="display:flex; gap:12px; align-items:flex-start">
            <p style="width:36px; height:36px; border-radius:50%; background:{bg}; color:{WHITE}; font-size:24px; font-weight:600; line-height:36px; text-align:center">{glyph}</p>
            <p style="flex:1; font-size:24px; line-height:1.3; color:{INK}">{text}</p>
          </div>'''


def checklist(title, subtitle, must, never, width=960):
    """A real task's checks in two columns: what must become true and what must stay false."""
    m = ''.join(check('✓', BLUE, t) for t in must)
    n = ''.join(check('✕', ACC, t) for t in never)
    return f'''<div style="width:{width}px; display:flex; flex-direction:column; gap:14px">
      <div style="display:flex; flex-direction:column; gap:4px">
        {ctitle(title)}
        <p style="font-size:24px; color:{SOFT}">{subtitle}</p>
      </div>
      <div style="display:flex; gap:48px">
        <div style="flex:1; display:flex; flex-direction:column; gap:10px">
          <p style="font-size:24px; font-weight:600; color:{BLUE}">Must become true</p>{m}
        </div>
        <div style="flex:1; display:flex; flex-direction:column; gap:10px">
          <p style="font-size:24px; font-weight:600; color:{ACC}">Must stay false</p>{n}
        </div>
      </div>
    </div>'''


def hbars(title, rows, max_w=500):
    """Labelled horizontal bars from zero. rows: [(label, value 0..100, color, shown)]."""
    out = ''
    for lab, v, col, shown in rows:
        out += f'''
        <div style="display:flex; flex-direction:column; gap:4px">
          <p style="font-size:24px; color:{SOFT}">{lab}</p>
          <div style="display:flex; align-items:center; gap:12px"><div style="width:{round(max_w * v / 100)}px; height:30px; background:{col}"></div><p style="font-size:28px; color:{SOFT if col == GREY else col}">{shown}</p></div>
        </div>'''
    return f'''<div style="flex:1; display:flex; flex-direction:column; gap:14px">
      {ctitle(title)}{out}
    </div>'''


def quote_card(heading, text):
    font = ''
    return f'''<div style="display:flex; flex-direction:column; gap:10px; background:{CARD}; border:1px solid {RULE}; border-radius:12px; padding:24px 28px">
        {label(heading)}
        <p style="{font}font-size:28px; line-height:1.4; color:{INK}">{text}</p>
      </div>'''


def rubric(heading, rows):
    """rows: [(kind, html)] with kind 'Objective' or 'Guardrail'."""
    out = ''
    for kind, text in rows:
        g = kind.lower().startswith('guard')
        out += f'''
        <div style="display:flex; gap:16px; align-items:center">
          <p style="width:150px; font-size:24px; font-weight:600; color:{ACC if g else INK}; background:{PINK if g else CHIP}; padding:6px 0; border-radius:999px; text-align:center">{kind}</p>
          <p style="font-size:28px; color:{INK}">{text}</p>
        </div>'''
    return f'''<div style="display:flex; flex-direction:column; gap:14px">
        {label(heading)}{out}
      </div>'''


def hl(text):
    """Mark the string a check reacts to inside quoted output."""
    return f'<span style="color:{ACC}">{text}</span>'


def summary(sid, points, closing, note=''):
    """One numbered point per part of the talk and one closing line."""
    items = ''.join(f'''
    <div style="display:flex; gap:32px; align-items:baseline; border-top:1px solid {RULE}; padding:20px 0 0 0">
      <p style="font-family:{SERIF}; font-size:56px; line-height:1; color:{ACC}; width:48px">{i + 1}</p>
      <div style="flex:1; display:flex; flex-direction:column; gap:6px">
        {label(lab)}
        <p style="font-size:28px; line-height:1.35; color:{INK}">{txt}</p>
      </div>
    </div>''' for i, (lab, txt) in enumerate(points))
    body = f'''<div style="display:flex; flex-direction:column; gap:14px; width:1560px">{items}
  </div>
  <div style="flex:1"></div>
  <p style="font-size:28px; line-height:1.4; color:{SOFT}; width:1560px">{closing}</p>'''
    return slide(sid, 'Summary', 'What each part showed', body, None, gap=32, note=note)
